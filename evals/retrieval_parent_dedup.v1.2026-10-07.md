# Retrieval experiment: saved C8 versus eight unique parents

Date: 2026-10-07. Status: completed diagnostic experiment; stopped for owner review.
No production installation, generation, new embeddings, gold change or follow-on experiment.

## Conclusion

Deduplicating original parents before top-k has a **small, real selection benefit**,
but does not make this retrieval setup sufficiently good. One additional must-have
item is delivered: the complete adult breathing assessment in case 08. Coverage
improves from 33/51 to 34/51; complete passes remain 6/13. No previously covered
item is lost. Irrelevant and potentially misleading case rates are unchanged;
context size and budget rejections increase.

The child embeddings and cosine ranking have not improved or changed. This test
isolates selection-unit diversity, not embedding quality. Remaining failures still
include below-threshold/low-ranked relevant passages and a directly observed
packing failure for burn treatment. Do not freeze this setup in production.

## Frozen comparison

- Control: saved C8 outputs from `retrieval-child-search-v1-2026-10-07`; not rerun.
- Candidate C8U8: scan that exact ranked child list, apply the same NO/general
  eligibility and cosine >= 0.35, keep the best child of each original parent,
  and select the first eight distinct parents. Descending cosine/ascending child
  ID tie ordering is unchanged.
- Only the unit consuming a top-eight slot changes. Different original parents
  in the same section/packing branch still consume separate slots. No document
  or branch deduplication, score averaging, reranking or gold-aware selection.
- Unchanged: all 15 questions, information-based gold/protocol, corpus, 287 child
  representations/index/vectors, saved query vectors/scores, tokenizer/GGUF,
  original full parents, narrow section packing/order and atomic rejection,
  2,000-token **complete-prompt** budget. No refill beyond the eight selected
  parents, no partial packet admission and no model inference.
- Protocol/runner/input hashes were recorded before candidate packing. No
  parameter tuning or criteria changes followed inspection of the results.

Source IDs below locate inspectable evidence; they are not exact-ID pass criteria.
Must-have items require all conditions, optional facts cannot compensate, and
supporting sources are optional if applicable primary context is sufficient.
Cream advice remains outside case 07 gold; sleeping mat remains optional in case
10. Cases 14/15 remain separate insufficient-coverage cases, not zero-item passes.

## Aggregate results

Denominators here are the **13 covered cases / 51 must-have items** only.
Noise rates mean cases with at least one annotated finding, not token fractions.

| Metric | Saved C8 | C8U8 |
| --- | ---: | ---: |
| Must-have coverage (micro) | 33/51, 64.71% | 34/51, 66.67% |
| Average per-case coverage (macro) | 62.82% | 64.74% |
| Complete cases passed | 6/13 | 6/13 |
| Irrelevant context | 13/13 | 13/13 |
| Potentially misleading context | 5/13 | 5/13 |
| Either noise category | 13/13 | 13/13 |
| Jurisdiction leakage | 0/13 | 0/13 |
| Context tokens, mean / median / max | 1,397.62 / 1,550 / 1,803 | 1,439.15 / 1,582 / 1,803 |
| Complete prompt tokens, mean / median / max | 1,587.15 / 1,744 / 2,000 | 1,628.69 / 1,761 / 2,000 |
| Delivered passages, mean / median / max | 8.62 / 9 / 13 | 9.00 / 9 / 13 |
| Distinct sections, mean / median / max | 7.85 / 8 / 12 | 8.23 / 8 / 12 |
| Admitted packets, mean / median / max | 5.77 / 6 / 8 | 6.15 / 6 / 8 |
| Budget-rejected packets | 5 | 8 |
| Cases with budget rejection | 5/13 | 7/13 |
| Duplicate-branch packing skips | 16 | 7 |

Across all 15 cases, including the two gaps, budget-rejected packets are 10 versus
13. These are not delivered context and do not count as coverage or delivered
noise. Remaining seven duplicate-branch skips are different parents within the
same branch, not repeated parent selections.

## All-case comparison

Counts are fully covered must-have items, not partial credit. The six complete
passes are 02, 03, 05, 09, 10 and 11 in both configurations.

