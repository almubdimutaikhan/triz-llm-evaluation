# Released evidence

Metadata only: no problem stems, gold solutions, generated answer text, judge explanations, private correspondence, credentials, or third-party principle descriptions.

| File | Rows | Grain |
|---|---:|---|
| `baseline.csv` | 6,768 | One judgement presentation; includes errors |
| `factorial.csv` | 1,280 | One factorial Gemini judgement presentation |
| `specialist.csv` | 640 | One factorial Jev judgement presentation |
| `selection.csv` | 240 | One shuffled 41-candidate rank/batch-score call, including failures |
| `same_order.csv` | 90 | One fixed-order repeat comparison |
| `tokens.csv` | 640 | One factorial generation, counted with `cl100k_base` |

`pair_id` joins the two answer orders. `case_id` is the bootstrap cluster. `a_arm`, `b_arm`, `pick`, and `picked_arm` permit mapping verification. `gen_model` and `judge_model` permit family exclusion. `error` records failed judgements. Selection rows retain presentation order, discard ID/position, parser status, and token counts; no candidate content is included. `same_order.csv` stores both discarded IDs rather than requiring trust in a precomputed agreement flag. Empty fields mean missing/unavailable, never a successful choice.

Model IDs and case IDs are preserved as logged, including aliases. Numeric outcomes and these identifiers support analysis replication, but cannot reconstruct or independently validate generation, problem sampling, semantic blinding, or the full original prompts. Candidate descriptions and restricted-source problem statements remain outside this release.

`manifest.json` pins the source files and exported CSVs by SHA-256. It also fingerprints each of the 640 generation cache records and system prompts without publishing their contents. Source working-tree modifications are disclosed. The included export hashes are checked by `scripts/analyze.py`.

To rebuild this export from the original local working snapshots:

```bash
python scripts/import_evidence.py \
  --source /path/to/triz-on-vs-off-agent \
  --selection /path/to/bvsr-llm-creativity \
  --cost /path/to/triz-cost-efficiency
```

Those local snapshots include uncommitted/ignored evidence; cloning the public source repositories alone may not recover them. The included CSVs are the stable starting point for this release. They support the offline statistics and charts without external files.

The MIT license covers newly authored code in this repository. It does not grant rights to upstream datasets, model text, books, source repositories, or the coauthored manuscript. Metadata is supplied as a research record with provenance; no blanket license to upstream material is asserted. Consult source terms before reconstructing or redistributing original texts.
