# Sources and credits

| Source | Use in this repo |
|---|---|
| [TRIZ-2AFC](https://github.com/almubdimutaikhan/triz-2afc-agent-framework) | My baseline and factorial experiments: generation protocol, blind judging, and decision records. |
| [BVSR](https://github.com/almubdimutaikhan/bvrs-llm-creativity) | My candidate-selection and repeatability experiments. |
| Local `triz-cost-efficiency` snapshot | Token counts for the 640 factorial generations. |
| [Wang & Uzzi (2026), TRIZBench](https://aclanthology.org/2026.findings-acl.1798/) · [data](https://github.com/ellenzhuwang/trizbench) | Source of the patent-derived problems. Its benchmark measures contradiction prediction, principle prediction, and grounded reasoning; this study measures creativity preference. |
| [Zheng et al. (2023), Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) | Prior work on position, verbosity, and self-enhancement bias in model judges. |
| [IM-LLM](https://github.com/orioli/IM-LLM) | Related work on product-graph context and ideation efficiency. The coauthored manuscript credits Almubdi Muitakan, Maria Tsakalerou, Marc Magrans de Abril, and Jose Berengueres. Its results are separate from the TRIZ experiments. |
| Altshuller (1997), *40 Principles: TRIZ Keys to Technical Innovation* | Background for the TRIZ treatment. |

Repo author and maintainer: **Almubdi Mutaikhan**. Exact source snapshots and file hashes are recorded in the [manifest](../evidence/manifest.json); some source files were uncommitted when exported. Original benchmark text, generated answers, and principle descriptions are excluded from this release.

The companion [LLM judge reliability](https://github.com/almubdimutaikhan/llm-judge-reliability) repo examines the judge–generator interaction and creative-selection follow-ups. Shared records are identified there; they are not additional replications.
