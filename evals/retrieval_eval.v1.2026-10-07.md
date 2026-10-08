# Retrieval-only A/B evaluation — 2026-10-07

B is not a clear improvement. It retrieves one additional required information
item, produces no additional complete case passes, and increases context size
and irrelevant context. Neither configuration meets the agreed qualitative MVP
acceptance bar. This does not assess Qwen generation or imply that generation
quality is adequate.

## Frozen experiment

Exactly 15 Norwegian questions, two configurations, one retrieval call per
question. Thirteen supported-context cases and two KB-coverage gaps. No answer
generation, new models, corpus/index changes or production modifications.

- A: current `SemanticRetrievalService.retrieve(question, top_k=3)` results,
  including production cosine threshold 0.35 and NO/general geography filtering.
  All results are delivered unchanged; no baseline truncation.
- B: the identical three ranked semantic seeds, with only narrow section-context
  packing changed. Existing generic nearest-branch expansion rule, same-document
  and same geography constraints, corpus-order passages, duplicate removal and
  atomic budget admission. No child embeddings, lexical fusion, reranking,
  below-rank-three refill or source-specific rules.
  Expanded B passages carry their packet seed's score for provenance/prompt
  serialization, not an independently computed cosine or a new ranking. Exact
  seed scores and expansion membership are recorded separately in the traces.
- Common budget: 2,000 tokens for the unmodified complete production grounded
  prompt, measured using the existing locked GGUF's `llama-tokenize`. Context
  tokens below count the actual serialized knowledge blocks separately.
  Tokenization is not generation. Chat-template overhead is excluded, consistently
  with the preceding context experiment. No packet exceeded the budget; the
  budget therefore did not cause any observed retrieval failure.
- Strict binary item coverage: necessary conditions and all constituent facts
  must be present. Partial facts score zero. Header information counts only when
  actually serialized into delivered context. Optional/supporting material cannot
  compensate for missing must-have facts. No exact chunk ID is a pass criterion.
- The protocol/configuration and input hashes were saved before new results were
  generated. Gold review labels were left untouched; this run was explicitly
  authorized by the owner's latest request.

## Aggregate metrics

All following denominators and size summaries concern the **13 supported cases**.
Complete pass measures all must-have facts, not absence of noise. Noise is reported
separately, including in cases that completely cover the required information.

| Metric | A: production | B: narrow packing |
| --- | ---: | ---: |
| Fully covered must-have items | 20/51 (39.2%) | 21/51 (41.2%) |
| Average per-case coverage | 37.7% | 39.6% |
| Complete cases | 2/13 (15.4%) | 2/13 (15.4%) |
| Irrelevant-context cases | 11/13 (84.6%) | 12/13 (92.3%) |
| Potentially misleading-context cases | 4/13 (30.8%) | 4/13 (30.8%) |
| Either irrelevant or potentially misleading | 11/13 (84.6%) | 12/13 (92.3%) |
| Jurisdiction leakage | 0/13 cases, 0 passages | 0/13 cases, 0 passages |
| Context tokens: mean / median / maximum | 433.8 / 474 / 702 | 618.6 / 666 / 1,267 |
| Delivered chunks: mean / median / maximum | 2.77 / 3 / 3 | 3.92 / 4 / 8 |
| Unique sections: mean / median / maximum | 2.69 / 3 / 3 | 3.46 / 3 / 8 |
| Complete prompt tokens: mean / median / maximum | 623.2 / 654 / 901 | 808.1 / 865 / 1,457 |

B increases mean context tokens by 42.6%, for one additional covered information
item (+2.0 percentage points micro coverage). No covered case loses information,
but none gains a complete pass. Only case 06 gains a fully covered item.

## Per-case inspection

Scores are fully covered items / required items, not chunk or source matches.
Both configurations pass only cases 02 and 09.

