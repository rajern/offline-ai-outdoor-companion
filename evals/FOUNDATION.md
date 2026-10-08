# Retrieval evaluation foundation — proposal v2

Owner update, 2026-10-08: the existing 25-case development set is approved for the
conditional optimization task. The original preparation-stage approval wording
below is retained as history. Separate adjudication and scorer regression passed;
the previous execution stopped at the Qwen Q4 runtime probe. Bounded follow-up
diagnostics now pass with explicit CPU isolation; see
[`qwen_embedding_stability_report.v1.md`](qwen_embedding_stability_report.v1.md).
The owner then authorized the existing 31-stage optimization. The resumed task
stopped before phase A at the RAM preflight; see
[`retrieval_optimization_report.v2.md`](retrieval_optimization_report.v2.md).
After the owner freed RAM, all three sequential model/resource/input checks
passed. Phase A now has 25 saved MiniLM contexts. A one-line provenance comparison
correction handles missing `published_at` through the existing KnowledgeItem
default, while preserving every source/context/index hash. The old freeze and
preflight summary are archived; a separate implementation-correction manifest
records the exact runner hashes before/after and 980 preserved result files.
No gold, judge, packing, resource or model settings changed; no judge call had
occurred before the correction. See
[`correction record`](retrieval_optimization_serialization_correction.v1.json).
The run resumed from those contexts. See the earlier
[`retrieval_optimization_report.v1.md`](retrieval_optimization_report.v1.md).
This grants no control-set access or final product/safety approval.

Status: **pending owner approval**. This task prepares cases and scoring only.
No new retrieval, control-set evaluation, generation, parameter search, model
change or production change was performed. Source inspection and rescoring of
already saved historical contexts are not new retrieval experiments.

Subsequent judge work, 2026-10-08: the owner selected Sol Codex Medium
provisionally. The [v2 validation report](retrieval_judge_validation_report.v2.md)
records completed synthetic stress tests and nine original historical cases.
The scoring-method discussion below describes the foundation preparation stage;
judge implementation now exists, while full hybrid scoring, new gold approval
and retrieval optimization remain pending owner review.

## Datasets and reproducibility

- `retrieval_development.v2.yaml`: all 25 development questions; its first 15
  case objects exactly equal `retrieval_cases.v1.yaml`. That original file and
  previous results remain unchanged.
- `retrieval_development_additions.v2.yaml`: the ten new case definitions and
  per-item `must_have_evidence`. Each evidence route lists actual approved
  source text/heading, not a required chunk ID. Multiple delivered passages can
  jointly satisfy a requirement; source IDs are provenance, not automatic credit.
- `holdout/retrieval_control.v1.yaml`: ten separate controls, with corresponding
  gold/evidence. Its README and AGENTS instructions govern later access.
- `retrieval_sources.v1.json`: titles, URLs, publishers, attribution and reuse
  metadata for the same 22 approved sources. No corpus content was changed.
- `retrieval_foundation.lock.json`: proposed versions/hashes, including the
  control-set hash without exposing control questions to optimization tooling.
- `.gitattributes` disables line-ending conversion for eval artifacts and the
  source manifest: existing LF and generated CRLF bytes both remain exactly
  preserved, so their recorded hashes survive a new Windows checkout.
- `retrieval_development_qa.v2.json`: source offsets, section references and
  hashes supporting all new development must-have requirements. Control-source
  QA is separate under `holdout/authoring_qa.v1.json`.

The source snapshot contains 22 documents and 190 passages. Development has
22 supported cases and three insufficient-coverage cases; controls have nine
supported cases and one gap. The new development cases contain 21 required
items. New controls contain 24 required items. Gap cases are not ordinary
coverage failures or automatic passes; supported subsets remain inspectable.

Question authoring used source content, not retrieved rankings. Historical
results were known to the author: this is not blinded authoring or an independent
external benchmark. Source support, source applicability, conjunctions and
limits were checked before calibration. No gold or certificate rules were
tuned after calibration. Exact duplicate questions were absent across all 35;
word-overlap checks were supplemented by an author review of information needs.
Shared topics are deliberate; CPR recognition versus CPR execution, navigation
versus trip-recipient planning, and self-rescue versus rescue of someone else
require materially different information. Difficulty labels are estimates.

### Ten new development cases

