# Retrieval evaluation boundaries

Owner task, 2026-10-08: the existing 25 development cases and conditional 31-step
optimization are authorized after the specified scorer/runtime prechecks. This
supersedes the preparation-only scope below; original gold/references remain
immutable. Current execution is blocked before phase A by the Qwen embedding
runtime probe. See `RETRIEVAL_OPTIMIZATION.md` and the preflight report. Holdout,
production changes and answer generation remain excluded.

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
