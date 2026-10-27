#!/usr/bin/env python3
"""Optional: independently recount tokens from original, non-redistributed caches.

Requires tiktoken==0.14.0 and access to the fingerprinted local source snapshot.
The public offline analysis does not require this script or the source text.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import tiktoken

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    a = p.parse_args()
    enc = tiktoken.get_encoding("cl100k_base")
    manifest = json.loads((ROOT / "evidence/manifest.json").read_text())
    fingerprints = {r["cache_id"]: r for r in manifest["generation_fingerprints"]}
    with (ROOT / "evidence/tokens.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        path = a.source / "data/factorial_129/generations" / (r["hash"] + ".json")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == fingerprints[r["hash"]]["sha256"]
        d = json.loads(path.read_text())
        prompt = sum(len(enc.encode(d[k], disallowed_special=())) for k in ("system", "user"))
        output = len(enc.encode(d["output"], disallowed_special=()))
        expected = tuple(int(r[k]) for k in ("prompt_tokens", "output_tokens", "total_tokens"))
        assert (prompt, output, prompt + output) == expected, r["hash"]
    print(f"Recounted {len(rows)} cached generation token totals: exact match.")


if __name__ == "__main__":
    main()
