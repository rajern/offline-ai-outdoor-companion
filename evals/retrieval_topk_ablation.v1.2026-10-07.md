# Retrieval top-k ablation — B3 versus B8

One controlled retrieval-only experiment, 2026-10-07. Completed; stopped for
owner review. No production, gold, corpus, model, prompt or embedding changes.
No generation calls, embedding inference or additional retrieval variants.

## Scope and controls

The preceding diagnosis proposed testing candidate starvation just outside top 3.
This experiment changes only the number of original semantic seeds scanned by
the existing narrow section packer: **B3 = 3; B8 = 8**. Neither is installed as a
production change. B3 is the previous experimental B, not production A.

All 15 frozen questions were evaluated with identical original query vectors,
190 stored passages / 22 documents, index, float32 cosine ranking, NO/general
filter, 0.35 threshold, tokenizer and packing algorithm. Exact protected hashes
match the prior evaluation. Parameters were saved before inspecting B8 results
in `retrieval_topk_ablation.v1.json` and the local `frozen-run.json`.

The **2,000-token budget applies to the complete unmodified grounded prompt**,
including source headers and existing instructions/question. Serialized context
tokens are reported separately. As before, tokenizer counts exclude any eventual
chat-template overhead. Prompts were saved, never executed. Expanded passage
scores are inherited seed scores, not independent cosine scores.

Packing is unchanged: narrow heading-branch expansion, corpus order,
deduplication, atomic packet admission; skip an over-budget packet and continue
with the remaining original seeds. No eviction, truncation or refill below top 8.
B3 reproduced all previous excerpts, packing traces, token counts and contexts
exactly. Every B8 context retains B3 as an exact excerpt prefix.

Strict information-based scoring is inherited unchanged. Every must-have item is
binary, with incomplete conditions scoring zero. Optional material/source counts
cannot earn coverage. B3 annotations are copied unchanged; newly delivered B8
facts/noise were manually inspected. Evidence quotes and offsets are saved.
Supporting sources are not required where applicable context already supplies
all required information. No exact chunk identity is a pass criterion.

## Aggregate results — 13 covered cases only

| Metric | B3 | B8 |
| --- | ---: | ---: |
| Must-have coverage (micro) | 21/51 = 41.18% | 34/51 = 66.67% |
| Average per-case coverage (macro) | 39.62% | 65.38% |
| Complete must-have passes | 2/13 = 15.38% | 7/13 = 53.85% |
| Cases with irrelevant context | 12/13 = 92.31% | 12/13 = 92.31% |
| Cases with potentially misleading context | 4/13 = 30.77% | 5/13 = 38.46% |
| Cases with either noise category | 12/13 = 92.31% | 12/13 = 92.31% |
| Observed jurisdiction leakage | 0/13 | 0/13 |
| Context tokens: mean / median / maximum | 618.62 / 666 / 1,267 | 1,311.38 / 1,524 / 1,770 |
| Complete prompt tokens: mean / median / maximum | 808.08 / 865 / 1,457 | 1,500.85 / 1,723 / 1,969 |
| Retrieved passages: mean / median / maximum | 3.92 / 4 / 8 | 8.69 / 10 / 12 |
| Distinct sections: mean / median / maximum | 3.46 / 3 / 8 | 8.00 / 9 / 12 |
| Covered cases with rejected budget packets | 0/13 | 4/13 |
| Rejected packets in covered cases | 0 | 5 |

Micro coverage improves by **25.49 percentage points**, with **five additional
complete passes**. Mean context size increases **2.12x**. No case loses must-have
coverage. A complete pass only means all must-have facts are present: it does not
cancel a separate noise finding or establish generation readiness.

## All cases

Numbers are fully covered must-have items / required items, not partial credit.
Tokens are serialized context tokens. All nonempty covered contexts contain
irrelevant material; the empty lost-case context does not.

