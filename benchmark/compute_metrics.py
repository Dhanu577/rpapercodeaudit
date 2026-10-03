from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STAGES = ["sentence_match", "repo_commit_valid", "file_exists", "line_range_valid", "excerpt_matches"]


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0: return (float("nan"), float("nan"))
    p = successes / total; denom = 1 + z*z/total; centre = (p + z*z/(2*total))/denom; margin = z*math.sqrt((p*(1-p)+z*z/(4*total))/total)/denom
    return centre - margin, centre + margin


def read_results(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows: return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, default=ROOT / "benchmark" / "results_deterministic.jsonl"); parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmark"); args = parser.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    results = read_results(args.input); tier_a = [r for r in results if r["tier"] == "A"]; tier_b = [r for r in results if r["tier"] == "B"]
    valid = [r for r in tier_a if r["expected_valid"]]; invalid = [r for r in tier_a if not r["expected_valid"]]
    accepted_valid = [r for r in valid if r["final_decision"]]; rejected_valid = [r for r in valid if not r["final_decision"]]; rejected_invalid = [r for r in invalid if not r["final_decision"]]; accepted_invalid = [r for r in invalid if r["final_decision"]]
    metrics=[]
    for name, successes, total in [("acceptance_rate",len(accepted_valid),len(valid)),("false_rejection_rate",len(rejected_valid),len(valid)),("rejection_rate",len(rejected_invalid),len(invalid)),("false_acceptance_rate",len(accepted_invalid),len(invalid))]:
        lo, hi = wilson(successes,total); metrics.append({"metric":name,"successes":successes,"n":total,"rate":successes/total if total else None,"ci_low":lo,"ci_high":hi})
    write_csv(args.output_dir / "metrics_summary.csv", metrics)
    by_type=[]
    for mutation in sorted({r["mutation_type"] for r in tier_a}):
        group=[r for r in tier_a if r["mutation_type"]==mutation]; rejected=sum(not r["final_decision"] for r in group); lo,hi=wilson(rejected,len(group)); by_type.append({"mutation_type":mutation,"n":len(group),"rejected":rejected,"accepted":len(group)-rejected,"rejection_rate":rejected/len(group) if group else None,"ci_low":lo,"ci_high":hi,"flag_n_lt_20":len(group)<20})
    write_csv(args.output_dir / "per_type_table.csv", by_type)
    matrix=[]
    for mutation in sorted({r["mutation_type"] for r in tier_a}):
        group=[r for r in tier_a if r["mutation_type"]==mutation]
        row={"mutation_type":mutation,"n":len(group)}
        for stage in STAGES:
            row[f"{stage}_any_stage_catch"]=sum(not r["stage_results"][stage] for r in group)/len(group)
            row[f"{stage}_first_stage_catch"]=sum(r["first_failing_stage"]==stage for r in group)/len(group)
        matrix.append(row)
    write_csv(args.output_dir / "stage_matrix.csv", matrix)
    anomalies=[]
    for r in tier_a:
        if bool(r["final_decision"]) != bool(r["expected_valid"]):
            anomalies.append({"case_id":r["case_id"],"expected_valid":r["expected_valid"],"final_decision":r["final_decision"],"first_failing_stage":r["first_failing_stage"],"stage_results":r["stage_results"],"hypothesis":"bug, label error, or boundary case: inspect case construction and validator stage semantics."})
    lines=["# Benchmark anomalies","",f"False acceptances/rejections: **{len(anomalies)}**.",""]
    for item in anomalies: lines += [f"## {item['case_id']}",f"- Expected valid: `{item['expected_valid']}`; final decision: `{item['final_decision']}`",f"- First failing stage: `{item['first_failing_stage']}`",f"- Stage log: `{json.dumps(item['stage_results'], sort_keys=True)}`",f"- Hypothesis: {item['hypothesis']}",""]
    (args.output_dir / "anomalies.md").write_text("\n".join(lines), encoding="utf-8")
    tier_b_rows=[]
    for mutation in sorted({r["mutation_type"] for r in tier_b}):
        group=[r for r in tier_b if r["mutation_type"]==mutation]; tier_b_rows.append({"mutation_type":mutation,"n":len(group),"mechanically_accepted":sum(r["final_decision"] for r in group),"acceptance_rate":sum(r["final_decision"] for r in group)/len(group)})
    write_csv(args.output_dir / "tier_b_summary.csv", tier_b_rows)
    try:
        import matplotlib.pyplot as plt
        figdir=args.output_dir / "figures"; figdir.mkdir(exist_ok=True)
        labels=[r["mutation_type"] for r in by_type]; rates=[r["rejection_rate"] for r in by_type]; lower=[max(0.0, r["rejection_rate"]-r["ci_low"]) for r in by_type]; upper=[max(0.0, r["ci_high"]-r["rejection_rate"]) for r in by_type]
        plt.figure(figsize=(11,5)); plt.bar(labels,rates,yerr=[lower,upper],capsize=4,color="#2f7f73"); plt.xticks(rotation=35,ha="right"); plt.ylabel("Rejection rate"); plt.title("Tier A rejection rate by mutation type (Wilson 95% CI)"); plt.tight_layout(); plt.savefig(figdir / "acceptance_rejection_rates.png",dpi=160); plt.close()
        stage_labels=STAGES; data=[[row[f"{s}_any_stage_catch"] for s in stage_labels] for row in matrix]
        plt.figure(figsize=(11,8)); plt.imshow(data,aspect="auto",cmap="YlGnBu",vmin=0,vmax=1); plt.colorbar(label="Fraction caught"); plt.xticks(range(len(stage_labels)),stage_labels,rotation=35,ha="right"); plt.yticks(range(len(labels)),labels); plt.title("Stage-by-mutation any-stage catch rate"); plt.tight_layout(); plt.savefig(figdir / "stage_by_mutation_heatmap.png",dpi=160); plt.close()
    except Exception as exc:
        (args.output_dir / "figures_unavailable.txt").write_text(f"Figures unavailable: {exc}\n", encoding="utf-8")
    summary={"tier_a": {"n":len(tier_a),"valid":len(valid),"invalid":len(invalid),"false_acceptances":len(accepted_invalid),"false_rejections":len(rejected_valid)},"tier_b": {"n":len(tier_b)},"anomalies":len(anomalies)}
    (args.output_dir / "metrics_summary.json").write_text(json.dumps(summary,indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__": main()
