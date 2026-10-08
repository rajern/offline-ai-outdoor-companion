# Retrieval failure diagnosis — frozen v1 evaluation

Diagnosis only, 2026-10-07. No production changes, gold edits, new retrieval
variants, embedding inference, index rebuild, query rewriting or Qwen generation.
The next experiment described below has **not** been run.

## Method and scope

The same eleven supported cases failed both A and B in the last controlled
comparison. This analysis maps every missing must-have item to actual, applicable
stored passages, including semantic alternatives outside the preferred document.
It does not treat finding an article or a link to un-ingested material as coverage.

- Reused the exact saved original-query vectors from the last evaluation.
- Read the current production corpus and embedding index, validated their hashes,
  and applied exactly the production float32 normalisation and cosine operation.
- Examined all 190 indexed passages. Main ranks below are among the **161
  geographically applicable NO/general passages before the 0.35 score filter**.
  Global ranks and excluded passages are saved separately.
- Verified that reconstructing the unchanged 0.35/top-3 selection reproduces the
  original production results for every case, including the empty lost-case result.
- Inspected the existing embedding tokenizer's actual 128-token truncation using
  its deployed loader/config. A diagnostic untruncated tokenizer clone measures
  length only; no embeddings/tokenizer assets or runtime settings were changed.
- All eleven original queries fit within 128 tokens. **Query truncation is not
  the cause.** Existing stored chunk bodies can be much longer.
- Every one of the **31 missing A items / 30 missing B items** has applicable
  information in the current corpus. Case 06 is the only A-only difference: B
  already recovered monitoring/warmth by section expansion.

Evidence is information-based. IDs below identify inspected evidence locations,
not required IDs for a retrieval pass. Quote/character offsets, alternative
passage combinations and token-visible portions are saved in the local artifacts.

## Per-case findings

Scores are cosine similarity, not probabilities. Multiple rank/score entries
identify different missing requirements. For case 06 the table emphasises the
still-missing B requirement; its A-only missing passage is reported immediately
below the table. For case 08, the best complete adult-assessment alternative is
included rather than requiring the preferred source identity.

| Case | Missing must-have information | Best relevant rank(s) | Score(s) | Actual corpus location | Primary category | Secondary category |
| --- | --- | ---: | ---: | --- | --- | --- |
| 01 Ankle/fracture | Fracture suspicion, diagnostic uncertainty, medical assessment, immobilisation/movement harm | 6 for immobilisation; 20 for suspicion/assessment | 0.341193; 0.294786 | Helsenorge, `source-04-006` Hva er brudd? / Førstehjelp ved brudd; `source-04-005` Hva er brudd? | ranking / embedding | top_k / threshold; multi-section requirement |
| 03 Drinking water | Both altitude-qualified boiling rules; chemical/toxin limitation and alternative source | 11; 13 | 0.448537; 0.440370 | CDC `source-21-010` Treat your water / Boil; `source-21-009` Treat your water | ranking / embedding | multi-section requirement |
| 04 Lost in fog | All five immediate lost-person actions | **1** | **0.335254** | DOC `source-09-007` Reduce your risk of getting lost / If you get lost | top_k / threshold | None |
| 05 Lightning ridge | Leave heights, do not shelter under overhang, outdoor measures only reduce risk | 8 | 0.406440 | NWS `source-22-004` Last Resort Outdoor Risk Reduction Tips; combines with already-returned `source-22-002` at rank 2 | top_k / threshold | multi-section requirement |
| 06 Severe bleeding | Initial 113 escalation for major/uncontrolled bleeding | 44 | 0.233094 | Helsenorge `source-02-006` Når skal du ringje 113? | ranking / embedding | multi-section requirement |
| 07 Adult hand scald | Cooling conditions, no ice, do not puncture blisters, hand assessment | 4 for assessment; 5 for treatment | 0.479880; 0.464033 | Helsenorge `source-03-007` Når bør du oppsøke helsehjelp?; `source-03-006` Førstehjelp ved brannskader | top_k / threshold | chunk / representation; multi-section requirement |
| 08 Unconscious adult | Full adult airway/breath assessment; monitoring plus abnormal-breath HLR/113 decision | 9 for complete adult assessment; 25 for decision/monitoring | 0.380829; 0.313416 | Helsenorge `source-01-004` HLR på voksne / sjekk pusten; `source-07-005` Sjekk for normal pust | ranking / embedding | chunk / representation; top_k / threshold; multi-section requirement |
| 10 Overnight equipment | Sleeping/survival insulation and emergency shelter | 6 | 0.483331 | DOC `source-12-002` Personal equipment; both missing facts in the actual equipment list | top_k / threshold | multi-section requirement |
| 11 Toilet hygiene | Burial depth/water distance and downstream placement | **4** | **0.583929** | CDC `source-21-015` Bury your poop; both missing requirements in one complete passage | top_k / threshold | multi-section requirement |
| 12 Brown high river | Brown-water warning; stop on flood, doubt or inadequate skill | 4 for stop conditions; 7 for brown-water warning | 0.449099; 0.414866 | DOC `source-14-006` Do not cross if there is any doubt; `source-14-005` Know the signs of an unsafe river | top_k / threshold | multi-section requirement |
| 13 Distress beacon | Activate in life danger, earlier help, activate if unsure rather than wait | 16 | 0.396384 | DOC `source-11-003` Call for help early; all required information in one short applicable passage | ranking / embedding | None |

