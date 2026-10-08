# Retrieval evaluation cases

## Proposed foundation v2 — pending owner approval

See `FOUNDATION.md` for the ten new development cases, scoring investigation,
saved-context calibration and limitations. `retrieval_development.v2.yaml`
contains 25 cases; its original 15 case definitions remain exactly unchanged.
`retrieval_foundation.lock.json` records versions and hashes. Full automatic
scoring is not yet validated for unattended optimization.

Ten controls are stored separately under `holdout/`. Do not read that directory
for optimization, debugging, intermediate-result assessment or judge calibration.
It is an author-known procedural holdout, not a secret dataset. Read applicable
AGENTS instructions; only an explicitly authorized final run may evaluate it.

## Original v1 set and historical comparisons

`retrieval_cases.v1.yaml` contains 15 information-based retrieval cases for the
owner-approved, frozen local Outwise knowledge base. Cases 01–05 preserve the
owner-reviewed pilots with the final requested revisions; cases 06–15 are new
proposals in the original file's retained review metadata. Historical evaluation
reports and results are preserved; the v2 additions still await owner approval.

## Purpose and pass criteria

This set evaluates **retrieved context independently of answer generation**.
It does not evaluate Qwen's answers, language quality, abstention, or implement
the project's safety policy. Gold expectations come from source inspection,
not retrieval rankings. All questions are Norwegian; several require English
source material. Difficulty labels are author estimates, not measured results.

For `expected_result: supported_context`, all `must_have_information` must be
available in applicable context, with necessary conditions and limitations.
Equivalent wording and correctly converted units count. Multiple passages may
collectively satisfy the criteria. A correct document title alone is not enough.
Section references identify evidence locations, not required chunks or an
exhaustive passage whitelist. Optional facts are not additional pass requirements.

Supporting sources are never required for a retrieval pass if the
preferred/primary source already covers all must-have information. Supporting
sources may improve context, but retrieval quality should not be rewarded merely
for returning more sources or more text. If primary context is incomplete,
another approved, applicable passage may supply a missing must-have fact: that
fact is required, not the identity of the supporting source. Irrelevant,
misleading and jurisdictionally inappropriate material must be noted separately,
not rewarded for length or source count. This file does not set top-k, ranking
thresholds or a noise-penalty formula; those belong to a later approved eval protocol.

## Knowledge gaps and geography

Cases 14 and 15 have `expected_result: insufficient_coverage`. There is no
full-answer gold context in this snapshot. Case 14 lists its source-supported
subset; case 15 has an empty must-have list because Norwegian fire rules are
absent. Neither is an automatic pass, nor an ordinary retrieval failure for
missing content that is not in the corpus. Future runs should report coverage
gaps and any supported subset separately from complete-answer retrieval results.
Returning a broad article, an un-ingested link or country-inappropriate rules
must not be treated as full coverage. LLM recognition of insufficient context
requires a separate generation evaluation; this set cannot measure that behavior.

`knowledge_gap.status: bounded_limitations` means the stated general information
need is covered, but the source cannot decide individual diagnosis, location,
route, real-time conditions or other explicitly listed limits. It is distinct
from `insufficient_coverage` for the core question. Such missing information
must not silently become a gold requirement or an invented instruction.

All cases use jurisdiction `NO`. General content is usable across jurisdictions;
NZ-specific emergency services, laws and operational rules are not Norwegian
gold. Mixed documents must be considered section by section. Case 15 explicitly
tests this distinction without changing production filtering.

## Format, provenance and stability

The YAML contains `schema_version`, `set_version`, frozen corpus/manifest hashes,
a source map and the `cases` list. Each case uses the same fields for the question,
relevant sources, primary sections, optional supporting sources, must-have facts,
acceptable passage combinations, optional information, misleading information,
knowledge gaps, gold uncertainty and rationale. Resolve document references in
`relevant_sources` and section entries through `sources` for title, publisher,
URL and language. These are approved document IDs, not chunk IDs. Source-based
criteria are paraphrases; attribution and reuse terms are retained through the
source map and `knowledge/manifests/approved-sources.json`, not raw article copies.

Keep the approved set stable during retrieval comparisons. Record the exact
set-file hash/version and corpus hash alongside future results. Do not edit
questions or criteria after looking at retrieval results. An owner-approved
semantic change requires a new set version; a changed corpus requires review of
coverage, geographic applicability and the source conflict noted in case 07.
Do not silently mark proposed cases approved or resolve clinical/legal uncertainty.

Existing `real-knowledge.json`, diagnostic case files and comparison scripts are
separate historical artifacts. This v1 set does not overwrite them, alter their
behavior, wire itself into production or authorize running any evaluation.
