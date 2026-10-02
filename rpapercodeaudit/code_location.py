"""Repository indexing and deterministic paper-claim code location.

Search is intentionally conservative: keyword hits create candidates, and every
candidate excerpt is re-read from disk before it is returned.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .claim_extraction import ExtractedClaim

INDEX_DIRS = ("R", "src", "man", "vignettes", "tests")
TEXT_SUFFIXES = {".r", ".R", ".cpp", ".cc", ".c", ".h", ".hpp", ".rd", ".md", ".rmd", ".tex", ".txt"}
STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "are", "was", "were", "below", "above",
    "into", "using", "used", "use", "method", "methods", "between", "than", "then", "their", "there",
    "what", "look", "find", "whether", "implementation", "paper", "claim", "gene", "genes",
}


@dataclass(frozen=True, slots=True)
class RFunction:
    name: str
    file: str
    line: int
    defaults: dict[str, str]


@dataclass(frozen=True, slots=True)
class IndexedFile:
    path: str
    lines: int


@dataclass(slots=True)
class CodeIndex:
    repo_path: Path
    commit_hash: str
    files: list[IndexedFile]
    r_functions: list[RFunction]


@dataclass(frozen=True, slots=True)
class CodeLocation:
    claim_id: str
    package: str
    commit_hash: str
    code_file: str
    start_line: int
    end_line: int
    code_lines: str
    code_excerpt: str
    keywords: list[str]
    status: str = "candidate"

    def to_output(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "package": self.package,
            "commit_hash": self.commit_hash,
            "code_file": self.code_file,
            "code_lines": f"{self.start_line}-{self.end_line}",
            "code_excerpt": self.code_excerpt,
            "keywords": self.keywords,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class InvalidLocation:
    item: dict[str, Any]
    reason: str


@dataclass(frozen=True, slots=True)
class LocationResult:
    locations: list[CodeLocation]
    not_found: list[dict[str, Any]]
    invalid: list[InvalidLocation]


def _git(repo: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Git is required to verify the repository commit.") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout).strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}") from exc
    return completed.stdout.strip()


def prepare_repository(repo_path: str | Path, commit_hash: str, *, checkout: bool = True) -> tuple[Path, str]:
    """Checkout or verify a commit and return its resolved full hash.

    A non-matching HEAD is detached at the requested commit by default. No
    force/reset operation is used, so local uncommitted work is not discarded.
    """
    repo = Path(repo_path).expanduser().resolve()
    if not (repo / ".git").exists():
        raise ValueError(f"Not a git repository: {repo}")
    requested = _git(repo, "rev-parse", "--verify", f"{commit_hash}^{{commit}}")
    head = _git(repo, "rev-parse", "HEAD")
    if head != requested:
        if not checkout:
            raise ValueError(f"HEAD {head} does not match requested commit {requested}")
        _git(repo, "checkout", "--detach", requested)
        head = _git(repo, "rev-parse", "HEAD")
    if head != requested:
        raise RuntimeError(f"Unable to verify requested commit: HEAD={head}, requested={requested}")
    return repo, requested


def _parse_defaults(parameters: str) -> dict[str, str]:
    defaults: dict[str, str] = {}
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    for char in parameters:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
            current.append(char)
        elif char in "([{":
            depth += 1
            current.append(char)
        elif char in ")]}":
            depth = max(0, depth - 1)
            current.append(char)
        elif char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current).strip())
    for part in parts:
        if "=" in part:
            name, default = part.split("=", 1)
            defaults[name.strip()] = default.strip()
    return defaults


def parse_r_functions(text: str, relative_file: str) -> list[RFunction]:
    """Parse common `name <- function(...)` forms with a regex.

    This is intentionally a lightweight parser; nested or unusual R syntax may
    not be fully represented. The README records this limitation when R is not
    installed or when this parser is used.
    """
    pattern = re.compile(r"(?ms)^\s*([A-Za-z.][A-Za-z0-9._]*)\s*(?:<-|=)\s*function\s*\((.*?)\)")
    functions: list[RFunction] = []
    for match in pattern.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        functions.append(RFunction(match.group(1), relative_file, line, _parse_defaults(match.group(2))))
    return functions


def build_index(repo_path: str | Path, commit_hash: str, *, checkout: bool = True) -> CodeIndex:
    repo, resolved_hash = prepare_repository(repo_path, commit_hash, checkout=checkout)
    files: list[IndexedFile] = []
    r_functions: list[RFunction] = []
    for directory in INDEX_DIRS:
        root = repo / directory
        if not root.exists():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file() and item.suffix in TEXT_SUFFIXES):
            relative = path.relative_to(repo).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            files.append(IndexedFile(relative, len(text.splitlines())))
            if path.suffix == ".R":
                r_functions.extend(parse_r_functions(text, relative))
    return CodeIndex(repo, resolved_hash, files, r_functions)


def _keywords(claim: Mapping[str, Any] | ExtractedClaim) -> list[str]:
    values = []
    for name in ("verbatim_sentence", "what_to_look_for", "claim_type"):
        value = getattr(claim, name, None) if not isinstance(claim, Mapping) else claim.get(name)
        if value:
            values.append(str(value))
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_.]*|\b\d+(?:\.\d+)?\b", " ".join(values))
    result: list[str] = []
    for token in tokens:
        if len(token) < 3 and not token.isdigit():
            continue
        if token.lower() in STOPWORDS:
            continue
        if token.lower() not in {item.lower() for item in result}:
            result.append(token)
    return result


def _read_excerpt(path: Path, start_line: int, end_line: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if start_line < 1 or end_line < start_line or end_line > len(lines):
        raise ValueError(f"line range {start_line}-{end_line} is outside file with {len(lines)} lines")
    return "".join(lines[start_line - 1:end_line])


def validate_location(repo_path: str | Path, item: Mapping[str, Any]) -> tuple[CodeLocation | None, str | None]:
    """Re-read a cited range and require exact excerpt equality."""
    try:
        relative = Path(str(item["code_file"]))
        start_line = int(item["start_line"])
        end_line = int(item["end_line"])
        expected = str(item["code_excerpt"])
        path = (Path(repo_path) / relative).resolve()
        repo = Path(repo_path).resolve()
        if repo not in path.parents:
            return None, "code_file resolves outside the repository"
        actual = _read_excerpt(path, start_line, end_line)
        if actual != expected:
            return None, "code_excerpt does not exactly match the cited on-disk lines"
        return CodeLocation(
            claim_id=str(item.get("claim_id", "")),
            package=str(item.get("package", "")),
            commit_hash=str(item.get("commit_hash", "")),
            code_file=relative.as_posix(),
            start_line=start_line,
            end_line=end_line,
            code_lines=f"{start_line}-{end_line}",
            code_excerpt=actual,
            keywords=list(item.get("keywords", [])),
            status=str(item.get("status", "candidate")),
        ), None
    except (KeyError, TypeError, ValueError, OSError) as exc:
        return None, f"invalid location: {exc}"


def locate_claims(index: CodeIndex, claims: Iterable[Mapping[str, Any] | ExtractedClaim], *, package: str = "", window: int = 2, max_candidates: int = 5, ranking_mode: str = "none", ranking_response: str | Path | None = None) -> LocationResult:
    locations: list[CodeLocation] = []
    not_found: list[dict[str, Any]] = []
    invalid: list[InvalidLocation] = []
    ranking = load_ranking_response(ranking_response) if ranking_mode == "demo" else {}
    for claim in claims:
        claim_dict = asdict(claim) if isinstance(claim, ExtractedClaim) else dict(claim)
        claim_id = str(claim_dict.get("id", ""))
        keywords = _keywords(claim_dict)
        scored: list[tuple[int, str, int]] = []
        for indexed in index.files:
            path = index.repo_path / indexed.path
            try:
                lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
            except (OSError, UnicodeDecodeError):
                continue
            for line_number, line in enumerate(lines, start=1):
                score = sum(1 for keyword in keywords if re.search(re.escape(keyword), line, re.IGNORECASE))
                if score:
                    scored.append((score, indexed.path, line_number))
        scored.sort(key=lambda item: (-item[0], item[1], item[2]))
        selected: list[dict[str, Any]] = []
        seen_ranges: set[tuple[str, int, int]] = set()
        for score, relative, line_number in scored:
            start = max(1, line_number - window)
            end = line_number
            path = index.repo_path / relative
            try:
                line_count = len(path.read_text(encoding="utf-8").splitlines(keepends=True))
                end = min(line_count, line_number + window)
                excerpt = _read_excerpt(path, start, end)
            except (OSError, UnicodeDecodeError, ValueError) as exc:
                invalid.append(InvalidLocation({"claim_id": claim_id, "code_file": relative, "start_line": start, "end_line": end}, f"could not read candidate: {exc}"))
                continue
            key = (relative, start, end)
            if key in seen_ranges:
                continue
            seen_ranges.add(key)
            selected.append({"claim_id": claim_id, "package": package, "commit_hash": index.commit_hash, "code_file": relative, "start_line": start, "end_line": end, "code_excerpt": excerpt, "keywords": keywords, "status": "candidate", "_score": score})
            if len(selected) >= max_candidates:
                break
        if ranking_mode == "demo":
            selected = apply_demo_ranking(selected, claim_id, ranking)
        elif ranking_mode == "api":
            selected = _rank_with_configured_llm(claim_dict, selected)
        if not selected:
            not_found.append({"claim_id": claim_id, "package": package, "commit_hash": index.commit_hash, "status": "not found", "keywords": keywords})
            continue
        for item in selected:
            item.pop("_score", None)
            location, reason = validate_location(index.repo_path, item)
            if location is None:
                invalid.append(InvalidLocation(item, reason or "validation failed"))
            else:
                locations.append(location)
    return LocationResult(locations=locations, not_found=not_found, invalid=invalid)


def load_ranking_response(path: str | Path | None) -> dict[str, Any]:
    response_path = Path(path) if path else Path(__file__).parent.parent / "demo" / "code_location_ranking.json"
    return json.loads(response_path.read_text(encoding="utf-8"))


def apply_demo_ranking(candidates: list[dict[str, Any]], claim_id: str, response: Mapping[str, Any]) -> list[dict[str, Any]]:
    order = response.get("rankings", {}).get(claim_id)
    return apply_rank_order(candidates, order)


def apply_rank_order(candidates: list[dict[str, Any]], order: Any) -> list[dict[str, Any]]:
    if not isinstance(order, list):
        return candidates
    reordered: list[dict[str, Any]] = []
    used: set[int] = set()
    for index in order:
        if isinstance(index, int) and 0 <= index < len(candidates) and index not in used:
            reordered.append(candidates[index])
            used.add(index)
    reordered.extend(candidate for index, candidate in enumerate(candidates) if index not in used)
    return reordered


def _rank_with_configured_llm(claim: Mapping[str, Any], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Use the optional generic LLM layer only when ranking mode is explicitly API."""
    from .llm import LLMClient
    prompt = (
        "Rank candidate code locations for this paper claim. Return JSON only as "
        '{"order": [integer indices]}. Never add indices or alter candidate data. '
        "If none are relevant, return {\"order\": []}.\n"
        f"CLAIM:\n{json.dumps(dict(claim), ensure_ascii=False)}\n"
        f"CANDIDATES:\n{json.dumps([{k: v for k, v in item.items() if k != '_score'} for item in candidates], ensure_ascii=False)}"
    )
    response = LLMClient().complete_json(prompt, purpose="code-location-ranking")
    return apply_rank_order(candidates, response.get("order"))


