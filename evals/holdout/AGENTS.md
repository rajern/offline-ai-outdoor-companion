# Retrieval holdout access boundary

This directory contains owner-review material, NOT optimization inputs.
The author created these questions; this is a procedural, not secret holdout.

Future optimization agents MUST NOT open, search, summarize, copy, embed, run,
score or use `retrieval_control.v1.yaml`, its gold, or its evidence as tuning,
experiment-choice, debugging or interim-selection input. Do not glob this
directory or ingest the whole `evals` tree as agent context. A hash in the public
lock identifies contents without providing permission to read them.

Allowed now: authoring and source-only QA for this task, owner review.
Allowed later: one final evaluation AFTER the development configuration, code,
parameters, development results, scorer version and owner approval are frozen.
Owner approval of the proposal is not authorization to run the holdout.
Require explicit owner authorization of the final holdout run and a frozen
configuration record. The default evaluation loader refuses holdout access.
Keep holdout results out of optimization messages/working memory. If results
inform another selection/tuning cycle, mark this holdout consumed, report the
contamination and require a fresh control set; do not call it untouched again.

These rules cannot prevent arbitrary filesystem reads. Enforce read exclusion
in later agent/task setup or use an owner-controlled separate checkout if a
stronger boundary is required. Do not claim cryptographic secrecy or blinding.