### Additional passage details

- **01:** Both necessary fracture passages are below threshold. RICE ranks 4 at
  0.346151, but is not a substitute for fracture suspicion/assessment. Merely
  lowering threshold would not move the assessment passage from rank 20 into top 3.
  All fracture gold facts are visible to at least one embedding view; the
  immobilisation/movement-harm facts are visible in both. The long splinting tail
  is truncated, but is optional, not the reason these core facts fail.
- **03:** Boiling and chemical limitations are well above threshold and therefore
  excluded by rank/top-3 selection, not the score cutoff. Full boiling instructions
  fit both embedding views. The chemical passage loses its alternative-source
  ending in the title/section view, but the body-only embedding sees it all.
  Required facts lie in separate risk, treatment/overview and procedure sections;
  overview text cannot substitute for the procedure. Irrelevant property-flood
  instructions rank 1 at 0.619180.
- **04:** A single complete general lost-person passage covers all five items,
  fits both embedding views, and ranks first. Its 0.335254 score is excluded by
  the fixed 0.35 threshold. This is the cleanest direct threshold failure.
- **05:** The missing last-resort passage fits all necessary statements in both
  embedding views. Rank 8 is outside top 3 but above threshold. Its risk-reduction
  introduction plus the already-retrieved general no-safe-outdoor-place statement
  jointly provides the full safety qualification. No new gold inference is needed.
- **06:** A also omitted `source-02-009` Overvak og hald kroppstemperaturen oppe,
  rank **22 / 0.292570**. B retrieved it by expansion despite its own low cosine.
  Initial major-bleeding escalation remains absent because it is in a different
  section at rank 44. Both are short, fully represented passages, so token
  truncation does not explain their poor scores.
- **07:** The treatment body has **240 embedding tokens**, versus a 128-token
  limit (254 with title/section). The no-blister-puncture fact is beyond the
  retained prefix in **both** views. Cooling and no-ice instructions are visible.
  The complete stored text is still retrievable as one passage at rank 5, and
  hand assessment is immediately before it at rank 4. Thus near-cutoff exclusion
  is the direct primary cause; representation is an observed secondary weakness.
  The approved cream/ointment conflict is excluded from gold and diagnosis of
  required coverage, as requested.
- **08:** The preferred adult airway passage `source-07-004` ranks
  **16 / 0.351135**, but the alternative adult HLR assessment passage at rank 9
  covers the whole airway/10-second item. Child and baby airway passages rank
  **3 / 0.446371** and **5 / 0.401707**, above both adult alternatives.
  The preferred normal-breath decision passage has **201 body tokens / 221 with
  title/section**. Its HLR, 113 clarification and monitoring tail is omitted from
  both embedding views. It remains complete in stored text at rank 25.
  The alternative combination of `source-07-007` monitoring
  (**23 / 0.321691**) and `source-01-001` HLR/113 guidance
  (**27 / 0.303765**) also lies below threshold. That short HLR passage fits both
  views, so truncation alone does not explain the whole case.
- **10:** The complete actual equipment list ranks 6, while its introduction
  ranks 3 and resource links rank 5. The body is exactly 128 tokens and retains
  all facts; the longer title/section view drops the emergency-shelter ending.
  An alternative tent passage is at **21 / 0.362361**; an emergency-shelter
  packing passage in the river article is at **36 / 0.333919**. These are
  acceptable information alternatives, not required sources. The sleeping mat
  remains optional. No full fact is absent from both primary embedding views.
- **11:** The complete burial passage is short (82 body / 109 title-context
  tokens), fully represented and applicable. It is displaced by property-flood
  text at rank **3 / 0.601642**. This is a direct top-3 boundary failure.
- **12:** Both missing river passages are short, complete and fully visible in
  both views. The currently delivered wait/turn-back section cannot substitute
  for their different required warning signs and stop conditions.
- **13:** One short activation passage (79 body / 98 title-context tokens)
  contains all requirements, is fully represented and geographically applicable.
  Three phone-only 113 passages rank above it, at scores 0.548369, 0.538833 and
  0.512825. It is not excluded by geography or threshold, not a multi-section
  collection problem, and not missing from the corpus.

## Aggregate interpretation

Primary categories sum to eleven cases. They are diagnostic judgements, not
causally proven model defects. Here, a *near cutoff* means necessary passages
at single-digit ranks **4–8**, above threshold, or the rank-1 threshold failure.
The boundary between a rank-8 cutoff issue and a ranking issue is not absolute.
All exact ranks are provided so the owner can inspect that classification.

