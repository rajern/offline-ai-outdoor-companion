# Outwise M2-06 — scorer corrections and optimization preflight

2026-10-08. **Stopped before phase A: 0/31 configurations run.** Repository
started clean at `5653392`, with no subsequent local or remote changes. The owner
authorized the unchanged 25-case development set and conditional optimization.

The scoring corrections passed calibration. The selected Qwen Q4_K_M model and
installed llama.cpp runtime failed embedding repeatability checks, including
two fresh processes. The cause remains unresolved. I have not substituted a
model, weakened the check after observing results, or run a two-model comparison.
There is consequently **no retrieval-quality ranking or recommended winner**.

## Corrected scoring

- **Case 05:** A clearly applicable universal outdoor-thunderstorm warning can
  support the outdoor-overhang instance. A/B historical requirement 4 is marked
  covered in the separate versioned adjudication layer, without changing gold.
- **Case 08:** Calling AND delivered guidance remain necessary. A/B/C8 requirement
  1 is adjudicated not covered; B8/C8U8 contain both components. Certificate route
  3 is disabled in an in-memory copy. Original certificate/reference files are
  unchanged. Historical child/baby and hypothermia risk flags are separately
  interpreted under the approved V2 scope rules, without automatic misdirection.
- **Case 09:** V3 examines individual substantive paragraphs inside relevant
  blocks. Municipal care-service evacuation is now identified as irrelevant in
  A/B. Clearly scoped post-ice rescue advice remains irrelevant, not automatically
  misleading. Direct conflict remains a separately reported subset of risk.

`retrieval_adjudication.v1.json` binds decisions to the exact saved context hashes.
`retrieval_judge_prompt.v3.md` preserves V2 and uses the unchanged V2 schema.
This is implementation of owner-approved development rules, **not independent
human expert adjudication or approval of product safety**.

## Verification and Codex consumption

**22/22 targeted regression rows passed:** the 12 known historical contexts and
ten previous synthetic controls for partial support, negation, quantity, scope,
geography, combined passages, irrelevant content, conflict, empty gold and case
07's exception. There were 19 unique inputs and three exact cache hits. This is
calibration, not a new independent validation set. No broad judge test suite was
rerun through the model.

| Measured judge consumption | This task only |
|---|---:|
| Actual calls / completed turns | 19 / 19 |
| Exact result-cache hits / avoided calls | 3 / 3 |
| Input tokens | 124,688 |
| Cached input, included in input | 27,648 |
| Output, including reasoning | 15,445 |
| Reasoning, included in output | 1,284 |
| Total tokens | 140,133 |
| Sum call time | 471.58 s (7 min 52 s) |
| API calls / unknown usage / extra observed calls | 0 / 0 / 0 |

Model: `gpt-6.1-sol`, Codex CLI 0.162.0-alpha.2, Medium, ChatGPT subscription.
No quota error was encountered; remaining capacity for 775 evaluations is not
established. Subscription use has no USD/API-cost estimate. CLI JSONL still does
not attest the actual server revision; requested/catalog identity is verified.

**26 local tests passed:** seven adapter/cache/adjudication/review tests, 14
existing runtime lock/recovery tests and five packing/geography/preflight-gate
tests. Final audit verified all 19 distinct completed calls, sealed logs and
usage, unchanged historical outputs/gold/product assets and frozen regression
code. The real experiment freeze command also refused the failed Qwen preflight
before creating an experiment or retrieving development contexts.

## Exact local models and blocker

| Model | Frozen identity | Synthetic local probe |
|---|---|---|
| MiniLM | Existing qdrant ONNX revision `faf4aa4225822f3bc6376869cb1164e8e3feedd0`; Apache 2.0; FastEmbed 0.7.4; 384d | Pass |
| EmbeddingGemma 2 | `google/embeddinggemma-2`, revision `914f7f89142e33e77833254d9c9b90c3cef7303b`; Apache 2.0; 768d; CPU float32, text-only 271,002,624 parameters | Pass after missing processor dependencies were installed locally |
| Qwen3-Embedding-0.6B Q4_K_M | Official F16 GGUF revision `370f27d7550e0def9b39c1f16d3fbaa13aa67728`, locally quantized; Apache 2.0; 1024d | Fail: identical-input embeddings differ |

