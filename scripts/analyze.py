#!/usr/bin/env python3
"""Rebuild numerical results from included metadata, offline, with stdlib only."""
import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARISONS = [
    ("P_L_TRIZ_ON", "P_L_TRIZ_OFF", "TRIZ content / long prompts"),
    ("P_S_TRIZ_ON", "P_S_TRIZ_OFF", "TRIZ mention / short prompts"),
    ("P_L_TRIZ_OFF", "P_S_TRIZ_OFF", "Generic structure / no TRIZ"),
    ("P_L_TRIZ_ON", "P_S_TRIZ_ON", "Long vs short / TRIZ on"),
]


def read(name):
    with (ROOT / "evidence" / name).open(newline="") as f:
        return list(csv.DictReader(f))


def family(model):
    # Provider-level exclusion is conservative here; both DeepSeek aliases map together.
    return model.strip().lower().split("/")[0]


def valid(r):
    return (not r["error"] and r["pick"] in ("A", "B") and
            r["a_arm"] != r["b_arm"] and
            r["picked_arm"] == r["a_arm" if r["pick"] == "A" else "b_arm"])


def filter_votes(rows, cross=True):
    good = [r for r in rows if valid(r)]
    eligible = [r for r in good if not cross or family(r["judge_model"]) != family(r["gen_model"])]
    groups = defaultdict(list)
    for r in eligible:
        groups[r["pair_id"], r["judge_model"], r["persona"]].append(r)
    kept = []
    for rs in groups.values():
        if len(rs) != 2:
            continue
        a, b = rs
        if (a["order"] != b["order"] and a["a_arm"] == b["b_arm"] and
                a["b_arm"] == b["a_arm"] and a["case_id"] == b["case_id"] and
                a["gen_model"] == b["gen_model"] and a["picked_arm"] == b["picked_arm"]):
            kept.append(a)
    return kept, {"rows": len(rows), "valid_rows": len(good), "cross_family_rows": len(eligible),
                  "candidate_vote_groups": len(groups), "retained_votes": len(kept),
                  "retention": len(kept) / len(groups) if groups else None}


def estimate(votes, treatment, reps=10000):
    if not votes:
        raise ValueError("No retained votes")
    groups = defaultdict(list)
    for r in votes:
        groups[r["case_id"]].append(int(r["picked_arm"] == treatment))
    # Sorted keys + local RNG make each interval independent of analysis call order.
    clusters = [(sum(groups[k]), len(groups[k])) for k in sorted(groups)]
    wins = sum(s for s, n in clusters)
    count = sum(n for s, n in clusters)
    rng = random.Random(20261027)
    draws = []
    for _ in range(reps):
        sample = rng.choices(clusters, k=len(clusters))
        draws.append(sum(s for s, n in sample) / sum(n for s, n in sample))
    draws.sort()
    return {"wins": wins, "votes": count, "cases": len(clusters), "p": wins / count,
            "ci_low": draws[int(.025 * reps)], "ci_high": draws[int(.975 * reps)],
            "case_balanced_p": sum(s / n for s, n in clusters) / len(clusters)}


def selection_results(rows, same_rows):
    out = []
    models = sorted({r["judge"] for r in rows})
    for model in models:
        for condition in ("rank", "score_batch"):
            sub = [r for r in rows if r["judge"] == model and r["condition"] == condition]
            groups = defaultdict(list)
            for r in sub:
                groups[r["set_id"]].append(r)
            pairs = []
            usable = []
            for rs in groups.values():
                for r in rs:
                    order = r["presented_order"].split(";")
                    if r["parse_status"] in ("ok", "discard_only") and r["discard_candidate_id"] in order:
                        assert len(order) == 41 and len(set(order)) == 41
                        assert order[int(r["discard_position"]) - 1] == r["discard_candidate_id"]
                        usable.append(r)
                if len(rs) == 2 and len({r["shuffle"] for r in rs}) == 2 and all(r in usable for r in rs):
                    pairs.append(rs)
            matches = sum(a["discard_candidate_id"] == b["discard_candidate_id"] for a, b in pairs)
            fixed = [r for r in same_rows if r["judge"] == model and r["condition"] == condition and
                     r["n"] == "41" and r["rep0_status"] in ("ok", "discard_only") and
                     r["rep1_status"] in ("ok", "discard_only") and r["rep0_discard"] and r["rep1_discard"]]
            fixed_matches = sum(r["rep0_discard"] == r["rep1_discard"] for r in fixed)
            out.append({"judge": model, "condition": condition, "attempted_calls": len(sub),
                        "usable_calls": len(usable), "slates": len(pairs), "matches": matches,
                        "shuffled_agreement": matches / len(pairs) if pairs else None,
                        "same_order_trials": len(fixed), "same_order_matches": fixed_matches,
                        "same_order_agreement": fixed_matches / len(fixed) if fixed else None,
                        "last_position_rate": sum(r["discard_position"] == "41" for r in usable) / len(usable) if usable else None})
    return out