| Case | B3 → B8 | Context tokens B3 → B8 | B8 outcome / explanation |
| --- | --- | ---: | --- |
| 01 Ankle / possible fracture | 0/4 → 0/4 | 600 → 600 | Fail: fracture passages remain below 0.35; higher k cannot admit them. Wrong ice/preparation context unchanged. |
| 02 Cold, wet companion | 5/5 → 5/5 | 855 → 1,412 | Pass unchanged; extra symptoms, equipment and unrelated water/ice text do not improve score. |
| 03 Stream drinking water | 2/5 → 5/5 | 700 → 1,716 | New pass: complete altitude-qualified boiling rule and chemical/toxin limitation delivered through rank-5 Disinfect branch expansion. Property-flood noise remains. |
| 04 Lost in fog | 0/5 → 0/5 | 0 → 0 | Fail: best complete passage ranks first but scores 0.335254, below unchanged threshold. |
| 05 Lightning on ridge | 3/6 → 6/6 | 300 → 1,436 | New pass: rank-8 last-resort passage supplies leave-heights, no-overhang and qualified risk reduction. Avalanche/flood/lost-person noise remains. |
| 06 Persistent major bleeding | 3/4 → 3/4 | 598 → 1,091 | Fail: initial major/uncontrolled-bleeding 113 instruction remains rank 44 / 0.233094. 113 for internal bleeding or deterioration is not the same trigger. |
| 07 Scalded hand | 0/4 → 1/4 | 1,267 → 1,635 | Fail: hand assessment admitted at rank 4; rank-5 treatment packet rejected at 2,162 prompt tokens. Cooling, no ice and no blister puncture absent from delivered context. |
| 08 Unconscious adult | 2/4 → 2/4 | 780 → 1,524 | Fail: full adult assessment best rank 9, outside top 8; adult HLR/decision branch remains low/below threshold. Child/baby and hypothermia-specific procedures are inappropriate substitutes. |
| 09 Heat prevention | 3/3 → 3/3 | 474 → 1,592 | Pass unchanged, but new cold-rescue movement advice is potentially misleading in heat prevention. |
| 10 Unexpected night out | 1/3 → 3/3 | 263 → 842 | New pass: rank-6 equipment list supplies sleeping/survival insulation and emergency shelter. Sleeping mat remains optional. |
| 11 Toilet hygiene | 1/3 → 3/3 | 666 → 1,770 | New pass: rank-4 burial passage supplies depth, distance and downstream placement; existing hand hygiene completes gold. Unrelated hypothermia/burn text added. |
| 12 High, brown river | 1/3 → 3/3 | 862 → 1,724 | New pass: rank-4 stop conditions and rank-7 brown-water warning supply all missing facts. Property/ice noise remains. |
| 13 Distress beacon, no phone | 0/2 → 0/2 | 677 → 1,706 | Fail: activation policy remains rank 16, outside top 8. Merely mentioning carrying a beacon is not activation guidance. Phone-only instructions remain inappropriate. |
| 14 Avalanche signs — KB gap | Supported subset 1/2 → 1/2 | 1,050 → 1,749 | Separate gap: no actual whumph/crack interpretation or operational retreat coverage. Extra ice guidance does not supply missing avalanche competence information. |
| 15 Norwegian campfire law — KB gap | No applicable gold facts | 1,387 → 1,605 | Separate gap: no Norwegian fire-law coverage in either context. Unrelated water/flood material; no NZ fire-law leakage observed. No zero-item pass awarded. |

## Interpretation and concrete failure modes

1. **Candidate starvation is real, but not the entire bottleneck.** Four of the
   five predicted above-threshold near-cutoff cases now pass: 05/10/11/12.
   The fifth, 07, gains hand assessment but remains blocked by packing budget.
   Case 03 additionally passes because a related rank-5 seed expands the unchanged
   treatment branch containing the independently lower-ranked gold passages.
   No rank improvement or new packing logic occurred.
2. **Selection order plus irrelevant branch expansion can consume the budget.**
   In case 07, drinking-water treatment already occupies much of B3. Adding the
   hand-assessment branch succeeds, but adding actual burn treatment would exceed
   2,000 tokens. The packer rejects it whole and later accepts unrelated hand
   hygiene. A correctly ranked candidate is not necessarily delivered evidence.
3. **Far-down ranking and threshold failures survive.** Cases 01/04/06/08/13
   remain failures for reasons the top-k-only change cannot solve. In particular,
   a first-ranked complete passage can still be excluded by the score cutoff.
4. **Higher k does not produce low-noise context.** The case-level irrelevant
   rate remains 12/13 (already saturated); it does not measure the quantity of
   irrelevant text. Raw contexts demonstrate extra unrelated branches and mean
   context size more than doubles. No invented token-level noise ratio is reported.
5. **Potential wrong-scenario advice increases.** Case 09 now contains advice to
   move to generate warmth, from an explicitly labelled post-ice-rescue passage,
   alongside the required heat-prevention instruction to reduce activity. This
   is a retrieval-context risk, not proof Qwen would misuse the advice.

The experiment supports the near-top-3 hypothesis and reveals a packing/order
interaction. **B8 is clearly better for coverage, but is not sufficiently good
overall to freeze for production or declare ready for generation evaluation.**
It leaves six covered cases incomplete, substantial noise, and one new
potentially misleading scenario combination. No automatic production adoption
or further experiment has been performed. Stop for owner review.