| Case | Situation / core gold | Sources | Difficulty |
|---|---|---|---|
| 16 | Dirty abrasion: appropriate washing; mild unscented soap if dirty; protection against new dirt | 02 | straightforward |
| 17 | Wasp sting with rapid allergic symptoms: recognize source-supported anaphylaxis pattern and urgent 113/medical help | 08 | harder |
| 18 | Self-rescue through thin ice: head above water, return direction, sound edge and a complete ascent method | 19 | harder |
| 19 | Avalanche group equipment: everyone carries beacon, probe and shovel and practises using them | 17 | straightforward |
| 20 | More demanding hike and changing weather: match ability to route; check forecast and change plans | 10, English | straightforward |
| 21 | Stove failed, 0.3-micron filter and tablets: filter limits including viruses; filtering followed by disinfection/product instructions | 21, English | harder |
| 22 | Navigation preparation in New Zealand: suitable offline/topographic coverage, download/test, battery and map backup | 09, English; NZ | harder |
| 23 | Already sheltered during thunderstorm: wait 30 minutes after last thunder; avoid electrical/plumbing exposure | 22, English | straightforward |
| 24 | Flooded stream and eroded steep banks: keep away from high water and unstable slopes/erosion/landslide exposure | 20 | straightforward |
| 25 | Build a stable rainproof branch shelter without tent/tarp: procedural coverage is absent | related general shelter sources only | gap |

Full questions, precise gold, acceptable alternatives, optional details,
misleading context and evidence routes are in the YAML, not just this summary.
Supporting sources are never required when applicable primary context supplies
all must-have facts. More sources/text cannot raise the core score. Norway and
NZ applicability remain explicit, including positive NZ applicability cases.

For comparability, report the unchanged first-15 slice against historical
baselines **separately** from the new full-25 result. Do not compare their
aggregate percentages as if they used the same population. Keep the existing
protocol (`retrieval_protocol.v1.yaml`) and source/corpus identities intact.
Owner approval should freeze this proposal before any new configurations run.

## Scoring investigation

The unit being scored is each complete information requirement in **delivered
context**, not a matching document ID, search hit, rejected budget packet or
information available elsewhere in the corpus. All conjunctions, conditions,
units and qualifications must be present; partial satisfaction earns zero in a
completed score. Optional information cannot compensate. Equivalent wording
and correct unit conversions remain valid gold alternatives.

| Method | Value / cost | Main risk |
|---|---|---|
| Deterministic evidence certificates | Cheap CPU-only positive proof from actual delivered source text; auditable, no model | Non-exhaustive; paraphrases, conversions and alternative passage combinations may remain unresolved |
| Fixed-rubric LLM judge | Can assess semantic entailment, noise and applicability across representations; repeated inference cost | False entailment/negatives, bias, unstable scores, language and high-stakes condition errors; no judge is implemented or validated yet |
| Hybrid with human calibration | Deterministic proofs first, semantic review for unresolved items and noise/geography, human checks on representative and adversarial samples | More engineering and review; unresolved items must block autonomous selection rather than silently become scores |

Recommendation: **hybrid**, not an opaque overall judge score. Proposed later
workflow: source certificates -> immutable exact-context manual-result cache
where available -> a blinded, separately calibrated semantic judge -> human
adjudication of uncertainty and finalist checks. The cache and judge are future
proposals, not implemented services. Judge choice and any local runtime/cloud
service require owner approval; no new model was downloaded or tested here.

The prototype (`automatic_retrieval_scoring.py`) certifies complete evidence
routes using whitespace-normalized delivered text and valid provenance. It
does not demand original chunk IDs or a particular chunk order. An unmatched
route returns `needs_review`, **not** a reliable negative. This is an intentional
incomplete proof system, not an architecture-neutral complete semantic scorer:
rewritten/summarized text and different valid alternatives need review. Do not
rank configurations by its lower bounds alone. No silent zero scores or wins
are allowed from unresolved items.

The proposed judge rubric is `retrieval_judge_rubric.v1.md`. The judge must see
only question, gold criteria and actual delivered context, without configuration
identity, rank or hidden source text. Each positive needs validating quotes from
that context. Quote presence alone still does not prove entailment; human
calibration must include missing qualifiers, negation, numeric changes, metric
conversions, alternate passages, cross-language cases and geographically wrong
material. Freeze rubric, model, decoding and validation rules before testing.

