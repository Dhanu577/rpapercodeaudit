from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if total == 0:
        return None, None
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * ((p * (1 - p) + z * z / (4 * total)) / total) ** 0.5 / denominator
    return max(0.0, centre - margin), min(1.0, centre + margin)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        rendered = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(rendered) + " |")
    return "\n".join(lines)


def build_reports(results: list[dict[str, Any]], cases: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    by_id = {row["case_id"]: row for row in results}
    if set(by_id) != {case["case_id"] for case in cases}:
        raise ValueError("result case IDs do not match frozen case IDs")

    metric_rows = []
    for label in ("must_accept", "must_reject"):
        group = [row for row in results if row["expected_class"] == label]
        n = len(group)
        accepted = sum(bool(row["observed"]) for row in group)
        rejected = n - accepted
        for metric, successes in (("acceptance_rate", accepted), ("rejection_rate", rejected)):
            low, high = wilson(successes, n)
            metric_rows.append({
                "expected_class": label,
                "metric": metric,
                "successes": successes,
                "n": n,
                "rate": successes / n if n else None,
                "ci_low": low,
                "ci_high": high,
            })
    write_csv(output_dir / "metrics_v2.csv", metric_rows)

    type_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        type_groups[(row["group"], row["mutation_type"], row["expected_class"])].append(row)
    per_type_rows = []
    for (group, mutation, label), rows in sorted(type_groups.items()):
        n = len(rows)
        accepted = sum(bool(row["observed"]) for row in rows)
        rejected = n - accepted
        match = None if label == "boundary" else (
            accepted == n if label == "must_accept" else rejected == n
        )
        per_type_rows.append({
            "group": group,
            "mutation_type": mutation,
            "expected_class": label,
            "n": n,
            "accepted": accepted,
            "rejected": rejected,
            "observed_vs_expected": "observed_only" if match is None else ("all_match" if match else "disagreement"),
            "flag_n_lt_20": n < 20,
        })
    write_csv(output_dir / "per_type_v2.csv", per_type_rows)

    boundary_rows = [row for row in results if row["expected_class"] == "boundary"]
    boundary_type_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in boundary_rows:
        boundary_type_counts[row["mutation_type"]]["accepted" if row["observed"] else "rejected"] += 1
    boundary_summary = [
        [mutation, sum(counts.values()), counts["accepted"], counts["rejected"]]
        for mutation, counts in sorted(boundary_type_counts.items())
    ]
    boundary_lines = [
        "# Boundary findings",
        "",
        "Boundary labels were assigned before running the validators and are not scored as false acceptances or false rejections. This file records observed behavior only.",
        "",
        "## Summary by mutation type",
        "",
        markdown_table(["Mutation type", "n", "Accepted", "Rejected"], boundary_summary),
        "",
        "## Per-case observations",
        "",
        markdown_table(
            ["Case", "Mutation type", "Observed", "Validator", "Raw error"],
            [[row["case_id"], row["mutation_type"], "accepted" if row["observed"] else "rejected", row["validator"], row.get("raw_error") or "—"] for row in boundary_rows],
        ),
        "",
    ]
    (output_dir / "boundary_findings.md").write_text("\n".join(boundary_lines), encoding="utf-8")

    unexpected = [
        row for row in results
        if (row["expected_class"] == "must_accept" and not row["observed"])
        or (row["expected_class"] == "must_reject" and row["observed"])
    ]
    bugs_lines = [
        "# Bugs found",
        "",
        "Labels are retained exactly as frozen. Boundary cases are excluded from this list.",
        "",
    ]
    if not unexpected:
        bugs_lines.append("No must_accept case was rejected and no must_reject case was accepted.")
    else:
        for row in unexpected:
            bugs_lines.extend([
                f"## {row['case_id']}",
                "",
                f"- Expected class: `{row['expected_class']}`; observed: `{'accepted' if row['observed'] else 'rejected'}`.",
                f"- Validator: `{row['validator']}`.",
                f"- Hypothesis: Potential validator behavior inconsistent with the documented rule, a label/input boundary, or a platform effect; investigate without reclassifying this case.",
                "- Input and raw validator log:",
                "```json",
                json.dumps({"validator_inputs": row["validator_inputs"], "raw_error": row.get("raw_error"), "observed": row["observed"]}, ensure_ascii=False, indent=2),
                "```",
                "",
            ])
    (output_dir / "bugs_found.md").write_text("\n".join(bugs_lines), encoding="utf-8")

    class_counts = Counter(row["expected_class"] for row in results)
    accepted_total = sum(bool(row["observed"]) for row in results)
    metrics_md = []
    for label in ("must_accept", "must_reject"):
        rows = [row for row in metric_rows if row["expected_class"] == label]
        metrics_md.append([label, rows[0]["n"], f"{rows[0]['rate']:.3f}", f"[{rows[0]['ci_low']:.3f}, {rows[0]['ci_high']:.3f}]", f"{rows[1]['rate']:.3f}", f"[{rows[1]['ci_low']:.3f}, {rows[1]['ci_high']:.3f}]"])
    report = [
        "# Adversarial validator benchmark v2",
        "",
        "## Methods",
        "",
        "Cases were generated from seed 42 and frozen with a SHA-256 checksum before any validator run. Sentence cases call the project's `validate_claims()`; commit cases call `prepare_repository()` with their declared `checkout` value; location cases call `validate_location()`. The runner records each function's output or raw error. It does not reproduce checks locally. DESeq2 and its fixture repository are not used or executed; all repository and file inputs are synthetic static text.",
        "",
        f"Cases: **{len(results)}** total — must_accept **{class_counts['must_accept']}**, must_reject **{class_counts['must_reject']}**, boundary **{class_counts['boundary']}**. Overall accepted by the called function: **{accepted_total}**.",
        "",
        "## Acceptance/rejection rates (Wilson 95% CI)",
        "",
        markdown_table(["Expected class", "n", "Acceptance rate", "95% CI", "Rejection rate", "95% CI"], metrics_md),
        "",
        "Boundary cases are reported as observations only and are not included in these rates.",
        "",
        "## Per mutation type",
        "",
        markdown_table(
            ["Group", "Mutation type", "Class", "n", "Accepted", "Rejected", "Observed vs expected"],
            [[row["group"], row["mutation_type"], row["expected_class"], row["n"], row["accepted"], row["rejected"], row["observed_vs_expected"]] for row in per_type_rows],
        ),
        "",
        f"Mutation types with n < 20: **{sum(row['flag_n_lt_20'] for row in per_type_rows)}** (all generated types have n ≥ 10; see `per_type_v2.csv` for flags).",
        "",
        f"## Bugs and boundaries\n\nMust-accept rejections or must-reject acceptances: **{len(unexpected)}**. See `bugs_found.md` for case inputs, raw logs, and hypotheses. Boundary cases: **{class_counts['boundary']}**; see `boundary_findings.md` for observed behavior.",
        "",
        "## Platform and limitations",
        "",
        f"- OS/platform: `{platform.platform()}`.",
        f"- Python: `{sys.version.split()[0]}`.",
        "- File-name case behavior is tested on the filesystem hosting this run; boundary observations should not be generalized to all filesystems.",
        "- These tests establish only observed validator behavior on the frozen synthetic inputs, not semantic correctness or behavior for every possible path or Git reference.",
        "- The generated repository contains synthetic text and Git metadata only; no fixture code was executed.",
        "",
    ]
    (output_dir / "REPORT_v2.md").write_text("\n".join(report), encoding="utf-8")
    summary = {
        "cases": len(results),
        "classes": dict(class_counts),
        "unexpected_must_accept_or_must_reject": len(unexpected),
        "boundary_cases": class_counts["boundary"],
    }
    (output_dir / "summary_v2.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=ROOT / "benchmark" / "results_v2.jsonl")
    parser.add_argument("--cases", type=Path, default=ROOT / "benchmark" / "cases_v2.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmark")
    args = parser.parse_args()
    results = read_jsonl(args.results)
    cases = read_jsonl(args.cases)
    print(json.dumps(build_reports(results, cases, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