| Case | Need | C8 -> C8U8 | Result / change |
| --- | --- | --- | --- |
| 01 | Ankle injury / possible fracture | 0/4 -> 0/4 | Fail; delivered context identical. RICE rest alone does not satisfy the full movement-harm item. |
| 02 | Wet, cold companion | 5/5 -> 5/5 | Pass; identical context. |
| 03 | Stream drinking water, altitude unknown | 5/5 -> 5/5 | Pass; identical context, including both altitude-dependent boiling durations. |
| 04 | Lost trail in fog | 0/5 -> 0/5 | Fail; identical unrelated avalanche/medical context. |
| 05 | Thunderstorm on exposed ridge | 6/6 -> 6/6 | Pass; identical context. |
| 06 | Bleeding that will not stop | 3/4 -> 3/4 | Fail; initial major/uncontrolled-bleeding 113 instruction missing. Extra ice-rescue packet rejected. |
| 07 | Scalded hand | 1/4 -> 1/4 | Fail; cooling/no ice/no blister puncture still budget-excluded. Extra sprain packet rejected. |
| 08 | Unconscious adult apparently breathing | 2/4 -> 3/4 | Fail but improved; complete adult airway/breath assessment now delivered. Absent/abnormal-breath HLR plus 113 clarification still missing. |
| 09 | Prevent overheating | 3/3 -> 3/3 | Pass; extra avalanche-terrain passage is noise, not a coverage improvement. |
| 10 | Unexpected night outdoors | 3/3 -> 3/3 | Pass; identical context. |
| 11 | Toilet hygiene near camp | 3/3 -> 3/3 | Pass; extra toiletries/water-soap advice is optional, not a core-score bonus. |
| 12 | High river at trail crossing | 2/3 -> 2/3 | Fail; brown/murky-water danger and do-not-cross condition still absent. Extra ice-rescue packet rejected. |
| 13 | Emergency beacon when phone fails | 0/2 -> 0/2 | Fail; identical context lacks beacon activation trigger and activate-if-unsure guidance. |
| 14 | Whumpfs/cracks on ski tour | Gap; supported subset 1/2 -> 1/2 | Identical context. No route-specific safety judgement available; excluded from normal metrics. |
| 15 | Norwegian campfire rules | Gap; no complete gold answer | Identical context. Applicable legal/location coverage absent; not a 0/0 pass. |

Only cases 08, 09 and 11 have newly delivered passages. Every candidate context
preserves the control's exact excerpt prefix; all other contexts are identical.
Cases 14/15 expose only incomplete/unrelated material, not a sufficient answer.
No abstention or Qwen behaviour is scored or inferred.

## What changed in case 08

The strict eight child hits represented only five original parents. The best
child of adult assessment parent `source-01-004` was original child rank 11,
cosine **0.3899381161**, above threshold but outside child top-eight. It becomes
unique-parent rank **8**, is selected, and the unchanged packer delivers its full
original passage. That passage supplies adult airway positioning, see/listen/feel,
and **up to ten seconds** to determine normal breathing, satisfying the complete
previously missing item. The timing tail's separate child is much lower ranked;
the admitted full parent, not the prefix child alone, supplies the complete item.

The other additions are an unconscious-person/113 summary (`source-01-002`) and
near-duplicate 116117 contact passage (`source-03-009`). More contact text is not
rewarded. Coverage rises to 75%, not a complete pass. Existing child/baby airway
procedures remain alongside the new adult procedure. Their explicit age headings
are retained; the potential wrong-age misapplication flag is retained, not an
assertion of a false source statement or an observed generated error.

## Remaining failures and candidate evidence

Ranks are in the saved NO/general child candidate landscape unless explicitly
marked unique-parent ranks. Best relevant refers to the specific missing need,
not merely any passage from the correct document. Scores are unchanged from C8.

| Case | Specific evidence / location | Why still missing |
| --- | --- | --- |
| 01 | Fracture suspicion/assessment best child 0.294786; immobilisation parent best child 0.347157 | Relevant information remains below 0.35; dedup cannot admit it. Rest/non-loading is only a partial composite item. |
| 04 | Complete lost-person original passage best child 0.335254 | Below threshold; unrelated candidates dominate delivered context. |
| 06 | Initial major-bleeding 113 passage best child 0.233094 | Far below threshold. Other 113 triggers are not equivalent to the required initial instruction. |
| 07 | Treatment `source-03-006`: original child rank 7, unique-parent rank 6, 0.463374 | Search succeeds; treatment packet would make prompt 2,246 tokens and is rejected against 2,000. Newly selected RICE packet would make 2,370 and is also rejected. |
| 08 | HLR/absent-abnormal-breath decision child rank 35, 0.316060 | Adult assessment selection fixed; remaining required decision still below threshold. |
| 12 | Brown-water warning `source-14-005`: child rank 11, unique-parent rank 10, 0.414866 | Above threshold but outside eight unique parents. Added rank-eight parent concerns ice rescue, not the missing river condition, and is rejected at 2,291 tokens. |
| 13 | Beacon activation `source-11-003`: child rank 23, unique-parent rank 22, 0.396384 | Above threshold but well outside selection. Correct-document product comparisons do not contain the required activation instructions. |

