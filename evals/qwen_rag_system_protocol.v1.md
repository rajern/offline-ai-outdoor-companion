# M2-06 local Qwen/RAG system baseline v1

Owner authorization: 2026-10-11. Freeze this protocol and all inputs before the
first generated answer. This is agent source review, not independent clinical
validation. No retrieval tuning, prompt tuning, gold changes or safety policy.

Candidate: existing MiniLM full-body window T-ranking, k16, no threshold,
original P3. Reuse the 25 saved contexts and frozen window index. Recompute only
the application query/ranking/packing for equality and end-to-end measurement;
any different delivered text or over-budget prompt stops the baseline.
Three corpus-gap cases (14,15,25) are reported separately from 22 supported cases.
Use the unchanged application prompt, Qwen3.5-2B Q4_K_M, 4,096 runtime context,
256 output tokens, temperature .2, top-p .8, top-k20, reasoning off, 120s timeout.
No new seed is supplied: the existing sampling settings are retained; one answer
per input cannot estimate sampling variance.

For every generated answer, read the question, actual context and unchanged
must-have requirements. Record each requirement as full / partial / absent /
uncertain in the answer, independently of retrieval coverage. Full means every
condition and sub-action is stated or follows unambiguously from the answer.
No credit for facts present only in retrieved sources. Record whether each
assertion is supported by delivered passage IDs; correct but unsupported model
knowledge still fails grounding. Preserve retrieval and answer scores separately.
Do not manufacture a weighted score, acceptance percentage or automatic winner.

Record separate dimensions: unsupported factual/actionable additions; concrete
wrong-action risk (existing V3 scope rules); irrelevant advice; direct conflict;
wrong-country instructions; short/clear Norwegian; acknowledgement of missing
information; and unresolved review findings. Flag precise answer spans and
passage IDs, and explain applicability. Omission alone is not a misleading flag.
Case16's historical scope/risk dispute remains requires_review unless the actual
source review resolves it. Evaluate new answer behavior separately from this
historical retrieval classification.

Classify every missing or problematic requirement: retrieval (absent delivered
support), generation (support delivered but omitted/misused), corpus (known absent
approved support), or prompt/constraints. More than one cause may apply. The
three-point instruction can constrain content without a hard token cutoff; only
attribute definite token truncation when runtime output proves it. Output token
count near 256 alone does not prove truncation.

After reviewing the baseline, at most three representative failures may receive
one diagnostic answer each with manually checked sufficient passages from the
same approved corpus, within the same prompt and output limits. Bind diagnostic
passage IDs and hashes before each call; never merge these into baseline results.
These tests diagnose missing context versus generation, not retrieval variants.

Run sequentially. Keep the actual local embedding model resident while Qwen is
active. Sample parent plus child RSS and host available RAM every .1s; stop and
retain artifacts on >4 GiB process-tree RSS or <256 MiB available RAM. Retain raw
command/stdout/stderr, exact prompt and input identity, timings and sampled CPU.
Cache by complete prompt, model/runtime/settings and relevant code hashes; reuse
only successful sealed identical calls. Never silently retry a stopped call.
Python network calls are denied during testing; local files and explicit GGUF
CLI are used. Record whether OS network disconnection was actually tested.

API response sources must equal stored metadata for delivered contexts, be
deduplicated by publisher/URL, and never come from generated citations. Verify
frontend display fields by code inspection; distinguish this from an interactive
browser review. Current production defaults remain unchanged.

Finish with all 25 rows (or an explicit technical stop), supported22 and original15
slices, gap behavior, examples, attribution, resource/latency statistics and
prioritized follow-up work. No new Codex judge calls are needed. M2-06 stays open
for owner manual quality approval; no holdout, production replacement or M3.
