# Method

This release reanalyzes existing experiments. It makes no new model calls.

| Track | Completed evidence | Question |
|---|---|---|
| Baseline | 45 problems; 5 generators; 4 judge models × 2 personas; 6,768 judgement rows | Does the full TRIZ prompt beat an empty system prompt? |
| Controlled follow-up | 40 problems; 4 generators; 4 conditions; 640 generations; 1,280 Gemini judgement rows | What survives control for generic structure and prompt length? |
| Specialist sensitivity | Same generations; 640 Jev judgement rows; two TRIZ contrasts | Does the result depend on the evaluator? |
| Selection reliability | 15 overlapping 41-candidate slates per model, from one problem; 240 shuffled-call records and 90 fixed-order comparison records | Does reordering candidates change removal? |
| Token analysis | The same 640 factorial generations | How much text-token usage accompanies each condition? |

The factorial conditions are long TRIZ, long generic design, short TRIZ mention, and short generic instruction. The generic long prompt follows a similar structure to the TRIZ prompt. This is an approximate design control, not exact token matching: output lengths differ, and the prompts differ in more than a single keyword. The baseline and factorial follow-up reuse problems and are not independent replications.

All 640 factorial cache records specify `temperature=0.0`, `max_tokens=4000`, with one sample per cell. Temperature zero does not guarantee repeatable hosted-model outputs. Generator models are GPT-4o, Claude Sonnet 4.5, DeepSeek Chat V3.1, and Gemini 2.5 Flash. The baseline additionally includes a locally run CrPO-Llama-3.1-8B generator; its archived protocol reports two samples at temperature 0.8. Model/provider and sampling differences prevent treating a change between tracks as a paired causal effect.

Generation uses stateless requests. Across conditions, problem text and user-task instructions stay fixed; only the system prompt varies. Gold solutions and labels are metadata, excluded from generation prompts. Judges see the extracted `FINAL SOLUTION` rather than the model's TRIZ analysis, with model/condition labels hidden. Pair construction filters missing, truncated, short, and jargon-leaking answers. These are properties of the upstream protocol; the released metadata cannot independently establish absence of semantic leakage or memorization.

For the primary preference estimate, we:

1. Reject errors and malformed or inconsistent pick mappings.
2. Exclude judgements from the generator's own provider/model family, including DeepSeek aliases.
3. Require exactly two records, with opposite answer mappings and the same chosen arm.
4. Collapse these two records to one vote.
5. Resample whole cases 10,000 times (seed `20261027`), retaining every vote in each sampled case. Report the vote-weighted preference and percentile 95% interval.

The estimand is **preference conditional on surviving these filters**. Cases with more retained votes have more weight. `summary.json` also reports case-balanced point estimates and factorial preference before the order-consistency filter. Filtering may favor easy or decisive comparisons; it does not remove all evaluation bias. Retention is 63.8% for the baseline's eligible vote groups, 68.8% for Gemini's factorial groups, and 51.9% for Jev's.

For selection, compare the discarded candidate ID across two calls. Only parseable removals that map to a presented candidate count. A bare parsed discard is accepted even when the full ranking is unavailable. Failed calls are never agreements. Fixed-order repeat and independent-shuffle results are separate comparisons on the same slate sample. Slates share candidates; no across-task confidence interval is claimed. The `1/41` reference assumes independent uniform choices and is not a fitted chance model.

Token counts apply `cl100k_base` to system text, user text, and output text. They exclude provider chat wrappers and hidden reasoning tokens. This is a consistent ruler, not native tokenization, API billing, or measured dollar cost.

Wide intervals, a single general-purpose factorial judge, correlated model families, possible benchmark familiarity, and the one-problem selection study limit generalization. No human validation or downstream agent-task improvement is established by this release.
