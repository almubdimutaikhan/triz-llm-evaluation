#!/usr/bin/env python3
"""Export numeric/decision metadata only. Never exports prompts or candidate text."""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--selection", type=Path, required=True)
    p.add_argument("--cost", type=Path, required=True)
    a = p.parse_args()
    records = []
    def export(base, rel, dest, fields, predicate=lambda r: True):
        src = base / rel
        rows = [{k: r[k] for k in fields} for r in read(src) if predicate(r)]
        out = ROOT / "evidence" / dest
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        records.append({"source_project": base.name, "source_path": rel,
                        "source_sha256": sha(src), "export": "evidence/" + dest,
                        "export_sha256": sha(out), "rows": len(rows)})

    fields = "pair_id case_id gen_model judge_model persona order a_arm b_arm pick picked_arm error".split()
    export(a.source, "results/main/judgements.csv", "baseline.csv", fields)
    export(a.source, "results/factorial_129/judgements_v2_gemini.csv", "factorial.csv", fields)
    export(a.source, "results/factorial_129/judgements_jev.csv", "specialist.csv", fields)
    export(a.selection, "results/mitigation/calls.csv", "selection.csv",
           "set_id n condition judge shuffle presented_order parse_status discard_position discard_candidate_id prompt_tokens completion_tokens".split(),
           lambda r: r["n"] == "41" and r["condition"] in ("rank", "score_batch"))
    export(a.selection, "results/mitigation/determinism.csv", "same_order.csv",
           "set_id n condition judge rep0_discard rep1_discard same_discard rep0_status rep1_status".split())
    export(a.cost, "data/calls.csv", "tokens.csv",
           "hash case_id mode model sample_idx prompt_tokens output_tokens total_tokens".split())

    # Tie imported token counts to the exact cached factorial generations.
    token_rows = read(ROOT / "evidence/tokens.csv")
    generation_hashes = []
    for r in token_rows:
        src = a.source / "data/factorial_129/generations" / (r["hash"] + ".json")
        d = json.loads(src.read_text())
        assert d["case_id"] == r["case_id"] and d["model"] == r["model"] and d["mode"] == r["mode"]
        assert not d["error"] and d["output"]
        generation_hashes.append({"cache_id": r["hash"], "sha256": sha(src),
                                  "system_sha256": hashlib.sha256(d["system"].encode()).hexdigest(),
                                  "params": d["params"]})
    snapshots = []
    for base in (a.source, a.selection, a.cost):
        rev = subprocess.check_output(["git", "-C", str(base), "rev-parse", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "-C", str(base), "status", "--porcelain"], text=True))
        snapshots.append({"project": base.name, "head": rev, "working_tree_has_changes": dirty})
    manifest = {"snapshot_date": "2026-10-27", "files": records, "sources": snapshots,
                "generation_fingerprints": generation_hashes,
                "note": "File hashes identify the working snapshots; HEAD alone does not identify uncommitted evidence. Text is intentionally withheld."}
    (ROOT / "evidence/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Exported", sum(r["rows"] for r in records), "metadata rows; checked", len(generation_hashes), "generation identities.")


if __name__ == "__main__":
    main()
