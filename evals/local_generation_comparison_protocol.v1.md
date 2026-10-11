# M2-06 bounded local generation comparison v1

Owner authorization: 2026-10-11, including the later input-budget amendment.
Generation input <=3,200 actual model tokens INCLUDING native chat template,
BOS and control tokens; output reservation 512; configured runtime context 4,096.
Verify actual slot context and model training context before inference. Check
input + 512 against both; allow no source truncation or context shifting.
The retrieval packing budget remains its historical 2,000 locked tokens.

Three approved candidates only: existing Qwen3.5-2B Q4_K_M; Qwen3.5-4B Q4_K_M
from the original Qwen checkpoint, verified GGUF publisher; official Google
Gemma 4 E2B-it QAT Q4_0 GGUF. Do not silently substitute or upgrade runtime.
Models run sequentially, CPU only, native system/user chat template, thinking
disabled. Same system instructions in local_generation_prompt.v1.md, temperature
0.2, top-p 0.8, top-k 20, other sampler defaults documented from runtime.
Seed 42 for primary/diagnostic/paraphrase calls, seed 43 for repeats. This seed
choice is frozen before answers, shared across models, and differs from the old
unseeded baseline. It cannot isolate causality of prompt changes.

Use EXACT saved T-ranking/P3 source blocks and order for each question. No
retrieval, new passages or repacking. Baseline inputs are the 25 sealed system
test contexts; the three sufficient-context diagnostics use their sealed old
inputs, without changing sources. Finalist paraphrases keep their corresponding
original contexts, so these assess generation sensitivity, not retrieval.

Freeze all 36 input definitions, gold, protocols, implementation, model/runtime
hashes, settings, contextual identities and token sequences before the first
answer. Preflight uses --no-warmup and only health/props/apply-template/tokenize;
none generates a response. Verify native system/user serialization and effective
non-thinking assistant prefix; do not manually invent a chat template.

Stage one: eight primary cases in order 19,05,08,17,21,23,15,25 and three old
sufficient-context cases 03,08,17 per eligible model: <=33 new responses.
Compare saved old 2B responses without repeating them.
Stage two only for a promising finalist: remaining 17 original cases, four
paraphrases (03,08,17,21), four repeats (08,17,21,23), fixed before stage one.
<=25 additional responses, <=58 total. An excluded resource-incompatible model
reduces the count; no replacement or extra call. No automatic retries.

Assessment inherits qwen_rag_system_protocol.v1.md: full/partial/absent/uncertain
per unchanged requirement, every sub-action/condition needed for full. Record
assertion support in actually delivered source IDs, unsupported additions,
irrelevance, concrete misleading risk, direct conflict, geography, clear
Norwegian, explicit insufficiency, and unresolved review separately. Critical
omissions and errors in supported breathing/CPR, anaphylaxis and water treatment
override aggregate coverage. A source gap is not an excuse for inventing advice.
Known gaps 14,15,25 never get vacuous complete pass. Keep historical reviews,
gold and raw scores unchanged; agent review is not independent clinical review.

Finalist eligibility: no confirmed critical error or critical omission when
sufficient sources were supplied, correct safe abstention in both screened gaps,
materially improved source use, and all technical/resource checks passed. Uncertain
critical assessments block selection. If none qualifies, stop after stage one.
Select among eligible candidates by source fidelity, coverage and then resource
cost; no new weighted score or post-hoc percentage. The 54/60 target counts full
answer items intersected with the 60 historically covered retrieval items, not
all full answer items. Report 72-denominator coverage and supported22/legacy15
separately. Target also requires all three gaps correctly handled, no confirmed
critical failures and acceptable resources. It is a development target, never a
safety approval. Windows results do not establish mobile suitability.

Keep the real MiniLM embedder resident during runtime checks and generation.
Original Resources guard: host available >=256 MiB, relevant process-tree RSS
<=4 GiB, sampled every .1s. On breach stop, kill own server, preserve logs;
no automatic retry/relaxation. A candidate demonstrably incompatible with the
4 GiB limit can be excluded; a transient host-memory breach stops the run.
Server binds numeric loopback only, Python external sockets denied during tests,
explicit local models, no paid API. OS disconnection is not claimed.

Retain requests, native effective prompts, exact tokenizer IDs, actual counts,
response JSON, stop reason, timing, CPU/RAM and seals locally. Cache includes
prompt/tokens/model/runtime/settings/seed/code/protocol identities. Same-cache
reuse requires verified seals; a dispatched but unsealed response cannot retry.
Exclusive shared Qwen lock prevents double runs. Resume never overwrites results.

Stop after the comparison/report or a real blocker. No holdout access, new
retrieval experiment, production/configuration change, final safety-policy work,
M3, new source or additional model variant. M2-06 remains open for owner review.