def main():
    manifest = json.loads((ROOT / "evidence/manifest.json").read_text())
    for item in manifest["files"]:
        assert hashlib.sha256((ROOT / item["export"]).read_bytes()).hexdigest() == item["export_sha256"], item["export"]
        assert len(read(Path(item["export"]).name)) == item["rows"]
    baseline_rows = read("baseline.csv")
    baseline, diag = filter_votes(baseline_rows)
    baseline_result = estimate(baseline, "triz")
    baseline_result["diagnostics"] = diag
    baseline_result["by_generator"] = {m: estimate([r for r in baseline if r["gen_model"] == m], "triz")
        for m in sorted({r["gen_model"] for r in baseline})}
    contrasts = []
    diagnostics = {}
    for filename, label in [("factorial.csv", "Gemini"), ("specialist.csv", "Jev")]:
        kept, diagnostics[label] = filter_votes(read(filename))
        for treat, base, name in COMPARISONS:
            rows = [r for r in kept if r["pair_id"].endswith(f"{treat}_vs_{base}")]
            if rows:
                all_valid = [r for r in read(filename) if valid(r) and family(r["judge_model"]) != family(r["gen_model"]) and r["pair_id"].endswith(f"{treat}_vs_{base}")]
                contrasts.append({"judge": label, "treatment": treat, "baseline": base, "name": name,
                                  **estimate(rows, treat), "unfiltered_order_p": sum(r["picked_arm"] == treat for r in all_valid) / len(all_valid)})
    costs = []
    for mode in sorted({r["mode"] for r in read("tokens.csv")}):
        rows = [r for r in read("tokens.csv") if r["mode"] == mode]
        for r in rows:
            assert int(r["prompt_tokens"]) + int(r["output_tokens"]) == int(r["total_tokens"])
        costs.append({"mode": mode, "calls": len(rows), "cases": len({r["case_id"] for r in rows}),
                      "mean_tokens": sum(int(r["total_tokens"]) for r in rows) / len(rows)})
    result = {"bootstrap": {"unit": "case", "replicates": 10000, "seed": 20261027, "estimand": "vote-weighted preference conditional on cross-family, order-consistent votes"},
              "baseline": baseline_result, "contrasts": contrasts, "factorial_diagnostics": diagnostics,
              "selection": selection_results(read("selection.csv"), read("same_order.csv")), "cost": costs}
    (ROOT / "results/summary.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["# Results", "", "Rebuild: `python scripts/analyze.py`. All intervals below resample cases (10,000 draws).", "",
             "| Contrast | Judge | Cases | Votes | Preference | 95% CI |", "|---|---|---:|---:|---:|---:|"]
    for r in [{**baseline_result, "name": "TRIZ vs empty control (baseline)", "judge": "4-model jury"}] + contrasts:
        lines.append(f"| {r['name']} | {r['judge']} | {r['cases']} | {r['votes']} | {r['p']:.1%} | [{r['ci_low']:.1%}, {r['ci_high']:.1%}] |")
    lines += ["", "The baseline and follow-up reuse problems. Cases, rather than votes, are the resampling unit. Wide intervals leave the controlled TRIZ effect unresolved.", "",
              "Selection results and token counts: [summary.json](summary.json). Selection rates describe overlapping candidate sets from one problem."]
    (ROOT / "results/RESULTS.md").write_text("\n".join(lines) + "\n")
    print("Verified hashes; rebuilt results/summary.json and results/RESULTS.md")


if __name__ == "__main__":
    main()
