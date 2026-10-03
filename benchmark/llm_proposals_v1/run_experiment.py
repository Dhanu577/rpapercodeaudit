from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.analyze_natural_v3_1 import is_reference_like
from rpapercodeaudit.claim_extraction import build_prompt, normalize_whitespace, validate_claims
from rpapercodeaudit.code_location import prepare_repository, validate_location
from rpapercodeaudit.heuristics import extract_heuristic_items, split_sections
from rpapercodeaudit.llm import LLMClient, LLMConfig

PAPER_PATH = ROOT / "examples" / "deseq2" / "DESeq.txt"
REPO_PATH = ROOT / "examples" / "deseq2" / "repo"
PINNED_COMMIT = "76c5f8523716804dbe0a9500b4b7e216c6af225c"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODEL = "gemini-3.8-flash"
RESOLVED_VERSION = "gemini-3.8-flash"
OUT = Path(__file__).resolve().parent
RETRYABLE = {429, 503}
RETRY_DELAYS = (10, 30, 90)
INTER_CALL_DELAY = 1.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: Any, *, secret: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    path.write_text(scrub(serialized, secret), encoding="utf-8")


def append_jsonl(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def scrub(text: str, key: str) -> str:
    return text.replace(key, "[REDACTED]") if key else text


def parse_response(raw: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


class ReplayResponse:
    def __init__(self, raw: bytes, status: int, headers: Any):
        self._buffer = io.BytesIO(raw)
        self.status = status
        self.headers = headers

    def read(self, *args: Any) -> bytes:
        return self._buffer.read(*args)

    def __enter__(self) -> "ReplayResponse":
        return self

    def __exit__(self, *_args: Any) -> bool:
        return False


class CapturingClient:
    """Use the unchanged LLMClient while retaining scrubbed wire responses and retry records."""

    def __init__(self, run_name: str, run_dir: Path, key: str):
        self.run_name = run_name
        self.run_dir = run_dir
        self.key = key
        self.config = LLMConfig.from_env()
        self.calls: list[dict[str, Any]] = []
        self.retry_log = run_dir / "retry_log.jsonl"
        self.last_failure: dict[str, Any] | None = None
        self.logical_call_count = 0
        self.chunk_index = 0

    def _one_attempt(self, prompt: str, purpose: str, attempt: int) -> tuple[Any, dict[str, Any], Exception | None]:
        capture: dict[str, Any] = {}
        real_urlopen = urllib.request.urlopen

        def wrapped_urlopen(request: Any, *args: Any, **kwargs: Any) -> Any:
            capture["url"] = request.full_url if isinstance(request, urllib.request.Request) else str(request)
            capture["method"] = request.get_method() if isinstance(request, urllib.request.Request) else None
            try:
                response = real_urlopen(request, *args, **kwargs)
            except urllib.error.HTTPError as exc:
                raw = exc.read()
                capture.update({"status": exc.code, "headers": dict(exc.headers.items()) if exc.headers else {}, "raw": raw})
                exc.fp = io.BytesIO(raw)
                raise
            raw = response.read()
            capture.update({"status": response.status, "headers": dict(response.headers.items()), "raw": raw})
            return ReplayResponse(raw, response.status, response.headers)

        urllib.request.urlopen = wrapped_urlopen
        result: Any = None
        error: Exception | None = None
        try:
            client = LLMClient(
                self.config,
                cache_dir=f"/tmp/llm-proposals-v1-{self.run_name}-chunk{self.chunk_index:02d}-attempt{attempt}-cache",
                log_path=f"/tmp/llm-proposals-v1-{self.run_name}-chunk{self.chunk_index:02d}-attempt{attempt}.jsonl",
                timeout=120,
            )
            result = client.complete_json(prompt, purpose=purpose)
        except Exception as exc:  # captured and classified by HTTP status below
            error = exc
        finally:
            urllib.request.urlopen = real_urlopen

        raw = capture.get("raw", b"")
        response_body = parse_response(raw)
        timestamp = utc_now()
        raw_path = self.run_dir / "raw_responses" / f"chunk{self.chunk_index:02d}_attempt{attempt:02d}.txt"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(scrub(raw.decode("utf-8", errors="replace"), self.key), encoding="utf-8")
        error_text = scrub(str(error), self.key) if error is not None else None
        call = {
            "run": self.run_name,
            "chunk_index": self.chunk_index,
            "attempt": attempt,
            "timestamp_utc": timestamp,
            "method": capture.get("method", "POST"),
            "url": capture.get("url", BASE_URL),
            "requested_model": self.config.model,
            "response_model": response_body.get("model") if response_body else None,
            "http_status": capture.get("status"),
            "exception": error_text,
            "raw_response_empty": not bool(raw),
            "raw_response_file": str(raw_path.relative_to(OUT)),
        }
        append_jsonl(self.run_dir / "calls.jsonl", call)
        self.calls.append(call)
        return result, call, error

    def complete_json(self, prompt: str, *, purpose: str) -> Any:
        self.logical_call_count += 1
        if self.logical_call_count > 1:
            time.sleep(INTER_CALL_DELAY)
        self.last_failure = None
        for attempt in range(1, len(RETRY_DELAYS) + 2):
            if attempt > 1:
                delay = RETRY_DELAYS[attempt - 2]
                prior = self.calls[-1] if self.calls else {}
                retry = {
                    "timestamp_utc": utc_now(),
                    "run": self.run_name,
                    "chunk_index": self.chunk_index,
                    "attempt": attempt,
                    "previous_status": prior.get("http_status"),
                    "delay_seconds": delay,
                    "model": self.config.model,
                }
                append_jsonl(self.retry_log, retry)
                print(f"retry: run={self.run_name} chunk={self.chunk_index} attempt={attempt} status={prior.get('http_status')} delay={delay}s", flush=True)
                time.sleep(delay)
            result, call, error = self._one_attempt(prompt, purpose, attempt)
            status = call.get("http_status")
            if error is None:
                return result
            if status in RETRYABLE and attempt <= len(RETRY_DELAYS):
                continue
            self.last_failure = {"call": call, "status": status, "error": call.get("exception")}
            raise RuntimeError(call.get("exception") or "LLM call failed without a response") from error
        self.last_failure = {"call": self.calls[-1] if self.calls else {}, "status": None, "error": "retry loop exhausted"}
        raise RuntimeError("retry loop exhausted")


def run_full_extraction(run_name: str, paper: str, chunks: list[str], key: str) -> dict[str, Any]:
    run_dir = OUT / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    run_started = utc_now()
    for path in (run_dir / "calls.jsonl", run_dir / "retry_log.jsonl"):
        if path.exists():
            path.unlink()
    os.environ.update({
        "LLM_PROVIDER": "openai-compatible",
        "LLM_BASE_URL": BASE_URL,
        "LLM_MODEL": MODEL,
        "LLM_API_KEY": key,
    })
    client = CapturingClient(run_name, run_dir, key)
    all_proposals: list[Any] = []
    malformed: list[dict[str, Any]] = []
    transport_failures: list[dict[str, Any]] = []
    chunk_records: list[dict[str, Any]] = []

    for chunk_index, part in enumerate(chunks, 1):
        client.chunk_index = chunk_index
        prompt = build_prompt(part)
        try:
            response = client.complete_json(prompt, purpose="claim-extraction")
        except Exception as exc:
            failure = client.last_failure or {}
            call = failure.get("call", {})
            if call.get("http_status") == 200 or call.get("http_status") is None:
                malformed.append({
                    "chunk_index": chunk_index,
                    "error": scrub(str(exc), key),
                    "raw_response_file": call.get("raw_response_file"),
                    "http_status": call.get("http_status"),
                })
            else:
                transport_failures.append({
                    "chunk_index": chunk_index,
                    "error": scrub(str(exc), key),
                    "http_status": call.get("http_status"),
                    "raw_response_file": call.get("raw_response_file"),
                })
            chunk_records.append({"chunk_index": chunk_index, "char_count": len(part), "proposal_count": 0, "status": "failed"})
            continue

        claims = response.get("claims") if isinstance(response, dict) else None
        if not isinstance(claims, list):
            call = client.calls[-1] if client.calls else {}
            malformed.append({
                "chunk_index": chunk_index,
                "error": "LLM response must contain a claims list",
                "raw_response_file": call.get("raw_response_file"),
                "http_status": call.get("http_status"),
            })
            chunk_records.append({"chunk_index": chunk_index, "char_count": len(part), "proposal_count": 0, "status": "malformed"})
            continue

        # Preserve model output entries exactly; the validator receives each original item below.
        all_proposals.extend(claims)
        chunk_records.append({"chunk_index": chunk_index, "char_count": len(part), "proposal_count": len(claims), "status": "parsed"})

    manifest = {
        "run": run_name,
        "started_at_utc": run_started,
        "finished_at_utc": utc_now(),
        "requested_model": MODEL,
        "resolved_version_from_step0_response_model": RESOLVED_VERSION,
        "base_url": BASE_URL,
        "temperature": 0,
        "auth_scheme": "Bearer; key read from GEMINI_API_KEY and never serialized",
        "purpose": "claim-extraction",
        "paper_path": str(PAPER_PATH.relative_to(ROOT)),
        "paper_sha256": hashlib.sha256(paper.encode("utf-8")).hexdigest(),
        "repo_path": str(REPO_PATH.relative_to(ROOT)),
        "commit_hash": PINNED_COMMIT,
        "chunk_count": len(chunks),
        "chunks": [{"chunk_index": i, "char_count": len(part), "sha256": hashlib.sha256(part.encode("utf-8")).hexdigest()} for i, part in enumerate(chunks, 1)],
        "chunk_results": chunk_records,
        "proposal_count": len(all_proposals),
        "malformed_responses": malformed,
        "transport_failures": transport_failures,
        "calls": client.calls,
        "retry_log": str((run_dir / "retry_log.jsonl").relative_to(OUT)),
    }
    write_json(run_dir / "proposals_unmodified.json", all_proposals, secret=key)
    write_json(run_dir / "malformed_responses.json", malformed, secret=key)
    write_json(run_dir / "transport_failures.json", transport_failures, secret=key)
    write_json(run_dir / "manifest.json", manifest, secret=key)
    return {"run_dir": run_dir, "proposals": all_proposals, "manifest": manifest, "malformed": malformed, "transport_failures": transport_failures}


def prepare_repo() -> dict[str, Any]:
    try:
        repo, resolved = prepare_repository(REPO_PATH, PINNED_COMMIT)
        return {"ok": True, "repo_path": str(repo), "requested_commit": PINNED_COMMIT, "resolved_commit": resolved, "error": None}
    except (OSError, RuntimeError, ValueError) as exc:
        return {"ok": False, "repo_path": str(REPO_PATH), "requested_commit": PINNED_COMMIT, "resolved_commit": None, "error": str(exc)}


def validate_proposals(proposals: list[Any], paper: str, repo_state: dict[str, Any], label: str, malformed: list[dict[str, Any]] | None = None, transport_failures: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    stage_counts = Counter()
    accepted_rows: list[dict[str, Any]] = []
    for index, proposal in enumerate(proposals, 1):
        sentence_result = validate_claims(paper, [proposal])
        if sentence_result.rejected:
            rejected = sentence_result.rejected[0]
            row = {"proposal_index": index, "proposal": proposal, "first_failing_stage": "sentence", "raw_validator_error": rejected.reason}
            rows.append(row); stage_counts["sentence"] += 1
            continue
        if not repo_state["ok"]:
            row = {"proposal_index": index, "proposal": proposal, "first_failing_stage": "commit", "raw_validator_error": repo_state["error"]}
            rows.append(row); stage_counts["commit"] += 1
            continue
        location, error = validate_location(REPO_PATH, proposal)
        if location is None:
            row = {"proposal_index": index, "proposal": proposal, "first_failing_stage": "location", "raw_validator_error": error}
            rows.append(row); stage_counts["location"] += 1
        else:
            accepted_rows.append({"proposal_index": index, "proposal": proposal, "location": location.to_output()})

    malformed = malformed or []
    transport_failures = transport_failures or []
    proposal_failures = len(rows)
    failure_units = proposal_failures + len(malformed) + len(transport_failures)
    total_units = len(proposals) + len(malformed) + len(transport_failures)
    rejection_rate = failure_units / total_units if total_units else 0.0
    ci = wilson(failure_units, total_units)
    short_count = 0
    reference_count = 0
    both_count = 0
    for entry in accepted_rows:
        item = entry["proposal"]
        sentence = item.get("verbatim_sentence", "") if isinstance(item, dict) else str(item)
        short = len(normalize_whitespace(str(sentence)).split()) < 5
        reference = is_reference_like(str(sentence))
        short_count += short
        reference_count += reference
        both_count += short and reference
    return {
        "label": label,
        "proposal_count": len(proposals),
        "accepted": len(accepted_rows),
        "rejected_proposals": proposal_failures,
        "malformed_response_failures": len(malformed),
        "transport_failure_units": len(transport_failures),
        "total_units_including_malformed_and_transport_failures": total_units,
        "total_rejected_including_malformed_and_transport_failures": failure_units,
        "first_failing_stage_counts": {key: stage_counts.get(key, 0) for key in ("sentence", "commit", "location")},
        "rejection_rate": rejection_rate,
        "wilson_95_ci_clipped_0_1": ci,
        "accepted_proposal_flags": {"short_sentence_lt_5_tokens": short_count, "reference_like": reference_count, "both": both_count},
        "repo_preparation": repo_state,
        "rejections": rows,
        "malformed_failures": malformed,
        "transport_failures": transport_failures,
        "accepted_proposals": accepted_rows,
    }


def wilson(failures: int, total: int, z: float = 1.959963984540054) -> list[float]:
    if total <= 0:
        return [0.0, 0.0]
    p = failures / total
    z2 = z * z
    denominator = 1 + z2 / total
    center = (p + z2 / (2 * total)) / denominator
    half = z * ((p * (1 - p) / total + z2 / (4 * total * total)) ** 0.5) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def exact_multiset_comparison(first: list[Any], second: list[Any]) -> dict[str, Any]:
    def key(item: Any) -> str:
        return normalize_whitespace(str(item.get("verbatim_sentence", ""))) if isinstance(item, dict) else json.dumps(item, ensure_ascii=False, sort_keys=True)
    c1, c2 = Counter(key(item) for item in first), Counter(key(item) for item in second)
    common = sum((c1 & c2).values())
    exact_objects_1 = Counter(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in first)
    exact_objects_2 = Counter(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in second)
    exact_objects_common = sum((exact_objects_1 & exact_objects_2).values())
    return {
        "run1_proposals": len(first),
        "run2_proposals": len(second),
        "run1_only_by_normalized_sentence_multiset": sum((c1 - c2).values()),
        "run2_only_by_normalized_sentence_multiset": sum((c2 - c1).values()),
        "common_by_normalized_sentence_multiset": common,
        "exact_object_matches_including_ids_and_fields": exact_objects_common,
        "normalized_sentence_multiset_jaccard": common / (len(first) + len(second) - common) if len(first) + len(second) - common else 1.0,
    }


def write_rejections_markdown(path: Path, datasets: list[dict[str, Any]], secret: str = "") -> None:
    chunks = ["# Rejected proposals and validator errors", "", "Model text and validator errors below are recorded without correcting or reclassifying proposal content.", ""]
    for dataset in datasets:
        summary = dataset["summary"]
        chunks.extend([f"## {summary['label']}", ""])
        rows = summary["rejections"]
        if not rows:
            chunks.extend(["No proposal-level rejections.", ""])
        for row in rows:
            item = row["proposal"]
            text = item.get("verbatim_sentence") if isinstance(item, dict) else str(item)
            chunks.extend([
                f"### Proposal {row['proposal_index']} — first failure: {row['first_failing_stage']}",
                "",
                "**Model/deterministic text:**",
                "",
                f"> {scrub(str(text).replace(chr(10), ' '), secret)}",
                "",
                "**Raw validator error:**",
                "",
                f"`{scrub(str(row['raw_validator_error']), secret)}`",
                "",
                "**Unmodified proposal object:**",
                "",
                "```json",
                scrub(json.dumps(item, ensure_ascii=False, indent=2), secret),
                "```",
                "",
            ])
        for failure in summary["malformed_failures"]:
            chunks.extend(["### Malformed/unparseable response failure", "", f"Chunk: {failure.get('chunk_index')}; HTTP status: {failure.get('http_status')}; error: `{failure.get('error')}`; raw: `{failure.get('raw_response_file')}`", ""])
        for failure in summary["transport_failures"]:
            chunks.extend(["### API request failure after retries", "", f"Chunk: {failure.get('chunk_index')}; HTTP status: {failure.get('http_status')}; error: `{failure.get('error')}`; raw: `{failure.get('raw_response_file')}`", ""])
    path.write_text("\n".join(chunks), encoding="utf-8")


def main() -> None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set; no request made")
    paper = PAPER_PATH.read_text(encoding="utf-8")
    chunks = split_sections(paper)
    repo_state = prepare_repo()
    write_json(OUT / "repo_commit.json", repo_state)

    run1 = run_full_extraction("run1", paper, chunks, key)
    time.sleep(INTER_CALL_DELAY)
    run2 = run_full_extraction("run2", paper, chunks, key)

    run1_validation = validate_proposals(run1["proposals"], paper, repo_state, "LLM run 1", run1["malformed"], run1["transport_failures"])
    run2_validation = validate_proposals(run2["proposals"], paper, repo_state, "LLM run 2", run2["malformed"], run2["transport_failures"])
    write_json(OUT / "run1" / "validation.json", run1_validation, secret=key)
    write_json(OUT / "run2" / "validation.json", run2_validation, secret=key)

    deterministic_proposals = extract_heuristic_items(paper)
    deterministic_validation = validate_proposals(deterministic_proposals, paper, repo_state, "Deterministic")
    write_json(OUT / "deterministic_proposals_unmodified.json", deterministic_proposals, secret=key)
    write_json(OUT / "deterministic_validation.json", deterministic_validation, secret=key)

    comparison = {
        "run1_vs_run2": exact_multiset_comparison(run1["proposals"], run2["proposals"]),
        "validation_count_differences": {
            key: run2_validation[key] - run1_validation[key]
            for key in ("proposal_count", "accepted", "rejected_proposals", "malformed_response_failures", "transport_failure_units", "total_rejected_including_malformed_and_transport_failures")
        },
        "by_first_failure_stage_run1": run1_validation["first_failing_stage_counts"],
        "by_first_failure_stage_run2": run2_validation["first_failing_stage_counts"],
    }
    write_json(OUT / "run_comparison.json", comparison)
    write_rejections_markdown(OUT / "rejected_proposals.md", [
        {"summary": run1_validation}, {"summary": run2_validation}, {"summary": deterministic_validation}
    ], secret=key)

    summary = {
        "generated_at_utc": utc_now(),
        "requested_model": MODEL,
        "resolved_model_version": RESOLVED_VERSION,
        "base_url": BASE_URL,
        "temperature": 0,
        "paper_path": str(PAPER_PATH.relative_to(ROOT)),
        "paper_sha256": hashlib.sha256(paper.encode("utf-8")).hexdigest(),
        "repo_path": str(REPO_PATH.relative_to(ROOT)),
        "commit_hash": PINNED_COMMIT,
        "chunk_count": len(chunks),
        "llm_run1": {k: v for k, v in run1_validation.items() if k not in {"rejections", "malformed_failures", "transport_failures", "accepted_proposals"}},
        "llm_run2": {k: v for k, v in run2_validation.items() if k not in {"rejections", "malformed_failures", "transport_failures", "accepted_proposals"}},
        "deterministic": {k: v for k, v in deterministic_validation.items() if k not in {"rejections", "malformed_failures", "transport_failures", "accepted_proposals"}},
        "repeat_comparison": comparison,
    }
    write_json(OUT / "summary.json", summary)

    report = [
        "# Gemini LLM-assisted proposal experiment",
        "",
        f"- Recorded at (UTC): {summary['generated_at_utc']}",
        f"- Requested model: `{MODEL}`; Step 0 response model/version: `{RESOLVED_VERSION}`",
        f"- Base URL: `{BASE_URL}`; temperature: `0`; key was supplied via Bearer auth and not saved.",
        f"- Paper: `{PAPER_PATH.relative_to(ROOT)}` (SHA-256 `{summary['paper_sha256']}`)",
        f"- Repository: `{REPO_PATH.relative_to(ROOT)}` at `{PINNED_COMMIT}`",
        f"- Chunks per full run: {len(chunks)}; inter-call delay: {INTER_CALL_DELAY}s; retry statuses 429/503 with waits 10/30/90s, up to 3 retries.",
        "",
        "## Results",
        "",
        "| Mode | Proposals | Accepted (all stages) | Rejected proposal items | Malformed response failures | API failure units | First fail: sentence | commit | location | Rejection rate (95% Wilson CI) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in (run1_validation, run2_validation, deterministic_validation):
        c = result["first_failing_stage_counts"]
        lo, hi = result["wilson_95_ci_clipped_0_1"]
        report.append(
            f"| {result['label']} | {result['proposal_count']} | {result['accepted']} | {result['rejected_proposals']} | {result['malformed_response_failures']} | {result['transport_failure_units']} | {c['sentence']} | {c['commit']} | {c['location']} | {result['rejection_rate']:.3f} [{lo:.3f}, {hi:.3f}] |"
        )
    report.extend([
        "",
        "Malformed responses and terminal request failures are counted as additional failure units in the rejection-rate denominator; first-failure stage counts cover parsed proposal items.",
        "",
        "## Report-only flags on fully accepted proposals",
        "",
        "| Mode | Accepted proposals | Short (<5 whitespace tokens) | Reference-like | Both |",
        "|---|---:|---:|---:|---:|",
    ])
    for result in (run1_validation, run2_validation, deterministic_validation):
        flags = result["accepted_proposal_flags"]
        report.append(f"| {result['label']} | {result['accepted']} | {flags['short_sentence_lt_5_tokens']} | {flags['reference_like']} | {flags['both']} |")
    report.extend([
        "",
        "## Repeat-run differences",
        "",
        "```json",
        json.dumps(comparison, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Rejections",
        "",
        "Every proposal-level rejection, with original text and the raw validator error, is listed in [rejected_proposals.md](rejected_proposals.md). Raw model responses are under each run's `raw_responses/` directory; unmodified proposal arrays are in `run1/proposals_unmodified.json` and `run2/proposals_unmodified.json`.",
        "",
    ])
    (OUT / "REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"run1": summary["llm_run1"], "run2": summary["llm_run2"], "deterministic": summary["deterministic"], "repeat_comparison": comparison}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
