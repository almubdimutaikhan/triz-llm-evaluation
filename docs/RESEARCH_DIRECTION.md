# Next experiment: Kazakh and English

Do the same prompt and evaluation choices behave differently across languages?

My [Kazakh vocabulary-extension audit](https://github.com/almubdimutaikhan/kazakh-vocab-extension-audit) examines tokenization and model evaluation after language adaptation. This study raises a related question: whether a judge's preferences and sensitivity to candidate order transfer to Kazakh.

The proposed experiment would use engineering briefs in Kazakh and English, checked by bilingual speakers for equivalent meaning. Within each language, compare TRIZ with a structured generic prompt. Hold the task instructions fixed, generate in fresh contexts, and present each answer pair in both orders.

For candidate selection, repeat each call with the order fixed and then reshuffled. Compare model decisions with bilingual human judgements. Report preference, repeatability, excluded-vote rates, and token usage by language, with uncertainty calculated across problems.

This experiment has not been run. Before collecting results, fix the case set, primary outcome, target effect, and sample-size rationale. The current one-problem selection study provides a reason to test this across more problems.