## Separate insufficient-coverage results

Cases 14 and 15 are excluded from all 13-case aggregates above. Case 14 retains
only one of two genuinely supported subset items; its actual knowledge gap is
not solved. Case 15 returns no applicable Norwegian legal information. Neither
retrieval result is scored on abstention or generation behaviour. Both contain
unrelated material, and neither shows wrong-country operational/legal content.
Their budget-rejected packets are separately inspectable in `budget-analysis.json`.

## Uncertainties and validity checks

- Manual semantic scoring has one annotator, not an independent owner review or
  calibrated inter-rater study. Full quotes, reasons, raw context and offsets make
  every decision inspectable. No threshold or gold item changed after results.
- Potentially misleading labels are scenario-risk judgements, not factual source
  contradictions. Conditions/headings remain visible. They are reported separately
  from strict must-have coverage. Case 02's explicitly conditioned post-ice advice
  is not labelled a direct contradiction; case 09's cold/heat mismatch is explicitly
  identified in its frozen irrelevant/potentially misleading criteria.
- Case 05 retains the earlier conservative explicit-information standard; the new
  passage now states the previously missing instructions expressly. Case 07's
  internal cream/ointment conflict remains entirely outside pass/fail and noise.
- Jurisdiction findings use actual delivered passages as well as metadata.
  General DOC hiking advice is not automatically NZ leakage; no delivered NZ
  specific legal/service/operational advice was found in these Norway cases.
  This does not demonstrate correctness for all countries or unseen questions.
- The old venv launcher pointed to a removed Python installation. An **existing
  bundled Python 3.12.14 / NumPy 2.3.5** was used without installing dependencies
  or repairing the environment. Pure-Python PyYAML was read from existing venv
  site-packages. All 15 original production selections and cosine scores reproduced
  exactly; all B3 contexts/traces/token counts also matched exactly. Runtime paths
  and versions are saved. This is a documented runtime substitution, not a silent
  claim of environment identity.
- One harness preflight stopped before writing the first B3 result or packing any
  B8 context, because tuple groups differed from JSON list serialization in an
  assertion. Only comparison serialization was corrected; algorithm unchanged.
  Its raw artifacts remain in the sibling `...-harness-preflight/` directory.
  Scoring quote validation also caught one transcription before any scoring file
  was written; corrected to the exact delivered quotation, with no criteria change.

## Artifacts and reproducibility

Repository artifacts:

- `evals/retrieval_topk_ablation.v1.json` — frozen parameters and inherited hashes.
- `evals/run_retrieval_topk_ablation_v1.py` — exactly B3/B8 and summary command.
- `evals/score_retrieval_topk_ablation_v1.py` — inspectable manual annotations;
  never runs retrieval or generation.
- This report.

Raw/source-bearing artifacts remain local/ignored under:
`knowledge/local/diagnostics/retrieval-topk-ablation-v1-2026-10-07/`.

Includes `frozen-run.json`, corpus/index/vector/manifest snapshots, original
query vectors, all **30** `retrieved.json` / `context.txt` /
`prompt-not-executed.txt` records, seed/packing/budget traces, exact token inputs
and outputs, `scoring.json`, `scoring-with-offsets.json`, `budget-analysis.json`,
`B3/results.json`, `B8/results.json`, `aggregate.json`, scripts/report snapshots,
protected-input integrity checks and an artifact hash inventory.

Scripts refuse to overwrite an existing run or scoring file. To inspect/recompute
aggregates from these saved contexts, use the runner's `summarize` entry point;
do not invoke `run` again. In this host's existing bundled runtime, append
`backend/.venv/Lib/site-packages` to `sys.path` for pure-Python YAML, insert `evals`
for module imports, and call `run_retrieval_topk_ablation_v1.summarize()`.

Key SHA-256 identities:

- Gold: `04ad519f56cfff4fc4158af1975363a142b06d84c84d8f7e842a1095d07868c4`
- Corpus: `bd954cd27111854db2a54a8b05335dac8be7776301060da2cce3dfedb2a33d20`
- Vectors: `1952356b4aef70c0a10fff752071bce511c61f7d8a31bdf6bd97a0d140d1a09d`
- Experiment: `19ccdc1be20938c3bd9cb87b30e77ebc70f1098f428ef8bfb2760c718b2e1f61`

All protected production/source/model/gold hashes unchanged. Embedding inference
calls: **0**. Generation calls: **0**. Additional retrieval configurations: **0**.
Owner review required before any next experiment or implementation change.
