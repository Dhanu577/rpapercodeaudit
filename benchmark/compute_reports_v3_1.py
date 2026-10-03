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


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    if total == 0:
        return None, None
    if successes == 0:
        return 0.0, z * z / (total + z * z)
    if successes == total:
        return total / (total + z * z), 1.0
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * ((p * (1 - p) + z * z / (4 * total)) / total) ** 0.5 / denominator
    return max(0.0, centre - margin), min(1.0, centre + margin)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        values = [str(value).replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def compare_v1(old_rows: list[dict[str, Any]], new_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    old = {row["case_id"]: row for row in old_rows}
    new = {row["case_id"]: row for row in new_rows}
    if old.keys() != new.keys():
        raise ValueError("v1 regression IDs differ from the original 422 results")
    changes = []
    for case_id in sorted(old):
        old_stages = old[case_id].get("stage_results", {})
        new_stages = new[case_id].get("stage_results", {})
        changed_stages = [key for key in sorted(set(old_stages) | set(new_stages)) if old_stages.get(key) != new_stages.get(key)]
        old_final = bool(old[case_id]["final_decision"])
        new_final = bool(new[case_id]["final_decision"])
        if old_final != new_final or changed_stages:
            changes.append({
                "case_id": case_id,
                "old_final": old_final,
                "new_final": new_final,
                "final_changed": old_final != new_final,
                "changed_stages": changed_stages,
                "old_stage_results": old_stages,
                "new_stage_results": new_stages,
                "old_first_failing_stage": old[case_id].get("first_failing_stage"),
                "new_first_failing_stage": new[case_id].get("first_failing_stage"),
                "old_errors": {"repo": old[case_id].get("repo_error"), "location": old[case_id].get("location_error")},
                "new_errors": {"repo": new[case_id].get("repo_error"), "location": new[case_id].get("location_error")},
            })
    return changes


def compare_v2(old_rows: list[dict[str, Any]], new_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    old = {row["case_id"]: row for row in old_rows}
    new = {row["case_id"]: row for row in new_rows}
    if old.keys() != new.keys():
        raise ValueError("v2 regression IDs differ from the original 520 results")
    changes = []
    for case_id in sorted(old):
        old_observed = bool(old[case_id]["observed"])
        new_observed = bool(new[case_id]["observed"])
        if old_observed != new_observed:
            changes.append({
                "case_id": case_id,
                "group": old[case_id].get("group"),
                "mutation_type": old[case_id].get("mutation_type"),
                "expected_class": old[case_id].get("expected_class"),
                "old_observed": old_observed,
                "new_observed": new_observed,
                "old_raw_error": old[case_id].get("raw_error"),
                "new_raw_error": new[case_id].get("raw_error"),
            })
    return changes


def write_regression_report(v1_changes: list[dict[str, Any]], v2_changes: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Regression report: v1/v2 on the v3.1 validator",
        "",
        "Comparisons use the original committed result files and the new, separately named rerun outputs. A v1 row is listed if its final decision **or any stage result** changed. A v2 row is listed when the real validator's `observed` acceptance outcome changed. No case was reclassified.",
        "",
        f"- V1 cases compared: 422; changed outcomes/stages: **{len(v1_changes)}**.",
        f"- V2 cases compared: 520; changed outcomes: **{len(v2_changes)}**.",
        "",
        "## V1 case changes",
        "",
    ]
    if v1_changes:
        lines.append(markdown_table(
            ["Case", "Old → new final", "Changed stages", "Old → new stage summary", "Old → new first failure"],
            [[row["case_id"], f"{row['old_final']} → {row['new_final']}", ", ".join(row["changed_stages"]) or "—", f"{row['old_stage_results']} → {row['new_stage_results']}", f"{row['old_first_failing_stage']} → {row['new_first_failing_stage']}"] for row in v1_changes],
        ))
        lines.extend(["", "### V1 error details", ""])
        for row in v1_changes:
            lines.extend([f"#### `{row['case_id']}`", "", f"- Old errors: `{row['old_errors']}`", f"- New errors: `{row['new_errors']}`", ""])
    else:
        lines.append("No v1 final decision or stage result changed.")
    lines.extend(["", "## V2 case changes", ""])
    if v2_changes:
        lines.append(markdown_table(
            ["Case", "Group", "Mutation", "Class", "Old observed", "New observed", "Old raw error", "New raw error"],
            [[row["case_id"], row["group"], row["mutation_type"], row["expected_class"], row["old_observed"], row["new_observed"], row["old_raw_error"] or "—", row["new_raw_error"] or "—"] for row in v2_changes],
        ))
    else:
        lines.append("No v2 observed acceptance outcome changed.")
    lines.extend(["", "All rows above retain their original case labels. Full new result records are in `results_v1_on_v3validator.jsonl` and `results_v2_on_v3validator.jsonl`.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def build_v3_reports(results: list[dict[str, Any]], cases: list[dict[str, Any]], out: Path, natural_summary: dict[str, Any]) -> dict[str, Any]:
    by_id = {row["case_id"]: row for row in results}
    if set(by_id) != {case["case_id"] for case in cases}:
        raise ValueError("v3.1 result case IDs do not match the frozen case IDs")

    class_counts = Counter(row["expected_class"] for row in results)
    metrics: list[dict[str, Any]] = []
    metric_table = []
    for label in ("must_accept", "must_reject"):
        group = [row for row in results if row["expected_class"] == label]
        n = len(group)
        accepted = sum(bool(row["observed"]) for row in group)
        rejected = n - accepted
        for metric, successes in (("acceptance_rate", accepted), ("rejection_rate", rejected)):
            low, high = wilson(successes, n)
            metrics.append({"expected_class": label, "metric": metric, "successes": successes, "n": n, "rate": successes / n if n else None, "ci_low": low, "ci_high": high})
        metric_table.append([label, n, f"{accepted / n:.3f}" if n else "—", f"[{wilson(accepted, n)[0]:.3f}, {wilson(accepted, n)[1]:.3f}]" if n else "—", f"{rejected / n:.3f}" if n else "—", f"[{wilson(rejected, n)[0]:.3f}, {wilson(rejected, n)[1]:.3f}]" if n else "—"])
    write_csv(out / "metrics_v3_1.csv", metrics)

    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        groups[(row["group"], row["mutation_type"], row["expected_class"])].append(row)
    per_type = []
    for (group, mutation, label), rows in sorted(groups.items()):
        n = len(rows)
        accepted = sum(bool(row["observed"]) for row in rows)
        rejected = n - accepted
        agreement = "observed_only" if label == "boundary" else ("all_match" if (accepted == n if label == "must_accept" else rejected == n) else "disagreement")
        per_type.append({"group": group, "mutation_type": mutation, "expected_class": label, "n": n, "accepted": accepted, "rejected": rejected, "observed_vs_expected": agreement, "flag_n_lt_20": n < 20})
    write_csv(out / "per_type_v3_1.csv", per_type)

    boundary = [row for row in results if row["expected_class"] == "boundary"]
    boundary_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in boundary:
        boundary_counts[row["mutation_type"]]["accepted" if row["observed"] else "rejected"] += 1
    boundary_lines = ["# V3.1 boundary findings", "", "Boundary cases were labeled before the run and are reported as observations only; they are excluded from must-class rates.", "", "## By mutation type", "", markdown_table(["Mutation type", "n", "Accepted", "Rejected"], [[name, sum(count.values()), count["accepted"], count["rejected"]] for name, count in sorted(boundary_counts.items())]), "", "## Per-case observations", "", markdown_table(["Case", "Mutation type", "Observed", "Validator", "Raw error"], [[row["case_id"], row["mutation_type"], "accepted" if row["observed"] else "rejected", row["validator"], row.get("raw_error") or "—"] for row in boundary]), ""]
    (out / "boundary_findings_v3_1.md").write_text("\n".join(boundary_lines), encoding="utf-8")

    failures = [row for row in results if (row["expected_class"] == "must_accept" and not row["observed"]) or (row["expected_class"] == "must_reject" and row["observed"])]
    bug_lines = ["# Bugs found in v3.1", "", "Labels are retained exactly as frozen. Boundary cases are excluded.", ""]
    if not failures:
        bug_lines.append("No must_accept case was rejected and no must_reject case was accepted.")
    else:
        for row in failures:
            bug_lines.extend([f"## {row['case_id']}", "", f"- Expected `{row['expected_class']}`; observed `{'accepted' if row['observed'] else 'rejected'}`.", f"- Validator: `{row['validator']}`.", "- Raw log and validator input:", "```json", json.dumps({"validator_inputs": row["validator_inputs"], "raw_error": row.get("raw_error"), "observed": row["observed"]}, ensure_ascii=False, indent=2), "```", ""])
    (out / "bugs_found_v3.md").write_text("\n".join(bug_lines), encoding="utf-8")

    accepted_total = sum(bool(row["observed"]) for row in results)
    out.mkdir(parents=True, exist_ok=True)
    mutation_type_counts = Counter(row["mutation_type"] for row in results)
    summary = {"cases": len(results), "classes": dict(class_counts), "accepted": accepted_total, "must_class_failures": len(failures), "boundary_cases": class_counts["boundary"], "mutation_types": len(mutation_type_counts), "types_n_lt_20": sum(count < 20 for count in mutation_type_counts.values())}
    (out / "summary_v3_1.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = [
        "# Adversarial validator benchmark v3.1", "",
        "## Methods", "",
        "The v3.1 cases were regenerated from seed 42, checksum-frozen, pushed, and tagged before this run. Sentence cases call `validate_claims()`, commit cases call `prepare_repository()`, and location cases call `validate_location()`. The runner performs no duplicate validation checks. No labels were changed after observing results.", "",
        f"Cases: **{len(results)}** — `must_accept` **{class_counts['must_accept']}**, `must_reject` **{class_counts['must_reject']}**, `boundary` **{class_counts['boundary']}**. Validator accepted **{accepted_total}** total cases.", "",
        "## Acceptance/rejection rates (Wilson 95% CI)", "", markdown_table(["Expected class", "n", "Acceptance rate", "95% CI", "Rejection rate", "95% CI"], metric_table), "",
        "Boundary cases are excluded from these rates and are reported only as observed in `boundary_findings_v3_1.md`.", "",
        "## Per mutation type", "", markdown_table(["Group", "Mutation type", "Class", "n", "Accepted", "Rejected", "Observed vs expected"], [[row["group"], row["mutation_type"], row["expected_class"], row["n"], row["accepted"], row["rejected"], row["observed_vs_expected"]] for row in per_type]), "",
        f"Distinct mutation types: **{summary['mutation_types']}**; types with n < 20: **{summary['types_n_lt_20']}**.", "",
        f"Must-class failures: **{len(failures)}**. See `bugs_found_v3.md`. Boundary cases: **{class_counts['boundary']}**.", "",
        "## Pilot, natural proposals, and report-only flags", "",
        f"The preflight accepted all **24/24** original valid pilot records. The saved natural deterministic proposals were **{natural_summary['accepted']} accepted / {natural_summary['rejected']} rejected**. Short sentences (<5 normalized whitespace tokens): **{natural_summary['short_sentence_count']}**; reference-like heuristic: **{natural_summary['reference_like_count']}**; both: **{natural_summary['both_flags_count']}**. These are report-only flags and do not influence validator decisions. See `natural_proposals_v3_1_flags.csv`.", "",
        "## v1/v2 regressions", "",
        "Every changed v1 stage/final decision and every changed v2 acceptance outcome is listed in `regression_report.md`. New results are kept in `results_v1_on_v3validator.jsonl` and `results_v2_on_v3validator.jsonl` without overwriting prior outputs.", "",
        "## Limitations", "",
        f"- OS/platform: `{platform.platform()}`; Python `{sys.version.split()[0]}`.",
        "- Project-authored unit tests do not independently establish semantic correctness.",
        "- The synthetic benchmark uses at least 10 cases per mutation type; several groups are still small.",
        "- File-name case observations are specific to the tested Linux filesystem.",
        "- Natural proposal flags are heuristic report annotations, not semantic classifications or validator rules.", "",
    ]
    (out / "REPORT_v3.md").write_text("\n".join(report), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute v3.1 metrics and exhaustive v1/v2 regression diffs without rerunning validators.")
    parser.add_argument("--cases", type=Path, default=ROOT / "benchmark" / "cases_v3.jsonl")
    parser.add_argument("--results", type=Path, default=ROOT / "benchmark" / "results_v3_1.jsonl")
    parser.add_argument("--out", type=Path, default=ROOT / "benchmark")
    parser.add_argument("--v1-old", type=Path, default=ROOT / "benchmark" / "results_deterministic.jsonl")
    parser.add_argument("--v1-new", type=Path, default=ROOT / "benchmark" / "results_v1_on_v3validator.jsonl")
    parser.add_argument("--v2-old", type=Path, default=ROOT / "benchmark" / "results_v2.jsonl")
    parser.add_argument("--v2-new", type=Path, default=ROOT / "benchmark" / "results_v2_on_v3validator.jsonl")
    parser.add_argument("--natural-summary", type=Path, default=ROOT / "benchmark" / "natural_proposals_v3_1_summary.json")
    args = parser.parse_args()
    results = read_jsonl(args.results)
    cases = read_jsonl(args.cases)
    v1_changes = compare_v1(read_jsonl(args.v1_old), read_jsonl(args.v1_new))
    v2_changes = compare_v2(read_jsonl(args.v2_old), read_jsonl(args.v2_new))
    write_regression_report(v1_changes, v2_changes, args.out / "regression_report.md")
    natural_summary = json.loads(args.natural_summary.read_text(encoding="utf-8"))
    summary = build_v3_reports(results, cases, args.out, natural_summary)
    summary["v1_changed_cases_or_stages"] = len(v1_changes)
    summary["v2_changed_cases"] = len(v2_changes)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
