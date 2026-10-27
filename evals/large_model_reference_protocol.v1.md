# GPT-6.1 Sol reference, 2026-10-25

Owner explicitly authorized the proposed comparison: eight GPT-6.1 Sol High
answers through existing Codex/ChatGPT subscription, followed by the unchanged
Sol Medium evaluator and source review. This supersedes earlier stops only for
this reference. No paid API, reset credits, retrieval, local regeneration, new
sources/models/prompts, full25, holdout, production or M3.

Use original baseline system prompt, exact saved user message, questions and
source order for19,05,08,17,21,23,15,25. One independent ephemeral CLI session per
answer; no history, tools, web, repository instructions, rubric, expected answer,
judge results or source selection based on gold. Pass original system text as
model_instructions_file (replacement base instructions), exact user text on
stdin. Same verified CLI and isolated flags as the existing judge; remove only
the judge's output-schema option and request High rather than Medium. Preserve
exact command/stdin/instructions/raw JSONL, model/CLI identities, usage and times.

This is a practical strong reference, not an isolated model-size experiment:
Codex model wrapper, High reasoning and sampling differ from local thinking-off.
No seed, temperature or512-token cap is requested through unsupported options.
Do not truncate final text. Record words/bytes and usage; reported output usage
may include hidden reasoning and is not a verified count of final-answer tokens.
Server model revision and full hidden system scaffolding are not independently
exposed. Original application prompt/source messages remain byte-bound.

Freeze all eight inputs, code/protocol, evaluator assets, parent closeout and
progress snapshots before any call. Reuse latest16 local baseline judgments and
the32 improvement answers/judgments unchanged, and the identical passed Medium
control. No baseline regrading. Generate all eight before freezing eight separate
one-answer anonymous judge inputs. Medium prompt/schema/rubric unchanged; each
judge starts fresh and sees no model label or generator reasoning. One-answer
grouping versus old groups up to3/4 is a limitation. Same model family as generator
and judge can favor style; source review is required, not independent clinical gold.

At most8 generation and8 judge calls, sequential under the existing kernel lock.
Timeout1200s per call; unchanged local client guards4GiB process-tree RSS and
256MiB host reserve, sampled0.1s. These measure client cost, not cloud inference
RAM/energy. Use proven host CLI transport with read-only/no-tools child. Save
intent before dispatch and raw streams before validation. Technical/resource/
quota/access failure stops; preserve incomplete output, no automatic retry or
parameter relaxation. Reconcile completed output before any separately reviewed
technical continuation. Stop at real subscription limits; never switch billing.

Report core15, retention intersecting13 fully delivered requirements, conditional
criteria, supported full coverage and two gap behaviors separately. Review all8
texts, actual source packs and new decisions/findings; no raw score edits. Higher
coverage alone does not establish safer advice. Compare practical gaps/regressions,
preserve uncertainty and do not infer a small-model ceiling or product readiness.
Snapshot TASKS.md/evals/AGENTS.md before their allowed progress updates. Preserve
all earlier raw/code/closeout artifacts and document final results, then stop.

Transport documentation checked: [non-interactive CLI](https://learn.chatgpt.com/docs/non-interactive-mode)
and [replacement instructions](https://learn.chatgpt.com/docs/config-file/config-reference).
