# Sol Codex judge validation v2

Owner authorization, 2026-10-08: GPT-6.1 Sol / Codex CLI / Medium / ChatGPT
subscription; 15 synthetic stress examples with three identical repeats, followed
by the nine remaining original historical cases across A/B/B8/C8/C8U8 (45 calls).
No OpenAI API calls, new retrieval, Qwen generation, embeddings, packing changes,
production changes or holdout access. The v1 recommendation is superseded by the
owner's provisional selection; v1 artifacts and references stay unchanged.

Changes and category definitions: `retrieval_judge_changes.v2.md` and
`retrieval_judge_prompt.v2.md`. `retrieval_judge_stress.v2.json` contains fictional
calibration data/expectations, never expert ground truth. Expectations, config
names and historical labels are stored separately and never sent to the judge.
The explicit corpus-gap description is retained; cohort/pass labels are removed.

## Commands

Use the evaluation environment from `JUDGE_PILOT.md`. The new runner never calls
v1 API/preflight functions or loads `.env`. It reuses v1 serializers, validation
and restricted CLI command flags without changing that frozen code.

```powershell
python -m unittest discover -s evals -p test_codex_judge_runtime.py
python evals/retrieval_judge_validation.py prepare --stage stress
python evals/retrieval_judge_validation.py run --stage stress
python evals/retrieval_judge_validation.py summarize --stage stress
# Inspect/calibrate stress outcomes before freezing the historical validation.
python evals/retrieval_judge_validation.py prepare --stage validation
python evals/retrieval_judge_validation.py run --stage validation
python evals/retrieval_judge_validation.py summarize --stage validation
python evals/retrieval_judge_validation.py verify --stage validation
```

Outputs remain under ignored
`knowledge/local/diagnostics/retrieval-judge-validation-v2-2026-10-08/{stress,validation}`.
`--run-dir` may only name a new directory under `knowledge/local`.
`prepare` refuses existing directories; run/resume never repeats a recorded
completed, invalid, failed or uncertain attempt. New intentional repetitions must
be in the frozen plan, not retries added after inspecting results.

## Execution, recovery and isolation

A kernel-backed exclusive file lock serializes **all v2 workers in this checkout**.
The lock releases on process exit; its persistent file is not a stale-lock signal
and must not be deleted by age. Never launch archived v1 alongside v2.
Before inference, an immutable intent and global active-call journal are written.
CLI stdout JSONL/stderr go directly to local files before parsing. Every turn's
usage is accounted, including invalid answers. The final result cannot overwrite
an existing record. A crashed completed call can be reconstructed from its final
JSONL message/usage without inference; recovered duration may remain unknown.
An unfinished call blocks further calls pending reconciliation, not an automatic
retry. This protects against forgetting an orphaned call in another v2 run.

Each judge starts ephemerally in a new directory outside the repo containing only
instructions/schema. A single input is provided by stdin. API credentials and
parent conversation/tool-pipeline variables are stripped. ChatGPT auth, exact
requested model and Medium support are verified. Project instructions, skills,
shell/exec, browsing, apps/plugins, memory and agent delegation are disabled.
Unexpected tool events invalidate a result and stop the batch. JSONL does not
prove the actual backend model/revision; it remains unknown. Runtime instructions
remain a confound, and this is tool/process isolation rather than an OS container.

## Freeze and scoring

Each stage freezes prompt, schema, settings, code, data/reference hashes and exact
delivered inputs before calls. Source-code snapshots are retained locally. Saved
contexts are verified against legacy gold/corpus/context hashes and licence
metadata. Original pilot outputs and product assets are hashed for immutability.
Historical validation uses cases 01,04,05,09,10,11,12,13,14 only. Calibration cases
and historical validation remain distinct; no prompt changes during validation.

Python computes coverage. Structural validation cannot prove semantic entailment.
Unknown items receive no points or invented zeros, and `requires_review` blocks
final coverage/complete-case resolution. Empty/gap gold never earns a complete
pass. Coverage, irrelevance, misleading advice, direct conflict, jurisdiction and
resources stay separate. Legacy reference disagreement reflects both possible
errors and changed noise definitions, not independent human accuracy.

No automatic configuration winner or acceptance threshold is chosen here.
Existing certificate checks are positive proof candidates, not authoritative
negative scorers: an unrecognized route stays unresolved. All conjuncts and
applicability must actually be established; case 08 shows why agreement with old
labels alone does not validate a certificate. Full hybrid integration, cache keys
for future contexts, human adjudication and approved tolerances are assessed in
the report; the 31 configurations remain unrun.
