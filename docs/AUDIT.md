# Analysis checks and corrections

Snapshot: **27 October 2026**. The [manifest](../evidence/manifest.json) identifies source files and exported CSVs by SHA-256. It also records Git HEADs and uncommitted changes.

| Issue in earlier material | Resolution here |
|---|---|
| Folder name `factorial_129` | The completed table contains **40** cases and **640** generations. The folder name refers to the planned sample. |
| Baseline report excludes only identical judge/generator model strings | `deepseek/deepseek-v3.1` and `deepseek/deepseek-chat-v3.1` are the same family. Both are excluded from judging one another. |
| Main v2 reports 68.2%, 1,841 votes | Correct family exclusion retains **1,723** votes: **68.1% [62.5%, 73.3%]**. Original intervals also used a different bootstrap RNG state. |
| Old factorial reports and cost tables disagree | Use the explicitly versioned `judgements_v2_gemini.csv`, not a narrative summary. Report the vote-weighted estimand consistently; case-balanced points remain in JSON. |
| Headline patent result: 72.2% on 84 cases | The available patent CSV now has only **32 rows from one case**, and its full cache is absent. The historical result is **not reverified or used** here. |
| Repeated judgements of the same problem | Bootstrap by case. The baseline and follow-up reuse problems. |
| Model naming differs across selection write-ups | Preserve the literal logged ID `anthropic/claude-sonnet-5`; display “Claude Sonnet” with a footnote. The underlying vendor/version identity is not independently verified. |
| GPT-4o often fails the 41-candidate task | Only 2 complete shuffled pairs remain per condition. Exclude it from the main reliability plot; keep all failures and denominators in the evidence/JSON. |
| Token-count comparison | Uses the same factorial generations. Counts use a shared tokenizer and differ from provider billing. |

The generic-structure contrast is **48.8% [38.7%, 58.5%]**, leaving the cause of the earlier empty-control advantage unresolved. Factorial intervals are exploratory and unadjusted for multiple comparisons. Jev's long-prompt interval reaches 50% at the lower endpoint; larger effects remain compatible with the data.

The IM-LLM manuscript, **“AI brainstorming: Is less context more?”**, covers a separate product-graph study. Its experiments are excluded from the TRIZ sample.

The scripts check file hashes, row counts, 640 generation identities, pick-to-arm mappings, family exclusions, opposite-order pairs, failed calls, token arithmetic, and candidate positions. Regression tests cover family aliases, order flips, duplicate presentations, failed parses, and case-level resampling. Checking semantic blinding requires the original text.

All 640 input/output token totals were also independently recounted from the original cached text and matched exactly. With that source snapshot and `tiktoken==0.14.0`, repeat via `python scripts/verify_source_tokens.py --source /path/to/triz-on-vs-off-agent`.
