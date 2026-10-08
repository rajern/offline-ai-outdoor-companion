# Retrieval optimization — resumed M2-06

2026-10-08. **Status: running. 0/31 configurations complete.**

Gold, original references and V3 scoring are unchanged. The proposed Qwen runtime retains explicit CPU isolation; context capacity is 2048 and batch/ubatch 1024 to reduce memory. Code checks exact model-input lengths before embedding and refuses overflow. A failed early preflight does not verify the input audit or runtime of later models.

The runner implements the frozen A → B → C sequence, linear pooled top16 percentile thresholds, whole-passage packing, exact-context cache reuse, exclusive execution and checked resume. A stage choice conservatively protects every covered requirement and every misleading/conflict/geography finding per case; unresolved or material tradeoffs stop advancement.

## All planned configurations

| Configuration | Model | k | Threshold | Packing | Retrieved / judged | Status | Micro25 / macro25 / complete25 |
|---|---|---:|---|---|---|---|---|
| A-minilm | minilm | 8 | None | P2 | 25 / 11 | partially_scored | unavailable |
| A-gemma2 | gemma2 | 8 | None | P2 | 0 / 0 | not_run | unavailable |
| A-qwen3-q4 | qwen3-q4 | 8 | None | P2 | 0 / 0 | not_run | unavailable |
| B-k3-none | pending stage choice | 3 | none | P2 | 0 / 0 | not_run | unavailable |
| B-k3-p10 | pending stage choice | 3 | p10 | P2 | 0 / 0 | not_run | unavailable |
| B-k3-p30 | pending stage choice | 3 | p30 | P2 | 0 / 0 | not_run | unavailable |
| B-k3-p50 | pending stage choice | 3 | p50 | P2 | 0 / 0 | not_run | unavailable |
| B-k3-p70 | pending stage choice | 3 | p70 | P2 | 0 / 0 | not_run | unavailable |
| B-k5-none | pending stage choice | 5 | none | P2 | 0 / 0 | not_run | unavailable |
| B-k5-p10 | pending stage choice | 5 | p10 | P2 | 0 / 0 | not_run | unavailable |
| B-k5-p30 | pending stage choice | 5 | p30 | P2 | 0 / 0 | not_run | unavailable |
| B-k5-p50 | pending stage choice | 5 | p50 | P2 | 0 / 0 | not_run | unavailable |
| B-k5-p70 | pending stage choice | 5 | p70 | P2 | 0 / 0 | not_run | unavailable |
| B-k8-none | pending stage choice | 8 | none | P2 | 0 / 0 | not_run | unavailable |
| B-k8-p10 | pending stage choice | 8 | p10 | P2 | 0 / 0 | not_run | unavailable |
| B-k8-p30 | pending stage choice | 8 | p30 | P2 | 0 / 0 | not_run | unavailable |
| B-k8-p50 | pending stage choice | 8 | p50 | P2 | 0 / 0 | not_run | unavailable |
| B-k8-p70 | pending stage choice | 8 | p70 | P2 | 0 / 0 | not_run | unavailable |
| B-k12-none | pending stage choice | 12 | none | P2 | 0 / 0 | not_run | unavailable |
| B-k12-p10 | pending stage choice | 12 | p10 | P2 | 0 / 0 | not_run | unavailable |
| B-k12-p30 | pending stage choice | 12 | p30 | P2 | 0 / 0 | not_run | unavailable |
| B-k12-p50 | pending stage choice | 12 | p50 | P2 | 0 / 0 | not_run | unavailable |
| B-k12-p70 | pending stage choice | 12 | p70 | P2 | 0 / 0 | not_run | unavailable |
| B-k16-none | pending stage choice | 16 | none | P2 | 0 / 0 | not_run | unavailable |
| B-k16-p10 | pending stage choice | 16 | p10 | P2 | 0 / 0 | not_run | unavailable |
| B-k16-p30 | pending stage choice | 16 | p30 | P2 | 0 / 0 | not_run | unavailable |
| B-k16-p50 | pending stage choice | 16 | p50 | P2 | 0 / 0 | not_run | unavailable |
| B-k16-p70 | pending stage choice | 16 | p70 | P2 | 0 / 0 | not_run | unavailable |
| C-P1 | pending stage choice | None | None | P1 | 0 / 0 | not_run | unavailable |
| C-P2 | pending stage choice | None | None | P2 | 0 / 0 | not_run | unavailable |
| C-P3 | pending stage choice | None | None | P3 | 0 / 0 | not_run | unavailable |

The machine-readable results retain the legacy15 slice separately, all safety/relevance flags, partial reviewed decisions, token lists, resource measurements and gap results. Incomplete runs have no final ranking or recommended winner. Historical B8 was 34/51 and 7/13 on the original 15 cases; no 25-case or changed-scorer aggregate is treated as a controlled historical improvement.

## Resources and judging

Technical preflight passed: **True**. Existing sealed regression cache checks: 22; fresh preflight judge calls: 0.

- minilm: pass=True; 4.31 s; simultaneous process-tree RSS 0.916 GB; minimum host available RAM 3573.8 MB.
- gemma2: pass=True; 83.31 s; simultaneous process-tree RSS 1.944 GB; minimum host available RAM 2180.6 MB.
- qwen3-q4: pass=True; 9.68 s; simultaneous process-tree RSS 1.696 GB; minimum host available RAM 2265.5 MB.

Operational limits were fixed before quality results: 256 MiB available-RAM reserve and 4 GiB process-tree RSS cap. Models run sequentially in separate workers. Measurements are sampled every 100 ms; they do not establish mobile feasibility.

Codex judge: 12 actual calls, 11 successful, 0 experiment cache hits, 1 calls with unknown usage. Tokens: `{"input_tokens": 83373, "cached_input_tokens": 0, "cache_write_input_tokens": 0, "output_tokens": 20149, "reasoning_output_tokens": 1861, "total_tokens": 103522}`. Sum call time: 520.47 s. ChatGPT subscription only; paid API calls: 0.

## Recommendation and review

No retrieval winner is recommended from incomplete or blocked results. Resolve the concrete blocker before continuing the frozen plan; do not change gold, judge or parameters based on these observations.

Raw contexts, judge input/output, sources, vectors and worker logs remain ignored under `knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/`. Public artifacts contain configuration definitions, hashes and summaries. Original preflight/stability reports remain historical records. No holdout, answer generation, new source or production change was performed.

## Audited operational correction

After all three sequential preflight checks passed, the first source check falsely rejected a missing `published_at` field versus its dataclass default `null`. One verifier line now compares canonical KnowledgeItem records. All 25 saved contexts, 198 excerpts and 980 result-file hashes were rechecked without retrieval or inference. Changed text, URL, metadata, ID and date remain rejected in the 13 passing orchestration tests. The original freeze and technical summary are archived separately; no gold, judge, packing, model or resource setting changed. See [correction audit](retrieval_optimization_serialization_correction.v1.json).

This is a progress snapshot. An incomplete consumption entry may be the currently active call, not a failed call. Aggregate comparisons and recommendation remain unavailable until the stage completes.