This experiment confirms duplicate-child slots can hide a useful parent, but
does not establish that they are the main bottleneck. It does not change cosine
scores, solve the substantial remaining ranking/threshold failures, remove noise,
or solve atomic section-packet budget rejection. No new covered-case KB gap was
identified. Original insufficient-coverage cases remain gaps.

## One possible next experiment — NOT run

A **packing-only ablation on the fixed saved C8U8 seeds**: original seed-parent
context only versus the current narrow section expansion, keeping seed order,
selection, budget, tokenizer, scores and gold unchanged. This would test whether
expansion/atomic packet size is withholding already-selected useful treatment,
especially case 07. It could lose multi-section information, so all 15 frozen
cases must be evaluated, not only the burn case. Do not combine it with threshold,
model or ranking changes. This is a proposal requiring owner review, not a fix
implemented or a result claimed.

## Uncertainty and integrity

Manual scoring has one annotator. Existing C8 annotations are copied unchanged;
candidate decisions use inspected new text and exact quotes/offsets. Partial
conditions receive no full credit. Optional details do not increase coverage.
Noise is case-level and can remain unchanged even when extra irrelevant text is
added; context-size metrics capture that cost. Potential misleading findings are
scenario-mismatch risks, not measured downstream generation failures. Case 08's
retained wrong-age-risk flag, with the now-present adult instructions, remains
open to owner review without altering frozen gold.

Zero leakage on this small set does not prove global geography correctness.
US-published general hygiene advice is not automatically US-jurisdiction leakage;
delivered legal/geographic applicability is what is evaluated. Raw candidate
lists intentionally retain original C8 `selected` flags; the candidate's actual
selection is explicitly recorded in `C8U8/*/retrieved.json` and
`selection-audit.json`, not inferred from those baseline flags.

Raw/source-bearing artifacts stay ignored/local:
`knowledge/local/diagnostics/retrieval-parent-dedup-v1-2026-10-07/`.
They include frozen protocol/runtime/input hashes, unchanged corpus/manifest and
child index/vector snapshots, all query vectors and all-candidate scores, copied
C8 outputs, C8U8 selection/packing traces, all 30 delivered contexts and unexecuted
prompts, tokenization outputs, manual scoring/evidence offsets, budget analysis,
per-case/aggregate metrics and final verification/hash inventory.

Repository artifacts are this report, `retrieval_parent_dedup.v1.json`,
`run_retrieval_parent_dedup_v1.py`, `score_retrieval_parent_dedup_v1.py` and
`verify_retrieval_parent_dedup_v1.py` (saved-output integrity checks only).
They are diagnostics only, not production configuration changes.

The saved-score experiment ran with bundled Python 3.12.14/NumPy 2.3.5 and the
existing pure-Python YAML package; no installs/downloads/native embedding calls.
Exact-hash tokenizer outputs were reused, with the same offline llama-tokenize
executable/GGUF for new strings. Scripts refuse overwriting an existing run or
scoring file. `summarize` recomputes metrics from saved annotations only; inspect
saved outputs rather than rerunning this experiment. Reproduction snapshots pin
the code, data, config and tokenization assets; the completed raw run is preserved.

Gold SHA-256: `04ad519f56cfff4fc4158af1975363a142b06d84c84d8f7e842a1095d07868c4`.
Corpus SHA-256: `bd954cd27111854db2a54a8b05335dac8be7776301060da2cce3dfedb2a33d20`.
Experiment SHA-256: `8e51a27c4c9b96ba7d0b0900cb706a3bbda2a6bd74f5dc8c4fe3a4cb7d4b6efc`.

All protected production/gold/corpus/manifest/model hashes and previous C8 inputs
unchanged. Baseline retrieval calls: **0**; embedding calls: **0**; generation
calls: **0**. One candidate-selection experiment, no new chunking variants.
**Stopped for owner review.**
