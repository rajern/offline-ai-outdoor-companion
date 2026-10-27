# Answer-rubric revision and Medium/High comparison v1

Owner authorization: 2026-10-24, side conversation: execute the complete proposed
review, preserve history, assess saved answers with Sol Medium and then High.
No additional owner review of the rubric is required for this evaluation.
This is a retrospective development evaluation, not a final safety-policy or
clinical approval. Production, retrieval, source corpus, historical gold and
holdout remain unchanged. No local answer generation or paid API is authorized.

## Question and design

Review the definitions of all 25 development cases. Assess all 50 already saved
answers: historical Qwen 25 + three sufficient-context diagnostics, and the
22 screening answers. Main, screening and sufficient-context slices stay separate.
Use the historical and revised criteria in each assessment so that rubric effects
can be compared within the same judge setting. Then change only requested
reasoning effort: gpt-6.1-sol medium, followed by gpt-6.1-sol high. ChatGPT-authenticated
Codex CLI, isolated ephemeral sessions, no tools or repository access for graders.

One input groups anonymous answers to the SAME question and SAME delivered context.
Each answer is assessed independently, with no ranking or preferred winner. Grouping
reduces repeated context tokens. Both rubric versions and multiple answers within
one call can influence interpretation; this design is paired, not independently
randomized. Identical group/answer/criterion order is used at both efforts.
Anonymization hides model labels, not all stylistic clues.

## Criteria construction

For every historical requirement record its exact text, proposed classification,
source provenance, omission consequence, permitted semantic alternatives, displaced
explanatory components, reviewer and uncertainty. Sources establish factual support;
necessity is a separate author judgment. Read the source corpus, not just retrieval
outputs. Do not infer clinical consensus from source quotes or agent agreement.

- Required: omitting it leaves a material part of the question unanswered or removes
  an action/qualification needed to use the answer correctly.
- Conditional: needed only when its declared branch applies; inactive criteria do
  not enter core coverage. Active conditional failures are reported separately.
- Optional: helpful explanation/repetition, without a demonstrated omission
  consequence for the immediate question. Optional facts never compensate for a
  missing required or active conditional item.
- Safety significance is independent of category. Uncertain safety significance
  remains explicitly review-needed. No unsupported clinical minimum is certified.

Accept equivalent meaning, unambiguous contextual reference and source-supported
alternative routes. Examples are examples, not mandatory exhaustive lists. Do not
require repeating facts already supplied by the user. Preserve actions together
with their decisive conditions, timing, numbers, negation and jurisdiction.

Full / partial / absent / uncertain are retained. Calling 113 for help satisfies
revised calling criteria without a separate declaration that the operator guides.
That historical conjunct still applies when scoring the HISTORICAL rubric.
Repeated symptom descriptions and causal explanations are not automatically
required. A generic safety slogan does not substitute for a concrete procedure.

## Controls and freeze

The author has already seen outputs: record retrospective bias; do not claim an
independent test. Use source-bound synthetic positive, omission, wrong-negation,
scope and equivalent-wording controls. These are author controls, not expert gold.
Freeze scripts, rubric, prompt, schema, input groups, controls and old artifacts
before first judge call. Run controls before main scoring at each effort. Stop on
structural/provenance failures or a confirmed critical false-positive control.
Do not tune the prompt between Medium and High. Any repair after a dispatched
call must retain original outputs and receive a separate lineage record.

## Execution and audit

Record exact stdin, instructions, output schema, command, CLI identity/hash,
requested model/effort, source/answer hashes, timestamps, raw JSONL/stdout/stderr,
usage, latency, output, validation and cache identity. Remove API credentials from
child environment; never read project .env. Verify actual CLI capability locally.
No automatic retry of dispatched/unsealed/failed calls. Recover completed raw
outputs without inference. Preserve a durable intent before every call and use
the existing global OS judge lock. Only one worker; all Medium calls precede High.
Sample own process-tree RSS and host memory under historical 4 GiB /256 MiB guards.
Do not consume account reset credits. Stop on quota or an unavailable exact model.
Neither reasoning effort nor actual server revision is independently observable
unless the CLI exposes them; document this limit rather than invent confirmation.

Public files contain authored criteria, decision metadata and aggregates only.
Raw source-bearing inputs, evidence quotations and logs remain ignored locally.
Do not overwrite old records or implicitly resume model-product work/M3.

## Analysis

Report required-item coverage with fixed per-case denominators; partial separately.
Report conditional, unsafe additions, critical omissions, grounding, abstention and
unresolved review separately. Never combine different rubric denominators into a
percentage-point model improvement. Compare old/new within Medium and within High;
then compare efforts within the same rubric. Historical agent review is a third,
different assessor, not a controlled Medium baseline.

Review EVERY Medium/High disagreement against exact answer, applicable sources and
frozen rule, blind to effort where practical. Also inspect agreed high-consequence
cases and report control errors, quote/provenance errors, uncertainty, latency and
tokens. A higher score is not a better judge. No independent clinical accuracy or
robustness estimate follows from one call per input and agent adjudication.

## Research rationale (read 2026-10-24)

- HealthBench (2025), sections 4.3 and 5: physician-written situation-specific
  criteria, consensus controls for critical themes, appropriate response depth.
  https://cdn.openai.com/pdf/bd7a39d5-9e9f-47b3-903c-8b847ca650c7/healthbench_paper.pdf
- Published HealthBench grader: illustrative examples need not all be repeated;
  all genuinely required conjuncts still apply. Its weights/clinical gold are NOT
  copied into Outwise. https://github.com/openai/simple-evals/blob/main/healthbench_eval.py
- RAGChecker (2024): distinguish missing claims, factual precision and contextual
  support. This does not establish which facts are necessary for an Outwise user.
  https://arxiv.org/abs/2408.08067
- NICE NG197 (2021), 1.2.7-1.2.11: prioritize needs and manageable information.
  Communication guidance, not an LLM benchmark or emergency-procedure validation.
  https://www.nice.org.uk/guidance/NG197/chapter/recommendations

This file authorizes no new source ingestion; research informs evaluation method.
