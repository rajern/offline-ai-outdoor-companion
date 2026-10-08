# Retrieval optimization preparation, 2026-10-08

Owner authorization covers the existing 25 development cases and the 31-step
plan, conditional on scorer and runtime checks. This supersedes the older
foundation preparation-only gate. Original gold, references and V1/V2 outputs
remain unchanged. Holdout, production settings and answer generation are excluded.

**Current status: resource preflight passed after RAM was freed; phase A resumed.**
Explicit CPU isolation passes the unchanged repeatability probe and a bounded
four-query/24-synthetic-passage ranking check. See the
[stability report](qwen_embedding_stability_report.v1.md). The owner subsequently
authorized A → B → C without intermediate approvals. Orchestration is implemented
and technically tested, but model preflight stopped when MiniLM left only 244.6 MiB
available RAM (reserve: 256 MiB). See the [resumed report](retrieval_optimization_report.v2.md).
The second resumption passed all three model/resource/input probes with the same
256 MiB reserve and 4 GiB RSS limit. All 25 MiniLM contexts were saved. The source
verifier initially compared raw dictionaries with dataclass dictionaries that
add `published_at: null`; the one-line correction canonicalizes the frozen source
through the same KnowledgeItem defaults. Changed source content, provenance or
metadata remains rejected. Thirteen orchestration tests passed, including this
default/mutation regression. See
[`retrieval_optimization_serialization_correction.v1.json`](retrieval_optimization_serialization_correction.v1.json).
The old freeze and passed preflight are preserved with a separate correction
manifest; only the runner verification-line identity was amended before any
judge call. All 980 existing index/context/token-cache files retain their hashes.
Ordinary `run` resumes them without another model probe or retrieval call.
No scoring, gold, model, packing or resource settings changed. Final results and
source review remain pending. The preceding failure is preserved in the
[report](retrieval_optimization_report.v1.md) and
[machine-readable results](retrieval_optimization_preflight_results.v1.json).

## Scoring and calibration

`retrieval_adjudication.v1.json` is the separate owner-authorized interpretation
layer. It permits clear universal implications for case 05, disables the third
case 08 requirement-1 certificate route in memory, and applies V2 scope rules to
historical noise labels. No original certificates or references are rewritten.
`retrieval_judge_prompt.v3.md` adds paragraph-level institutional irrelevance
checks while preserving V2. Schema V2 is reused unchanged.

`retrieval_optimization_scoring.py` provides the blinded adapter, complete-source
certificate checks, explicit proof/judge-disagreement review and exact-identity
cache. Cache keys bind the entire delivered input, prompt/schema, model/effort,
authentication, CLI version/settings, validator versions and relevant input/
judge code. V2 results cannot be reused under the changed V3 prompt. Equivalent
V3 inputs reuse a sealed call; input, output, usage, final JSONL and file hashes
are rechecked. Review/uncertain prevents aggregate selection scores; a missing
certificate does not replace a semantic judgment with zero. The existing global
OS lock and active-call recovery remain in use. API functions are never called.

The regression uses 12 saved known-problem contexts and ten selected previous
synthetic controls: 22 rows, 19 unique inputs, three exact cache hits. Expectations
are separate, owner-adjudicated development calibration, not independent expert
validation. Every row passed. Source-bearing plans/logs remain ignored locally.

```powershell
python -m unittest discover -s evals -p test_retrieval_optimization_scoring.py
python -m unittest discover -s evals -p test_codex_judge_runtime.py
python evals/run_judge_regression_v3.py verify
python evals/run_judge_regression_v3.py summarize
# A completed regression run resumes without additional inference:
python evals/run_judge_regression_v3.py run
```

The frozen regression directory already exists; `prepare` never overwrites it.
Changes to frozen judge code require a new version and a deliberate new plan,
not a retry of existing calls. Failed/invalid calls are recorded and never
automatically repeated or switched to an API.

## Local embedding probes and experiment prototype

`optimization_embeddings.py` contains only local embedding adapters. Qwen's HTTP
endpoint is a dedicated loopback llama.cpp embedding server, not the OpenAI cloud
API or Qwen answer generation. `preflight_retrieval_optimization.py` records
synthetic dimension/normalization/repeatability probes, runtime versions and
resources. Attempts have separate directories and must not overwrite predecessors.
Current probe code also freezes its settings and records the server command.
Earlier attempts' public memory numbers are correctly labelled as sums of process
peak working sets, not simultaneous sampled RSS; raw records remain unchanged.

`retrieval_optimization.v1.json` defines the planned 3 + 25 + 3 configurations,
threshold calculation and P1/P2/P3 rules. `run_retrieval_optimization_v1.py` is a
**staged A/B/C runner**, with tested atomic packing, threshold freeze and stop gates. It refuses to
freeze while the latest probe of any named model fails. It preserves the existing MiniLM
document vectors and would tokenize the unchanged grounded prompt using the
locked GGUF/tokenizer, without generation. The proposed snapshot workspace
explicitly copies only development/code/corpus inputs; it contains no holdout.
Python workers reject attempts to open or traverse the holdout. This is a process
guard, not an OS security boundary. The experiment workspace has not been created
because the resource preflight failed.

The Qwen adapter now explicitly disables devices, operation offload and KV
offload; zero GPU layers alone did not isolate the old runtime. The unchanged
original probe passes in attempt 06. `diagnose_qwen_stability.py` refuses to
overwrite its frozen local plan and records repeats, token IDs, cosine, ranking,
top-k membership and boundary crossings. No judge or optimizer is called.

The runner now accounts exact embedding inputs, uses serial short-lived model
workers, verifies source/context/prompt hashes and tokenizer caches, and freezes
the per-model top16 linear percentiles before B. Qwen retains the CPU flags;
proposed capacities are context 2048, batch/ubatch 1024. The intermediate 2048/2048
buffer probe passed unchanged numerical tolerance, but the final 1024-batch model
preflight was not reached. Full real-corpus execution and finalist source checks
are consequently unverified. 43 local technical tests passed; a mocked full driver
checks exactly 31 configurations. These tests are not model-quality evaluations.

Before resuming, free sufficient host RAM. Operational limits were fixed before
quality results: 256 MiB available reserve and 4 GiB process-tree RSS. Preserve
the failed preflight and explicitly retry only after the resource state changes:

```powershell
knowledge/local/optimization-env/Scripts/python.exe evals/run_retrieval_optimization_v1.py run --retry-technical
```

This preserves each failed attempt and archives the preceding summary. It cannot
replace preflight identities after experiment freeze. After a successful freeze,
ordinary `run` verifies identities and resumes existing indices, contexts and
sealed scores; review, failed judge calls or quota errors remain blocking.
Do not bypass the gate to run two models, select
a winner or implement production changes. Exact backend Sol revision remains
unreported by CLI JSONL, as in V2; requested/catalog model and Medium are verified.
No subscription-limit share or unlimited capacity is inferred from token counts.

Local environment used for embedding probes:
`knowledge/local/optimization-env/Scripts/python.exe`. This is separate from the
product environment. Installed versions are in the public preflight results;
large models, packages, raw sources, vectors and logs are ignored. Model setup
used official pinned revisions; Qwen Q4_K_M was locally quantized from official
F16 with the recorded runtime and output hashes, without changing the tokenizer
or production assets.
