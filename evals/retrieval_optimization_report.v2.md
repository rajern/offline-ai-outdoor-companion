# Retrieval optimization — resumed M2-06

2026-10-08. **Status: blocked. 0/31 configurations complete.**

Execution stopped at the documented gate: Available-RAM reserve failed while loading MiniLM: 244.6 MiB available < 256 MiB required.

Gold, original references and V3 scoring are unchanged. The proposed Qwen runtime retains explicit CPU isolation; context capacity is 2048 and batch/ubatch 1024 to reduce memory. Code checks exact model-input lengths before embedding and refuses overflow. A failed early preflight does not verify the input audit or runtime of later models.

The runner implements the frozen A → B → C sequence, linear pooled top16 percentile thresholds, whole-passage packing, exact-context cache reuse, exclusive execution and checked resume. A stage choice conservatively protects every covered requirement and every misleading/conflict/geography finding per case; unresolved or material tradeoffs stop advancement.

## Implemented changes and verification

Started clean at `1593c4e`; orchestration was committed/pushed as `fbddec4` before
the resource trial. **43 local tests pass**: 12 orchestration/resume, five packing,
five Qwen adapter/metrics, seven scoring/cache and 14 judge runtime tests. The full
driver was exercised with mocked control results: exactly 3 + 25 + 3 calls to
retrieval/scoring, with thresholds frozen before the first B case. This is a
technical test, not 31 actual experiment configurations or proof of live readiness.

The unchanged V3 regression and all 22 sealed cache rows were rechecked without
fresh inference. Case05 implication rules, case08 call AND guidance/disabled
route3, case09 paragraph-level irrelevance, gap handling, binary coverage and
review/disagreement stops are preserved. No new general judge test was run.

Qwen context/batch buffers were reduced before quality results to address prior
RAM pressure. The intermediate context/batch/ubatch 2048 probe passed the unchanged
original repeatability test (attempt07): RSS 1.272 GB, 5.18 s, six local embedding
requests; minimum available RAM was 206 MB. The final proposed context 2048 /
batch/ubatch 1024 setting is unit-tested, but its real-model repeatability and
complete token audit were **not reached**, because final preflight stopped at
MiniLM startup. Gemma's final technical probe was also not reached. No model,
reasoning level, CPU flag, prompt, gold or scoring rule was substituted.

The exact preflight source snapshot and its 13 hashes are preserved locally.
After the live memory stop, only explicit retry/reporting safeguards and their
unit tests were added; no second model trial was launched. Real index construction,
context serialization, new-case scoring and finalist source review remain
**unverified**. No complete end-to-end readiness is claimed.

## All planned configurations

| Configuration | Model | k | Threshold | Packing | Retrieved / judged | Status | Micro25 / macro25 / complete25 |
|---|---|---:|---|---|---|---|---|
| A-minilm | minilm | 8 | None | P2 | 0 / 0 | not_run | unavailable |
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

Technical preflight passed: **False**. Existing sealed regression cache checks: 22; fresh preflight judge calls: 0.

- minilm: pass=False; 4.49 s; simultaneous process-tree RSS 0.644 GB; minimum host available RAM 256.5 MB.

Operational limits were fixed before quality results: 256 MiB available-RAM reserve and 4 GiB process-tree RSS cap. Models run sequentially in separate workers. Measurements are sampled every 100 ms; they do not establish mobile feasibility.

Codex judge: 0 actual calls, 0 successful, 0 experiment cache hits, 0 calls with unknown usage. Tokens: `{}`. Sum call time: 0.00 s. ChatGPT subscription only; paid API calls: 0.

## Recommendation and review

No retrieval winner or ranked quality comparison is recommended: no configuration
has been evaluated. Micro/macro changes, complete-case changes, new noise/safety/
geography findings, threshold values and finalist passages are unavailable for
both 25 and legacy15. Do not substitute missing results with zeros.

Even after the worker exited, three read-only host measurements showed only
386–487 MB available out of 14.70 GB RAM. The operational reserve was fixed before
any quality result; it was not lowered after the failure. No other user program
was closed. Free sufficient RAM for the heavier model workers before resuming.
The earlier successful Gemma probe used about 1.47 GB by its historical measurement;
allow additional space for Python, the parent runner and the RAM reserve.

Explicitly resume with:

```powershell
knowledge/local/optimization-env/Scripts/python.exe evals/run_retrieval_optimization_v1.py run --retry-technical
```

This preserves every old attempt and archives the preceding summary. A technical
identity cannot be changed after experiment freeze. No experiment workspace was
created in this task. The existing 31-plan and all scoring rules remain the basis
for the next run; no API fallback, model-list change or new quality threshold is
authorized by this report.

Raw contexts, judge input/output, sources, vectors and worker logs remain ignored under `knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/`. Public artifacts contain configuration definitions, hashes and summaries. Original preflight/stability reports remain historical records. No holdout, answer generation, new source or production change was performed.