| Category | Primary cases | Secondary cases |
| --- | ---: | ---: |
| top_k / threshold | **6** (04/05/07/10/11/12) | 2 (01/08) |
| ranking / embedding | **5** (01/03/06/08/13) | 0 |
| chunk / representation | 0 | **2** (07/08: necessary information excluded from both embedding views) |
| multi-section requirement | 0 | **9** (all except 04/13) |
| knowledge-base gap | **0** | 0 |
| other | 0 | 0 |

Five near-cutoff cases have all still-missing required passages between ranks
4 and 8 above threshold. The sixth is the lost case: complete information ranks
first but is below threshold. The other five have essential information at
rank 11–44 or otherwise poorly ranked, sometimes also below threshold.

Nine cases require combining sections for the complete case, including facts
already present in A/B. This count does not mean nine independent primary
multi-section defects. It explains why returning one relevant overview or
article cannot suffice. All missing information has a complete stored passage
or valid passage combination; none requires inventing missing source material.

## Main bottleneck and one proposed next experiment

The strongest overall observation is **candidate selection before context
packing**: useful information exists, but production's three selected passages
and fixed threshold do not admit it. The local/near-cutoff component affects
six cases; severe relative ranking affects five. Narrow packing cannot repair
unrelated seeds or missing sibling sections. There is no basis to blame KB
coverage or Qwen for these eleven retrieval failures.

The data does **not** establish that the embedding model alone is at fault.
Cosine ranking reflects the model, averaged body/title representation and
existing truncation together. Truncation is directly observed; its causal
effect on scores needs a separate controlled experiment, not asserted here.

**Propose one next experiment: a top-k-only ablation, B with three versus eight
original semantic seeds**, keeping the corpus, index, original questions,
0.35 threshold, narrow-packing algorithm, tokenizer and 2,000-token complete
prompt budget unchanged. No production change.

Hypothesis: near-top-3 candidate starvation explains the five above-threshold
near-cutoff cases. Compare strict frozen must-have coverage, complete cases,
noise, geography and context size. Log every budget-excluded packet separately
so budget effects are not mistaken for rank failures. Do not refill below the
original top eight or silently truncate instructions.

This tests one variable rather than jointly lowering threshold, changing
embeddings or rewriting queries. It will not solve the rank-1 threshold case,
the far-down-ranking cases or the representation problems by itself. An outcome
with more coverage but substantially more noise is evidence, not an automatic
production recommendation. **Experiment not run; owner review required.**

## Artifacts, integrity and remaining uncertainty

Diagnostic script: `evals/diagnose_retrieval_failures_v1.py`.

Raw/source material remains in the ignored local directory:
`knowledge/local/diagnostics/retrieval-failure-landscape-v1-2026-10-07/`.

- `diagnostic-config.json`: input hashes, definitions, runtime versions,
  effective production parameters and protected-file hashes.
- `case-XX/all-candidates.json`: all 190 candidates, text and metadata,
  exact cosine, global/applicable rank, unchanged-threshold eligibility.
- `case-XX/missing-information.json`: every missing item, corpus evidence,
  alternative sufficient combinations, character offsets, both embedding
  prefixes and whether individual facts were visible/truncated.
- `case-XX/original-query-vector.npy`: exact original saved query vector.
- `diagnosis.json`: per-case findings and primary/secondary aggregation.
- `integrity-after.json`: all protected files unchanged.

Gold SHA-256: `04ad519f56cfff4fc4158af1975363a142b06d84c84d8f7e842a1095d07868c4`.
Corpus SHA-256: `bd954cd27111854db2a54a8b05335dac8be7776301060da2cce3dfedb2a33d20`.
Vector SHA-256: `1952356b4aef70c0a10fff752071bce511c61f7d8a31bdf6bd97a0d140d1a09d`.

Semantic equivalence follows the frozen owner-reviewed criteria; no gold/scoring
changes were made. Case 05 retains the preceding evaluation's conservative
explicit-information boundary. Cases with multiple categories are not counted
twice in primary totals. No claim of unique causal attribution is made.

One non-causal metadata defect was observed in the prior frozen experiment:
unquoted `NO` in the protocol YAML was serialised as boolean `false` by its
YAML-1.1 reader. The actual production service and expansion code used the string
`NO`, and exact replay plus actual passage checks confirm the correct filter.
This does **not** change previous results or explain the failures. The frozen
protocol/output is preserved; this discrepancy is documented, not silently fixed.

Verification: all original production selections reproduced, all mapped quotes
validated in geographically applicable current passages, all original queries
untruncated, and all protected corpus/model/production/gold hashes unchanged.
New retrieval variants: zero. Embedding inference calls: zero. Qwen generation
calls: zero. **Stopped for owner review.**
