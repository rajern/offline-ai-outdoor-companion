# Historical retrieval judge pilot

The owner authorized this bounded pilot on 2026-10-08. It evaluates saved
retrieval context, not generated answers. It does not approve the development
foundation, autonomous scoring, retrieval optimization, safety policy or release.
Do not open `holdout/` for this workflow.

The three requested alternatives are GPT-6 Luna API / Medium, GPT-6.1 Sol API /
Medium, and GPT-6.1 Sol Codex CLI / Medium through ChatGPT subscription access.
No model or reasoning substitutions are allowed. All receive the same frozen
judge instructions, JSON schema, case requirements and original delivered blocks.
Codex adds its own runtime messages; this is a comparison of execution modes,
not a guarantee of byte-identical complete provider requests or model snapshots.

## Setup and commands

Use Python 3.11+ and a separate evaluation environment:

```powershell
python -m venv knowledge/local/judge-venv
.\knowledge\local\judge-venv\Scripts\python.exe -m pip install -r evals/requirements-judge.txt
.\knowledge\local\judge-venv\Scripts\python.exe -m unittest discover -s evals -p test_retrieval_judge_pilot.py
```

On this machine the bundled Python and packages installed into the ignored
`knowledge/local/judge-pilot-deps` directory were used. The runner adds that
directory to its import path when present. Product dependencies are untouched.

`OPENAI_API_KEY` is read only from root `.env`, with interpolation disabled;
neither its value nor request headers are logged. Codex is run with OpenAI/API
credential variables removed and `forced_login_method="chatgpt"`. Verify
`codex login status` independently if authentication changes. Never copy an API
key into a CLI config, command argument, log, or second file.

```powershell
python evals/retrieval_judge_pilot.py prepare
python evals/retrieval_judge_pilot.py preflight
python evals/retrieval_judge_pilot.py run
python evals/retrieval_judge_pilot.py summarize
```

The existing pilot is preserved. `prepare` refuses overwriting it; `run` resumes
only missing records. A failed, invalid, uncertain or completed attempt is not
silently retried. An in-flight budget journal entry without a completion record
requires inspection/reconciliation before any new payment. There are no SDK
retries. A changed prompt, selection or evaluation rule needs a new version and
owner authorization; never rebrand a retuned pilot as independent validation.

`--alternatives luna-api`, `sol-api`, or `sol-codex` selects an already agreed
alternative. Run only one worker per alternative and one API worker per ledger.
For concurrent API/CLI execution, the API worker MUST explicitly use
`--alternatives luna-api sol-api` and the CLI worker `--alternatives sol-codex`.
Do not leave the default all-three selection on an API worker when another CLI
worker is active. The runner has overwrite protection, not concurrent work
claims. During this pilot the default worker overlapped the end of the separate
CLI worker, producing one unused extra CLI call and an overwrite refusal. The
original completed records survived; the extra call's usage was not persisted.
The report counts all recorded usage and identifies this unknown separately.

## Frozen design and privacy

`retrieval_judge_pilot.v1.json` selects cases 02, 03, 06, 07, 08 and 15 from the
original 15, with A/B/B8/C8/C8U8 saved contexts. The other nine historical
questions are not submitted to judges. New development questions and the final
holdout are not evaluated. There are 30 inputs per judge and at most 90 historical
assessments. The same shuffled order is used for each alternative.

`prepare` validates historical gold/corpus identity and exact delivered-context
hashes. It checks stored licence/reuse metadata and strips candidate rankings,
configuration IDs, reference labels and hidden source information. All inputs,
private references, schema, prompt, code identity, costs and protected production
hashes are frozen before historical calls. The corpus is hashed for integrity;
it is never transmitted to a judge. Only selected saved excerpts and explicit
case criteria are submitted. Raw source text and results remain Git-ignored.

Codex runs in a fresh temporary directory outside the repo containing only
instructions/schema and receives the single case by stdin. User config/rules,
project instruction loading, skills, shell/exec, apps, plugins, browsing,
computer use, hooks, memory and delegation are disabled for the judge invocation.
The process has a read-only policy. Tool events invalidate a result and stop CLI
comparison. CLI startup diagnostics are retained separately from tool events.
This removes normal file-reading routes; it is not a separate OS container
with an inaccessible filesystem. Runtime wrappers remain a documented confound.
Model/Medium support is checked in the local CLI model catalog, with explicit
flags on every call. CLI JSONL does not return backend model revision; it is
recorded as unknown rather than inferred from an answer or fabricated.

## Validation and cost accounting

The schema enforces shapes/enums; Python checks identity, exactly one item per
requirement, exact quote occurrence in the stated block, required reasons and
decision/field consistency. It cannot prove semantic correctness of a reason or
that quotes entail every condition. Covered items require evidence; partial
items require missing components; uncertain decisions block final coverage and
complete-pass metrics. Gap/empty-gold cases never earn full passes. Case 07
cream/ointment text remains outside coverage and noise scoring.

API reservations include a conservative UTF-8 input bound, schema/envelope
overhead, cache-write rate and the full 6,000-token output cap, including
reasoning. Reservations are journaled before requests and updated from actual
usage. Unknown usage retains its reservation. Output/total tokens already include
reasoning; it is not charged twice. Cache reads/writes are priced separately when
reported. The $5 cap includes failures; it is a local estimate, not a billing
guarantee. Prices and official URLs are frozen in the configuration. Recheck
prices before any authorized future pilot. Subscription tokens/time have no
inferred dollar cost. A synthetic CLI smoke check is reported separately.

Historical references were authored by earlier Codex agents with quote-based
inspection. Agreement, false positives/negatives **relative to these references**,
unknowns, case passes, noise/geography disagreement, schema/quote failures and
usage must stay separate. Six questions with five correlated contexts are not
30 independent tasks. No geographical-positive historical examples exist in the
selected pilot; agreement on negatives does not validate leakage detection.

After the report, stop for owner selection of the judge. Additional calibration,
independent adjudication, stability tests, adversarial conditions and tolerances
are still required before autonomous scoring or retrieval optimization.