Existing work supports separating retrieval/context evaluation from answer
faithfulness ([RAGAS](https://arxiv.org/abs/2309.15217)). LLM judging is a candidate,
not assumed ground truth: published evaluations identify position, verbosity
and self-preference biases and limited reasoning
([MT-Bench judge study](https://arxiv.org/abs/2306.05685)). These methods were
researched only; no judge inference occurred.

### Saved-context calibration (not a new retrieval experiment)

Certificates were authored from sources before comparing them with manual
labels. `prepare_eval_foundation.py calibrate` reads saved contexts and manual
annotations for the existing 15 cases only. It verifies gold/corpus identities,
context hashes and saved token counts. It does not open the holdout.

| Saved configuration | Correct positive proofs / 51 covered-case items | False-positive proofs | Unresolved items | Complete-case lower bound / 13 |
|---|---:|---:|---:|---:|
| A | 20 | 0 | 31 | 2 |
| B | 21 | 0 | 30 | 2 |
| B8 | 34 | 0 | 17 | 7 |
| C8 | 33 | 0 | 18 | 6 |
| C8U8 | 34 | 0 | 17 | 6 |

Across 255 covered-case item comparisons, all 142 manually positive items were
certified; none of the 113 manually negative items received a positive proof.
Those 113 remain unresolved: this is **55.7% resolution**, not 100% reliable
automatic scoring. The comparisons reuse the same 15 previously seen questions
and correlated contexts; they are not 255 independent cases. Retrospective
agreement does not establish future reliability or alternative-representation
fairness. All per-case decisions and input hashes are in
`retrieval_scoring_calibration.v1.json`.

Gap case 14 has a concrete remaining limitation: each saved configuration has
one manually covered supported-subset item, but the conservative certificate
does not prove it (0/2 certified). Rules were not adjusted after seeing this.
Case 15 has no full-answer gold and must never pass on an empty required list.

Noise, potentially misleading context and final jurisdiction-leakage metrics
are **not automated**: nonempty contexts require semantic review. Metadata
applicability checks are guardrails, not proof of zero leakage. Calibration
records previous human flags separately, without using them as auto decisions.
Context/prompt tokens and rejected packets are preserved from saved artifacts;
future runs must measure their actual tokenizer/template inputs and complete
prompt budget, not infer tokens from characters or assume template overhead.

### Required metrics and blockers before autonomy

Keep micro must-have coverage, average per-case coverage, complete case passes,
irrelevant context, misleading context, jurisdiction leakage, retrieved
packet/chunk count, context tokens, complete prompt tokens and budget rejection
counts separate. Report gaps and supported subsets separately. During prototype
review show uncertainty/bounds explicitly; only adjudicated full binary decisions
may drive the agreed final coverage metrics.

Before autonomous optimization the owner must approve the 20 new cases and
process holdout; a complete scoring method must be calibrated beyond positive
certificates, particularly negatives, noise, geography and alternate wording.
No numeric acceptance threshold or judge-error tolerance is invented here.
Agree these before further runs. Cases with clinical/natural-hazard limits are
retrieval tests, not approval of a final safety policy or individual diagnosis.

The holdout is author-known and publicly versioned, not cryptographically secret.
Instruction and loader exclusion are procedural controls, not a filesystem
security boundary. A later optimizer with unrestricted repository access must
be instructed not to read it; stronger isolation requires an owner-controlled
checkout/access boundary. The one final control run needs explicit permission
after selecting and freezing the configuration. Any tuning based on control
results consumes the holdout and requires new controls.

## Checks and rerun instructions

- Source/schema QA: all 20 new cases, all required evidence routes and sections;
  exact original-case preservation and no exact duplicate questions.
- New prototype tests: `python -m unittest discover -s evals -p test_eval_foundation.py`.
- Existing behavior tests: `python -m pytest backend/tests evals/test_parent_context.py evals/test_retrieval_refinement.py evals/test_token_chunking.py`.
- Frontend: `pnpm typecheck`.

Completed verification: 11 new scoring tests and 80 existing backend/eval tests
passed; frontend typecheck and web export passed. Build output remains ignored.

Dependencies are existing local Python/PyYAML, pytest and frontend tooling; no
dependencies were added. Helpers require the frozen, ignored local corpus and
historical raw contexts to reproduce source QA/calibration. They are not pushed
as public data. Public hashes and per-item decisions permit audit; full local
reruns need the same legally sourced local artifacts. Output scripts refuse to
overwrite results. Never invoke authoring control QA as part of optimization,
calibration, debugging or development-result review.

**Stop point:** waiting for owner approval of evaluation foundation and scoring
approach. The full automated scorer is not yet ready for unattended optimization.
