# Retrieval evaluation boundaries

Owner task, 2026-10-08: the existing 25 development cases and conditional 31-step
optimization are authorized after the specified scorer/runtime prechecks. This
supersedes the preparation-only scope below; original gold/references remain
immutable. Subsequent bounded diagnostics resolved the Qwen repeatability blocker
with explicit CPU isolation; see `qwen_embedding_stability_report.v1.md`. The
owner subsequently authorized resuming the existing 31 configurations after
technical/resource checks, without intermediate approvals. The resumed task
initially stopped before phase A at the available-RAM guard. After the owner freed
RAM, all three sequential resource/input probes passed with the original limits.
The 25 MiniLM contexts were preserved after a one-line correction for missing
source defaults; see `retrieval_optimization_serialization_correction.v1.json`.
Phase A completed all three configurations / 75 judgments. The integrity audit
passed without inference. Stage selection stopped on real per-item coverage and
safety tradeoffs; case 13 additionally needs semantic review. See
`retrieval_optimization_report.v3.md`. B/C are not run. Do not repeat A or modify
gold/judge based on results; obtain the owner's provisional model decision and
case 13 review before advancing. Finalist review remains unfinished. Holdout,
production changes and answer generation remain excluded.

Owner review task, 2026-10-09: the offline model-selection review is complete;
see `retrieval_embedding_selection_review.v1.md` and its evidence JSON. MiniLM
is recommended only as the experimental phase B candidate. Full breathing/CPR
support in case 08 and anaphylaxis support in case 17 are unreachable with its
frozen top-16/section rules. Case 13 Gemma risk and case 20 MiniLM coverage have
separate proposals in `retrieval_embedding_selection_adjudication.proposed.v1.json`;
they are NOT active scoring rules. Original judgments/gold/cache remain unchanged.
Do not treat the recommendation or proposals as the owner's decision. Stop here
until the owner selects the model and resolves the proposed adjudications; do not
repeat phase A or start B/C from this review alone.

Read `FOUNDATION.md` before future retrieval optimization. Default input is the
25-case development set, never the control set. Do not recursively read/search
`evals/holdout/` or include its files in optimizer context, calibration, debugging
or experiment selection. Its local AGENTS.md defines the final-run approval gate.
The holdout author knew its cases; these are process controls, not true blinding.

This preparation task authorizes source-only gold QA and scoring calibration on
ALREADY SAVED historical contexts, not fresh retrieval runs, model/parameter/
packing experiments or production changes. New cases/scorer are pending owner
approval. Unknown automatic decisions are not semantic failures and must not be
used to choose a winner. Preserve original 15 cases and historical outputs.

Development aggregate comparisons must also retain the unchanged legacy-15 slice;
do not compare a 25-case score with a historical 15-case score as if populations
were equal. Noise, jurisdiction and size remain separate from coverage.