| Case | A | B | Finding |
| --- | ---: | ---: | --- |
| 01 Ankle / possible fracture | 0/4 | 0/4 | Ice self-rescue and preparation, no fracture assessment or protection. |
| 02 Wet, cold companion | 5/5 | 5/5 | Correct treatment at semantic seed rank 3 suffices alone. B additionally packs unrelated unconscious-person procedures. |
| 03 Stream drinking water | 2/5 | 2/5 | Clear-water risk and treatment need retrieved; both altitude-qualified boiling rules and chemical/toxin limitation absent. Flood/property advice dominates the highest-ranked seed. |
| 04 Lost in fog | 0/5 | 0/5 | No production candidate above the unchanged 0.35 threshold. B has nothing to expand. |
| 05 Lightning on ridge | 3/6 | 3/6 | General lightning danger and proper shelter present. Ridge departure, explicit overhang exclusion and last-resort outdoor risk-reduction guidance missing. Lost-person advice is unrelated. |
| 06 Severe bleeding | 2/4 | 3/4 | Pressure and over-bandaging present. B adds warmth/monitoring/113 on deterioration, but neither supplies the initial major-bleeding 113 criterion. Minor-cut advice also retrieved. |
| 07 Adult hand scald | 0/4 | 0/4 | Burn symptoms, abrasion care and drinking-water boiling instead of adult cooling, no-ice/no-blister-puncture and hand assessment. B expands water treatment to six passages. Cream advice is excluded from scoring. |
| 08 Unconscious adult | 2/4 | 2/4 | 113 and proper side position present; full adult airway/breath assessment and abnormal-breath CPR branch missing. B adds monitoring but not the whole final item. Paediatric instructions remain. |
| 09 Hot-day prevention | 3/3 | 3/3 | Correct prevention passage alone suffices; care-service evacuation text remains extraneous. |
| 10 Unexpected night / gear | 1/3 | 1/3 | Delivered warm-clothes heading plus bad-weather preparation covers item 1. Sleeping/survival insulation and emergency shelter absent. Gear-list introduction is not the actual gear list. Sleeping mat is optional. |
| 11 Toilet and hand hygiene | 1/3 | 1/3 | Hand hygiene and 60% sanitizer present. Waste depth/water distance and downstream placement absent; household flood advice unrelated. |
| 12 Brown, high river | 1/3 | 1/3 | Wait/turn back present. Brown-water danger criterion missing; high-flow avoidance alone lacks the doubt/inexperience conditions of the composite item. Property mitigation adds noise. |
| 13 Distress beacon | 0/2 | 0/2 | Three phone-only 113 passages replace beacon activation guidance despite no mobile coverage. B expands into first-aider aftercare, wrist casting and burn criteria. |
| 14 Avalanche signs | Separate gap | Separate gap | Both cover 1/2 of the supported subset; neither retrieves competence/terrain-avoidance guidance. Explicit whumph/crack interpretation and retreat are absent from the KB. Ice rescue and accident-story links add noise. |
| 15 Norwegian campfire law | Separate gap | Separate gap | No applicable legal coverage exists; unrelated water/flood/preparation context returned. No NZ fire-rule leakage observed. Empty must-have list is not a pass. |

### Insufficient-coverage cases

Neither gap case enters normal coverage, complete-pass or noise denominators.
No retrieval refusal or LLM abstention is scored. The actual context does not
cover the missing knowledge; absence of an answer in the KB is not a retrieval
ranking failure for that missing information.

| Case | A chunks / context tokens | B chunks / context tokens | Geography |
| --- | ---: | ---: | --- |
| 14 Avalanche | 3 / 831 | 4 / 1,050 | No observed leakage |
| 15 Campfire | 3 / 502 | 9 / 1,387 | No observed leakage; NZ-specific fire article not delivered |

## Main failure modes and interpretation

1. **Wrong semantic seed or absent seed.** An ankle query gets ice rescue; a
   beacon query gets duplicated phone-call text; the lost query has no eligible
   result. Narrow packing cannot recover information in an unrelated branch.
2. **Correct article, wrong instructional section.** Drinking-water risk is not
   the boiling procedure; burn symptoms are not treatment; toilet hygiene overview
   is not the required waste-placement instructions. Article identity is insufficient.
3. **Narrow sections do not necessarily contain the needed neighbouring branch.**
   Bleeding treatment expansion adds monitoring but not the initial escalation
   section. An adult airway assessment is not recovered by expanding side position.
4. **Noise is amplified along with useful context.** Burn and beacon queries
   expand irrelevant source branches, sometimes markedly, without gaining gold facts.
