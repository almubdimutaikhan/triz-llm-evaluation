# Results

Rebuild: `python scripts/analyze.py`. All intervals below resample cases (10,000 draws).

| Contrast | Judge | Cases | Votes | Preference | 95% CI |
|---|---|---:|---:|---:|---:|
| TRIZ vs empty control (baseline) | 4-model jury | 45 | 1723 | 68.1% | [62.5%, 73.3%] |
| TRIZ content / long prompts | Gemini | 39 | 75 | 52.0% | [39.4%, 64.3%] |
| TRIZ mention / short prompts | Gemini | 39 | 80 | 57.5% | [45.1%, 69.4%] |
| Generic structure / no TRIZ | Gemini | 40 | 86 | 48.8% | [38.7%, 58.5%] |
| Long vs short / TRIZ on | Gemini | 39 | 89 | 49.4% | [39.5%, 58.7%] |
| TRIZ content / long prompts | Jev | 33 | 78 | 60.3% | [50.0%, 70.7%] |
| TRIZ mention / short prompts | Jev | 37 | 88 | 50.0% | [39.5%, 60.2%] |

The baseline and follow-up reuse problems. Cases, rather than votes, are the resampling unit. Wide intervals leave the controlled TRIZ effect unresolved.

Selection results and token counts: [summary.json](summary.json). Selection rates describe overlapping candidate sets from one problem.
