# Saved retrieval re-assessment v1

Authorized 2026-10-25 as steps 1 and 2 of the owner's agreed plan. Freeze all
definitions, authored controls, model/profile, code, schema, prompt, provenance
and inputs before any evaluator call. Keep old experiments and scores unchanged.

## Scope and inputs

Use exactly the 25 primary context groups in the completed answer-rubric run,
`knowledge/local/diagnostics/answer-rubric-revision-v1-2026-10-24/continuation-v1/`.
These are the actual delivered contexts of the historical Qwen baseline and
match its T-ranking/P3 contexts. Do not rerun searches, tokenizers or local models.
Do not assess all 31 former configurations or the three diagnostic contexts.
Read no holdout. No new source text is added to the public repository.

Evaluator inputs omit all generated answers, model/configuration names, old
scores and historical rubric text. Include only question, jurisdiction, declared
corpus limitations, revised required/conditional criteria, optional information,
case noise guidance and the exact numbered delivered blocks. Their content/order
must match saved product inputs. Source IDs preserve provenance, not authority
for a claim absent from actual text.

## Scoring contract

Each required or conditional criterion receives full / partial / absent /
uncertain. Full requires applicable evidence for every necessary component.
Partial requires an independently correct part, exact evidence and named missing
components; a keyword attached to a wrong action or decisive condition is not
partial coverage. Uncertainty is genuine scope/meaning doubt, not ordinary absence.
Quotes may be combined across blocks. Question facts establish applicability and
references, but neither question nor criterion text supplies missing source advice.

The main numerator is full required criteria on supported cases, denominator63.
Partial, absent and uncertain are separate; unknowns remain in the denominator.
Report confirmed coverage and an uncertainty bound, never call the bound a score.
Average per-case coverage and all-core-covered case counts stay separate.
Conditional branch availability is an inventory, not a dynamically changed main
denominator. No applicability decision depends on generated answers.

Relevant optional content is not noise just because it earns no core points.
Inspect substantive passages for irrelevance, potentially misleading applicability,
direct conflict, wrong-country operational/legal information and unresolved source
limitations. Preserve clearly labelled other-scenario scope: off-topic material
alone is not an applicable conflict. Repetition/navigation alone earns no noise flag.
Full coverage can coexist with conflicting additional text; flag that separately.
The known cream ambiguity in case07 stays outside core coverage and is recorded
as unresolved source limitation, not clinically adjudicated or used to change gold.
This separate limitation record supersedes only the old retrieval prompt's blanket
suppression of that known ambiguity; no historical risk label is edited.

## Preflight and controls

Use the existing subscription-authenticated CLI and frozen command builder.
No API fallback, paid API or reset credits. Keep 4GiB own process-tree RSS and
256MiB host reserve; one judge at a time under the existing OS lock. New call
timeout1200s, no truncation, no automatic retry after a dispatched failed attempt.
Raw logs, exact serialized stdin, schema/instructions, command, hashes, resources,
usage and requested model/effort are saved. Actual server revision is unknown.

Before the main25, run three source-bound authored controls, with seven criteria:
complete/multi-span evidence, one permitted alternative, partial information,
absence, universal warning covering the given instance, wrong-scenario matching,
and full coverage alongside an explicit conflicting instruction. Control labels
and required/forbidden flag types are frozen before inference. These are synthetic
author checks, not clinical gold or a broad error-rate calibration.
All controls must pass, with valid exact quotes and no critical false-positive
coverage, before main scoring. A failure stops main dispatch. Preserve and diagnose
any stop; no score-driven change of expected labels. A necessary technical repair
must use a separately documented adapter/version retaining the original attempt.

At most28 successful dispatches: three controls then25 primary contexts. No
parallel judges. Reuse completed exact-bound records; inspect unsealed streams for
complete recoverable output before any further action. A dispatched failure is a
stop, not an invitation to retry. Stop on access/quota/resource/validation barriers.

## Review, comparison and preservation

Review each main criterion decision against its actual sources, with extra
attention to negatives, partials, uncertainty, critical conditions and full-case
claims. Review all risk findings and the known source-limit cases. Preserve raw
judgments; document any proposed correction as an exact-input-bound review layer.
Do not silently change rubric or raw scores. Report unresolved interpretations;
no automatic production selection follows from confirmed development coverage.

Match raw new retrieval decisions with the already sealed Medium answer decisions
per case/criterion. Compute source-conditioned retention by set intersection.
Report full25 historical-Qwen and matched-screen8 model slices separately; the
three diagnostic contexts were not re-scored and are not assigned new retention.
Retain case-level old72/new63 tables to distinguish definition changes from search
changes. The old60/72 is historical, not evidence of a new technical improvement.

Parent freeze, raw call seals and immutable closeout artifacts are verified. Only
TASKS.md and evals/AGENTS.md are permitted to change as progress documentation;
their pre-task contents are saved. Backend, source data, old rubrics/prompts,
answer judgments, previous reports, controls and holdout stay untouched.

Finish with a readable report, machine-readable per-criterion counts/retention,
review notes, offline integrity checks and exact limitations. Complete this task
only; do not start the local improvement round or GPT generation comparison.