5. **Some composite requirements remain partially present.** A correct phone
   number with a different trigger, monitoring without abnormal-breath action, or
   flood avoidance without the required doubts/skills conditions is not full coverage.

This is evidence of a retrieval information-selection bottleneck under the
current configuration. It does not isolate embedding quality from corpus/chunk
representation or threshold/ranking effects, and says nothing about Qwen's
ability to use clean context. No further experiment or fix is performed.

## Evaluation uncertainties

- Scoring is a single manual semantic assessment, not an independent multi-reviewer
  adjudication. All positive and partial evidence quotes, reasons and offsets are
  stored for owner review. No model grades its own output.
- Case 05 is scored conservatively: general outdoor-unsafety does not automatically
  provide the explicitly required overhang exclusion or last-resort risk-reduction
  item. Those semantic boundary judgements are highlighted, not used to revise gold.
- Case 10's warm-clothes fact comes from the actual delivered `Tema` heading;
  counting it is information-based, not credit for an unshown source section.
- Noise labels are more subjective than explicit missing facts. The four potentially
  misleading cases (06/07/08/13) contain wrong-severity, wrong-injury, wrong-age or
  unavailable-channel instructions. This means risk of misapplication, **not**
  observed generation errors or proof the source advice itself is incorrect.
  Preserved conditional advice is not automatically marked conflicting.
- No geography leakage observed in these 15 questions is not a universal guarantee.
  Publisher-country attribution is not jurisdiction leakage. The existing approved
  passage-level metadata remains unchanged.
- This B is intentionally the same production parent-ranking plus packing only,
  not earlier experiments that also changed to token-sized child ranking. Findings
  apply to this explicitly frozen two-configuration comparison and this small set.
- The burn-source cream conflict remains documented, excluded from all success/noise
  decisions as requested. No final safety policy is approved by this evaluation.

## Saved artifacts and reproducibility

Public evaluation definitions/scripts (no copied raw articles):

- `evals/retrieval_protocol.v1.yaml`
- `evals/run_retrieval_eval_v1.py`
- `evals/score_retrieval_eval_v1.py`
- This report.

All raw material is saved locally under the ignored directory
`knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07/`:

- `frozen-run.json`: configuration, runtime versions, protected-file hashes.
- Gold/protocol/runner, corpus, manifest, production index/vector snapshots.
- `case-XX-query-vector.npy`: exact vectors used by production retrieval.
- `A/results.json`, `B/results.json`: aggregates and all per-case annotations,
  versions/hashes, configuration and raw-context paths.
- `A/case-XX/`, `B/case-XX/`: raw context, unexecuted serialized prompt,
  ranked seeds with full metadata/scores, expanded excerpts, packet/budget trace
  and exact tokenizer counts/identifiers.
- `tokenization/`: inputs, token IDs, process arguments/status and stderr.
- `scoring.json`, `scoring-with-offsets.json`: strict manually authored item
  decisions, partial evidence, optional notes, noise and geography inspection.
- `aggregate.json`, `retrieved-all.json`, `integrity-after.json`.

Input hashes:

| Artifact | SHA-256 |
| --- | --- |
| Gold v1.0.0 | `04ad519f56cfff4fc4158af1975363a142b06d84c84d8f7e842a1095d07868c4` |
| Corpus | `bd954cd27111854db2a54a8b05335dac8be7776301060da2cce3dfedb2a33d20` |
| Protocol v1.0.0 | `0103124bae370c7c087e9156afcf82e30f865edb040ce5fa658f70257cdd1165` |
| Production vectors | `1952356b4aef70c0a10fff752071bce511c61f7d8a31bdf6bd97a0d140d1a09d` |
| Run script | `e75d882ee9f5a6792749fb212c23cd5c8744838da6ffcdbe9c62f3a573b3b736` |
| Manual annotation script | `119af909589ae90633433fb357033d0c77c3d80a438d9803da58b34f7891b857` |

Verification: all 30 contexts and evidence quotes validated; same ordered seeds
for both modes in every case; A exactly equals the production results; all prompts
within budget; no additional variants; all protected input hashes unchanged,
including gold, source manifest, production code, embedding assets and GGUF.
Generation calls: zero. **Stopped for owner review.**
