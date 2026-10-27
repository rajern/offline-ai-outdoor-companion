# Bounded generation improvement v1

Owner authorization 2026-10-25: "ok kjør og gjennomfør det takk", after the
explicit 32-answer plan. This task supersedes earlier stops only for this run.
No new retrieval, sources, models, quantizations, runtime upgrade, production,
M3, GPT product-answer comparison, full25, repeats, combined A+B or length trial.

Two models, unchanged files/runtime/native templates: Qwen3.5-2B Q4_K_M and
Gemma 4 E2B official QAT Q4_0. Same eight saved questions and exact source bytes
in order19,05,08,17,21,23,15,25. Baseline is the latest16 saved answers, not old
full25. Reuse their raw Medium assessments; no baseline regeneration/regrading.

A changes only the sampling profile; same v1 system and user messages/tokens.
B changes only the system prompt to the exact first text block in the research
proposal v1; same user text and old sampler. Each uses 512 output, seed42,
4096 slot, <=3200 native input, no truncation/shift, thinking off, CPU and one
server slot. Qwen A: T1,p1,k20,min_p0,presence2,repeat1. Gemma A: T1,p.95,k64,
min_p0,presence0,repeat1. Other sampler fields, chain and repeat_last_n64 are
explicitly pinned from the old effective settings; compare returned settings.
Gemma's min_p0 and unchanged penalties are experimental choices, not Google claims.

Freeze definitions, code, metadata and model/runtime identities before preflight.
Preflight all32 native inputs for both models BEFORE any completion; verify A's
exact tokens equal baseline and B changes only system content. Then seal complete
runtime/input freeze before responses. MiniLM remains resident without queries
through loading, preflight and generation. Models/answers execute sequentially;
Qwen A then B, Gemma B then A, fixed case order within each. Record runtime and
resource costs without claiming warm-server order is a causal speed comparison.

Use existing guards unchanged: combined process-tree RSS<=4GiB, host reserve
>=256MiB sampled .1s, load<=120s, each completion<=120s. Loopback-only explicit
local models and Python network denial; do not claim OS disconnection. Resource
or technical failure stops; no automatic retries, limit relaxation or silent
response replacement. Save dispatch marker and raw response BEFORE validation.
Recover a completed raw response after a technical stop only via a documented
separate adapter; never repeat an unsealed dispatched completion automatically.

Assess with unchanged answer rubric v1, judge prompt/schema and requested Sol
Medium. Preserve old/revised fields because they are part of the locked judge
format; main comparisons use revised core15 and criterion-aligned available13.
Conditional requirements and two gap behaviors are separate. A full criterion
can coexist with wrong additions; critical findings override a coverage ranking.

The same-case four NEW answers are anonymized in eight sequential judge calls,
each assessed independently, not ranked. IDs/order are randomized with a fixed
pre-answer seed. Baseline scores remain the prior sealed raw Medium judgments;
batch size4 versus prior up-to3 is a limitation. Reuse the identical sealed
equipment control only after prompt/schema/CLI/input and success are verified.
Do not spend a call repeating an identical control. Bind exact judge inputs,
stdin bytes, prompt/schema/CLI hashes before dispatch. Judge timeout1200s follows
the previous documented successful continuation; no parallel judges/tools/web.
Record raw streams, model/effort request, usage, elapsed time and resources.
Server model revision is not independently exposed. Stop at a real quota/access
block; no paid API or reset credits. Host permission may be used for the proven
CLI transport, with the child retaining isolated read-only/no-tools settings.

Review all32 answers/findings against actual source blocks and frozen rubric;
retain raw judgments and document disagreement separately. No post-result rubric
or prompt edits, weights, cherry-picked retries or new pass percentage. Measure
full/partial/absent, criterion intersection retention, unsupported/conflict/
critical omission flags, conditional completeness, gaps, limit stops, time and
RAM. A single sample on selected development questions is not general quality
or stability evidence. A/B interaction is unmeasured, so a negative B does not
exclude usefulness with A settings. No autonomous production winner or safety
policy. Report changes, regressions and uncertainties, then stop.

Preserve prior closeout manifests, source/input/code/raw artifacts and public
scores. TASKS.md and evals/AGENTS.md alone may receive progress updates; snapshot
their original bytes and normalize slash identity in preservation checks. No
holdout read/search. New results use separate private storage and public names.