def _rank_with_anthropic(
    claim: Mapping[str, Any],
    candidates: list[dict[str, Any]],
    *,
    api_key_env: str = "ANTHROPIC_API_KEY",
    model_env: str = "ANTHROPIC_MODEL",
    cache_dir: str | Path = ".cache/code_location_ranking",
    log_path: str | Path = "logs/llm_calls.jsonl",
    timeout: int = 120,
) -> list[dict[str, Any]]:
    """Optionally rank keyword candidates; never invent or modify excerpts."""
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(f"Missing API key environment variable: {api_key_env}")
    model = os.environ.get(model_env, "claude-3-5-sonnet-latest")
    prompt = (
        "Rank the candidate code locations for this paper claim by likely relevance. "
        "Return JSON only as {\"order\": [integer indices]}. Do not add indices. "
        "If none are relevant, return {\"order\": []}.\n\n"
        f"CLAIM:\n{json.dumps(dict(claim), ensure_ascii=False)}\n\n"
        f"CANDIDATES:\n{json.dumps([{k: v for k, v in item.items() if k != '_score'} for item in candidates], ensure_ascii=False)}"
    )
    cache_key = hashlib.sha256(f"{model}\n{prompt}".encode("utf-8")).hexdigest()
    cache_path = Path(cache_dir) / f"{cache_key}.json"
    if cache_path.exists():
        response = json.loads(cache_path.read_text(encoding="utf-8"))
        return apply_rank_order(candidates, response.get("order"))
    payload = {"model": model, "max_tokens": 512, "temperature": 0, "messages": [{"role": "user", "content": prompt}]}
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            api_result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Anthropic ranking request failed ({exc.code}): {detail}") from exc
    response_text = "".join(block.get("text", "") for block in api_result.get("content", []) if block.get("type") == "text").strip()
    if response_text.startswith("```"):
        response_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", response_text, flags=re.IGNORECASE | re.DOTALL).strip()
    parsed = json.loads(response_text)
    if not isinstance(parsed, dict):
        raise ValueError("LLM ranking response must be a JSON object")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(log_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "model": model, "prompt_version": "code-location-ranking-v1", "prompt": prompt, "response": parsed}, ensure_ascii=False) + "\n")
    return apply_rank_order(candidates, parsed.get("order"))