The exact Q4 output SHA-256 is
`470901844f8cb73a3e0479ea1dd57ad1baba7072481f1897b2dc4b132b9051a7`.
Installed llama.cpp: build 11193 / `4e7481175`, CPU inference, last-token pooling.
Official Qwen GGUF offers F16/Q8 rather than Q4; the conversion source, quantizer
hash and output size are recorded. No quantized substitute was downloaded.
Official model/runtime guidance: [Google model card](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2),
[Google text setup](https://ai.google.dev/gemma/docs/embeddinggemma/inference-embeddinggemma-with-sentence-transformers),
[Qwen GGUF](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF),
[installed-version llama.cpp server interface](https://github.com/ggml-org/llama.cpp/blob/4e7481175/tools/server/README.md).

In the first diagnostic, repeated normalized Qwen query vectors differed by up
to **0.01406 per component**, with repeat cosine **0.996871**. Consecutive identical
requests also differed (maximum 0.00546). Disabling prompt caching, explicitly
erasing the slot, and using float32 KV with Flash Attention off did not pass the
predefined numerical repeatability check (`allclose`, absolute tolerance 1e-5).
Two independent processes reduced but did not eliminate the difference:
maximum **0.001127**, cosine **0.999972**. This is not a posthoc accuracy percentage
threshold. It is a technical input-reproducibility check fixed before the probes.

The root cause is unknown; I cannot attribute it conclusively to cache, threading,
quantization or a runtime bug. Ranking changes were **not tested**. The inference
is that an unexplained input-history/process effect could change close rankings
or percentile boundaries, so comparing models now risks an uncontrolled factor.
This runtime combination has not been accepted for the planned experiment.

## Resource findings and their limits

The host reports 14.70 GB RAM and 8 physical / 16 logical CPU cores. All initial
embedding adapters used four CPU threads. Core weights are approximately 0.24 GB
for MiniLM ONNX, 1.49 GB for the full Gemma download (only text loaded), and 0.40 GB
for Qwen Q4. Retained F16 conversion input adds 1.20 GB locally.

The successful tiny probes took 2.81 s / 3.05 CPU-s for MiniLM and 18.41 s /
27.31 CPU-s for Gemma, including startup/imports and repeated two-query tests.
Their recorded sums of process peak working sets were approximately 0.66 GB and
1.47 GB. Qwen's diagnostic settings ranged about 1.88–3.06 GB by the same measure.
**These are not model-only RAM or simultaneous peak RSS measurements.** The
public export labels the earlier measurement correctly; future probe code samples
simultaneous RSS. Available host RAM fell to roughly 208–248 MB in heavier probes.
No mobile, full-corpus throughput, index-size, context/prompt-token or truncation
benchmark was performed. These tiny startup results cannot establish which
retrieval model is faster or better for the actual workload.

## Planned comparisons and unfinished execution

| Phase | Planned configurations | Run | Quality/results |
|---|---|---:|---|
| A | MiniLM, Gemma 2, Qwen Q4; k=8, no threshold, P2 | 0/3 | Unavailable |
| B | k=3/5/8/12/16 × none/p10/p30/p50/p70; selected model, P2 | 0/25 | Unavailable |
| C | P1/P2/P3; selected model/k/threshold | 0/3 | Unavailable |
| Total | 31 configurations, 775 case/configuration pairs | 0/31 | No winner |

All 31 individual planned identities and their `not_run` status are in
`retrieval_optimization_preflight_results.v1.json`. Micro/macro coverage, complete
cases, noise, geography, safety regressions, prompt tokens, discarded packets and
retrieval performance are unmeasured. There is no new 15-case aggregate to compare
with historical B8's 34/51 coverage and 7/13 complete cases, and no 25-case result.
Those two populations have not been mixed.

The blinded adapter, sealed exact-identity cache and hybrid review guard are
implemented. Missing certificates remain unproven; proof/judge disagreements and
uncertainty block selection rather than becoming silent scores. The phase-A
runner and atomic P1/P2/P3 packing are prototypes with local behavior tests.
**Full B/C execution orchestration, actual truncation/resource measurement and
finalist source review remain unfinished.** The full evaluation flow is not
declared ready. These limitations are explicit rather than hidden behind a
successful calibration report.

Next step is a narrow correction/verification of Qwen's runtime, with the same
model and disclosed settings, or an explicit owner decision changing the model
plan. Then finish the remaining orchestration, freeze identities and proceed
through A → B → C with source-review stop gates. No new general judge campaign is
needed on the evidence obtained here.

The process stopped as requested: no holdout read/evaluation, production change,
Qwen answer generation, new knowledge source or extra retrieval configuration.
Models, source text, cache entries and logs remain under ignored `knowledge/local`.
Public artifacts contain rules, hashes, aggregate results and code, not raw sources.