def load_accepted_claims(path: str | Path) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("accepted"), list):
        return [dict(item) for item in data["accepted"]]
    if isinstance(data, list):
        return [dict(item) for item in data]
    raise ValueError("claims JSON must be a list or an object with an accepted list")


def _json_output(result: LocationResult) -> dict[str, Any]:
    return {"locations": [item.to_output() for item in result.locations], "not_found": result.not_found, "invalid": [asdict(item) for item in result.invalid]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Locate accepted paper claims in a pinned R/Bioconductor repository commit.")
    parser.add_argument("repo", type=Path)
    parser.add_argument("commit_hash")
    parser.add_argument("claims_json", type=Path, help="Step 2 JSON output or a JSON list of accepted claims")
    parser.add_argument("--package", default="")
    parser.add_argument("--no-checkout", action="store_true", help="Require HEAD to already match the requested commit")
    parser.add_argument("--ranking", choices=("none", "demo", "api"), default="none", help="Optional ranking mode: deterministic, saved demo response, or Anthropic API")
    parser.add_argument("--ranking-response", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    index = build_index(args.repo, args.commit_hash, checkout=not args.no_checkout)
    result = locate_claims(index, load_accepted_claims(args.claims_json), package=args.package, ranking_mode=args.ranking, ranking_response=args.ranking_response)
    output = json.dumps(_json_output(result), indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
