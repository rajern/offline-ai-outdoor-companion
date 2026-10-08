# Token-aware child search — frozen B8 versus C8

One owner-authorized controlled experiment, 2026-10-07. Completed; stopped for
owner review. C8 is diagnostic only, not installed in production. Gold, sources,
corpus content, embedding model, Qwen, ranking formula, thresholds, prompts and
production files unchanged. No reranker, hybrid/lexical search, query rewriting,
generation, further chunking variant or follow-up experiment.

## Outcome

**This C8 implementation removes embedding truncation but does not improve
end-to-end retrieval quality over B8.** Strict coverage falls by one required
item, and one previously complete river-crossing case becomes incomplete.
Some useful search targets improve, but none of the six previously failed
covered cases gains a fully covered must-have item. Candidate crowding, weak
relative similarity/threshold exclusions and parent-packing budget remain.

## Method and frozen controls

Baseline B8 contexts, annotations and outputs were copied directly from the
previous frozen top-k experiment; **baseline retrieval was not rerun**. All 15
original query vectors were reused without query re-embedding. C8 alone received
one new diagnostic index under ignored `knowledge/local/diagnostics/`.

Before evaluating C8, `retrieval_child_search.v1.json` and `frozen-run.json`
recorded the algorithm, hashes and controls. Child definitions, input token IDs,
span coverage and length statistics were saved before query scoring began.

- Same 190 original passages and 22 approved source documents; exact source
  substrings only. Every child retains parent/source/document/section and offsets.
- Same locked local multilingual MiniLM ONNX model/revision, actual FastEmbed
  tokenizer loader, mean pooling, CPU provider, 4 threads and batch size 16.
- Same two embedding views: **body text** and **title + `. ` + section + `. ` +
  body text**. Each view is normalized; their mean is then normalized, matching
  production `text-context-mean-v1`. No source name, URL, topic or other metadata
  is included in embedding input.
- Unsplit parents whose complete inputs already fit both views reuse the exact
  existing stored vectors, keeping unrelated recomputation/padding effects out
  of the comparison. Only new children of split parents are newly embedded.
- Same float32 cosine, descending score / ascending ID ties, NO/general geography
  filtering and 0.35 threshold. **Top 8 means eight child hits**, including
  duplicate parents; no refill to eight unique parents or branches.
- Each selected child maps to the unmodified original parent. The **exact same
  narrow section packer** then expands/deduplicates/adopts or rejects complete
  original-parent packets in seed order. Children are not sent directly to Qwen.
- Same llama-tokenize binary/GGUF and **2,000-token complete unmodified prompt
  budget**, including instructions, question and source headers. Chat-template
  overhead remains excluded, as in B8. Prompts saved, never executed.
- Same strict binary information-based scoring and prior semantic judgements.
  Partial required conjunctions count zero. No chunk-ID pass criteria, source-count
  bonus, mandatory supporting source when primary context is sufficient, or
  optional-info compensation. Cream conflict remains non-scoring; mat optional.

### Effective limit and the one chunking configuration

The stored model config has `max_position_embeddings: 512`; tokenizer config has
`model_max_length: 512` **and `max_length: 128`**. The deployed FastEmbed loader
selects their minimum. Its actual tokenizer reports **right truncation at 128**.
Thus 128 is the effective deployed input limit, not a claim that the architecture
physically cannot accept a larger length.

Chunking stays within original passages. Greedily choose the last fitting
paragraph/newline or sentence end; otherwise a word end, with token-offset ends
only as a last resort. Both embedding views, including unchanged metadata and
special tokens, must fit <=128. Split parents use a **maximum 16-token trailing
word-aligned overlap**, dropped only when required for forward progress. No
cross-parent overlap, source rewriting or metadata shortening. All original
characters are covered; every child equals its original character substring.

An untruncated/no-padding clone of the **actual loaded tokenizer**, including its
special-token configuration, measures full inputs. For every child/view, IDs are
checked against the actual deployed truncated tokenizer with padding removed:
they are identical. No child input is truncated. New embedding input count is
322; unsplit original vectors are reused for 126 parents.

| C8 index statistic | Result |
| --- | ---: |
| Original parents / split parents | 190 / 64 |
| Child chunks / geography-applicable child candidates | 287 / 229 |
| Body input tokens: min / median / mean / max | 6 / 74 / 70.54 / 120 |
| Metadata+body input tokens: min / median / mean / max | 14 / 95 / 90.72 / 128 |
| All 574 view inputs: min / median / mean / max | 6 / 85 / 80.63 / 128 |
| Truncated child embedding inputs | **0** |
| B8 original body inputs exceeding 128 | 44/190 |
| B8 original metadata+body inputs exceeding 128 | 64/190 |

## Aggregate comparison — 13 covered cases

| Metric | Saved B8 | C8 |
| --- | ---: | ---: |
| Must-have micro coverage | 34/51 = 66.67% | 33/51 = 64.71% |
| Average per-case macro coverage | 65.38% | 62.82% |
| Complete passes | 7/13 | 6/13 |
| Cases with irrelevant context | 12/13 | 13/13 |
| Cases with potentially misleading context | 5/13 | 5/13 |
| Observed jurisdiction leakage | 0/13 | 0/13 |
| Context tokens: mean / median / max | 1,311.38 / 1,524 / 1,770 | 1,397.62 / 1,550 / 1,803 |
| Complete prompt tokens: mean / median / max | 1,500.85 / 1,723 / 1,969 | 1,587.15 / 1,744 / 2,000 |
| Delivered parent passages: mean / median / max | 8.69 / 10 / 12 | 8.62 / 9 / 13 |
| Distinct sections: mean / median / max | 8.00 / 9 / 12 | 7.85 / 8 / 12 |
| Budget-rejected packets / affected covered cases | 5 / 4 | 5 / 5 |

The 12/13 versus 13/13 irrelevant-context increase comes from the lost-case query:
B8 returned nothing; C8 adds avalanche and unconscious-person material but none
of the required lost-person actions. Case-level noise flags do not measure total
irrelevant token quantity. A must-have pass does not cancel separate noise flags.

## Per-case changes — all 15 cases

| Case | Fully covered must-haves B8 → C8 | Context tokens B8 → C8 | Complete prompt tokens B8 → C8 | Interpretation |
| --- | --- | ---: | ---: | --- |
| 01 Ankle / possible fracture | 0/4 → 0/4 | 600 → 1,582 | 779 → 1,761 | Partial RICE rest/non-loading newly present, but no fracture suspicion/assessment or full movement-harm conjunction. No full-item gain; much more unrelated text. |
| 02 Cold, wet companion | 5/5 → 5/5 | 1,412 → 1,412 | 1,610 → 1,610 | Same passage set; child ranking changes do not improve already-complete coverage. |
| 03 Stream drinking water | 5/5 → 5/5 | 1,716 → 1,644 | 1,906 → 1,834 | Chemical/alternative-source tail child ranks higher; branch expansion preserves full boiling and limitation rules. |
| 04 Lost in fog | 0/5 → 0/5 | 0 → 513 | 186 → 700 | Required short, unchanged passage still below threshold; new context is unrelated. |
| 05 Lightning on ridge | 6/6 → 6/6 | 1,436 → 1,713 | 1,623 → 1,900 | Correct last-resort child improves rank, but more flood-property noise enters. |
| 06 Major bleeding | 3/4 → 3/4 | 1,091 → 1,585 | 1,274 → 1,768 | Required initial bleeding 113 criterion is still far below threshold. Added fracture/neck/back/hip 113 advice has a different trigger. |
| 07 Adult hand scald | 1/4 → 1/4 | 1,635 → 1,635 | 1,825 → 1,825 | Cooling child selected, but complete original treatment packet rejected by budget; cream excluded. |
| 08 Unconscious adult | 2/4 → 2/4 | 1,524 → 1,001 | 1,723 → 1,200 | Eight child hits contain only five unique parents. Child/baby procedures still outrank full adult assessment; HLR/monitoring tail remains low. |
| 09 Heat prevention | 3/3 → 3/3 | 1,592 → 1,493 | 1,772 → 1,673 | Pass retained; inappropriate cold-rescue movement advice remains. |
| 10 Unexpected night out | 3/3 → 3/3 | 842 → 1,093 | 1,023 → 1,274 | Equipment prefix child ranks higher; original parent packing supplies shelter tail, not a direct shelter-tail search success. |
| 11 Toilet hygiene | 3/3 → 3/3 | 1,770 → 1,145 | 1,969 → 1,344 | Burial/hand hygiene retained; burn noise gone, flood and hypothermia noise remain. |
| 12 High brown river | **3/3 → 2/3** | 1,724 → 1,550 | 1,918 → 1,744 | Regression: brown-water warning moves outside top 8 due to new competition. Stop conditions and wait/turn-back retained. |
| 13 Distress beacon | 0/2 → 0/2 | 1,706 → 1,803 | 1,903 → 2,000 | Correct beacon document appears via device comparison, but required activation instruction still absent. |
| 14 Avalanche signs — gap | Supported subset 1/2 → 1/2 | 1,749 → 1,662 | 1,939 → 1,852 | Additional planning/rescue text does not fill explicit sign interpretation or safe retreat gap. Separate, not a full-answer pass. |
| 15 Norwegian campfire law — gap | No applicable legal gold | 1,605 → 1,716 | 1,782 → 1,893 | No Norwegian fire-law coverage; unrelated water/flood text, no NZ legal leakage. No empty-list pass awarded. |

No previously failed covered case improves or worsens in **full-item coverage**.
Case 01 gains useful partial information, not a complete required item. Case 12,
previously passed, worsens and becomes a failure. Cases 14/15 remain excluded from
normal coverage/pass/noise aggregates; all-15 budget rejections are 9 B8 / 10 C8.

## Gold-information ranking and mechanism diagnosis

Ranks are geographically applicable ranks **before the unchanged score cutoff**.
B8 ranks come from its saved top-eight seeds or the prior saved full-candidate
diagnosis; no baseline query was rerun. C8 raw ranks count children, whereas B8
counts original passages. Their pool sizes differ (229 versus 161 applicable
candidates), so raw rank shifts alone are not evidence of a worse embedding.
The saved audit additionally gives projected unique-parent ranks without
retrieving/packing any additional configuration.

| Needed information / evidence location | B8 parent rank / cosine | C8 child rank / cosine | What actually happened |
| --- | --- | --- | --- |
| 01 Fracture suspicion/assessment (`04-005`) | 20 / .294786 | 27 / .294786 (unique parent 21) | Short fully represented parent unchanged; still below threshold. |
| 01 Immobilisation/movement harm (`04-006`) | 6 / .341193 | 7 / .347157 (unique parent 6) | Small score gain, still below .35; not delivered. |
| 03 Alternative water source after chemical contamination (`21-009`) | 13 / .440370 | Tail child 5 / .518610 | Newly represented tail enters top 8; full parent/branch admitted. First complete chemical-limit sentence itself is in child rank 18 / .442427. Both facts become present through parent context, not because one child independently contains the whole conjunction. |
| 03 Full boiling rule (`21-010`) | 11 / .448537 | 17 / .448537 | Direct boiling target not selected in either; same treatment-branch packing brings it. |
| 04 All lost-person actions (`09-007`) | 1 / .335254 | 4 / .335254 (unique parent 3) | Already short/untruncated and unchanged; cutoff still excludes it. |
| 05 Ridge/overhang/qualified risk reduction (`22-004`) | 8 / .406440 | 5 / .431613 | Relevant fact-bearing child genuinely ranks higher and is admitted. Already passed B8. |
| 06 Initial major-bleed escalation (`02-006`) | 44 / .233094 | 68 / .233094 (unique parent 48) | Already short and fully represented; unchanged score, far below cutoff. |
| 07 Cooling/no ice (`03-006`) | 5 / .464033 | 7 / .463374 (unique parent 6) | Selected child, but parent packet rejected: **2,246 > 2,000** prompt tokens. A packing/order/budget failure. |
| 07 No blister puncture (`03-006`) | Same parent; statement truncated out of both old views | 10 / .448043 | Statement now fully represented in a child, but outside top 8. Selected sibling would still deliver it via full parent if packing admitted that parent. |
| 07 Hand assessment (`03-007`) | 4 / .479880 | 4 / .478704 | Selected/admitted; covered in both runs. |
| 08 Adult airway/assessment alternative (`01-004`) | 9 / .380829 | Prefix 11 / .389938 (unique parent 8); ten-second tail 45 / .299356 | Modest prefix score gain but duplicate-child competition excludes it; full timing-tail representation does not yield a high relevant score. |
| 08 Abnormal-breath HLR/113 (`07-005`) | 25 / .313416; tail truncated in both views | 35 / .316060 (unique parent 29) | Fully represented child remains below threshold. Monitoring tail rank 36 / .313521; no full-item recovery. |
| 10 Sleeping equipment (`12-002`) | 6 / .483331 | Prefix 4 / .505924 | Search improves for prefix; shelter/survival-insulation tail itself is rank 26 / .370748. Full parent supplies that tail. |
| 11 Burial depth/distance/downstream (`21-015`) | 4 / .583929 | 4 / .583929 | Short unmodified passage: identical score/rank, retained. |
| 12 Brown-water warning (`14-005`) | 7 / .414866 | 11 / .414866 (unique parent 10) | Unchanged vector, displaced by other/new child candidates. Not selected; **not** rejected by budget. |
| 13 Beacon activation (`11-003`) | 16 / .396384 | 23 / .396384 (unique parent 22) | Short fully represented passage unchanged; still behind irrelevant operational/device material. |

IDs locate inspected evidence only; the gold remains information-based. The
full quote/fragment/child-input audit is in each `gold-ranking-audit.json`.
Multiple passages can collectively supply facts. A best child of a parent is
not automatically the child containing the specific instruction; the table
explicitly distinguishes them. No document hit is awarded as a full gold match.

### 1. Search improvement

Real targeted gains occur for the water chemical/alternative-source tail,
lightning last-resort facts and sleeping-equipment prefix. However, these cases
already passed B8. The equipment shelter tail still ranks low and is included
only by parent packing. Newly represented burn no-puncture and adult HLR tails
do **not** enter top 8. Changes to short unrelated children can also increase
their scores and consume slots or budget.

### 2. Packing failure

Case 07 cleanly demonstrates a selected correct child without delivered correct
parent context. Symptom, abrasion and a six-passage water-treatment branch enter
first. After hand assessment and hygiene, burn treatment would cost 2,246 tokens,
so the unchanged atomic packer rejects it. Its missing facts cannot receive credit
from the saved rejected-tokenization candidate. The same failure existed in B8
at 2,162 tokens; child search did not remove it.

### 3. Remaining ranking / threshold / candidate-selection failure

Cases 01/04/06/08/13 retain ranking/cutoff problems; core short passages in
01/04/06/13 were already fully representable. Case 08's HLR/monitoring tail now
fits but remains low/below threshold. Case 12 is newly lost through candidate
competition, not source coverage or packing. None of these missing instructions
is absent from the unchanged corpus. The actual KB gaps remain only 14/15.

Child multiplicity is a documented interaction, not silently hidden by changing
top-k. Eight covered cases have duplicate packing hits (16 duplicate-hit traces
total, including same-branch siblings as well as same-parent children). In case
08, eight child hits yield only five distinct parents: two children of the call-113
passage and three of side-position context. The adult-assessment parent is eighth
in the unique-parent projection but eleventh in raw child order. The projection
is an observation, **not** a scored unique-parent experiment.

## What the 128-token hypothesis does and does not establish

Truncation is real and has been eliminated for this diagnostic representation.
Required burn and adult HLR statements previously beyond both retained prefixes
now affect fully represented child inputs. This is a genuine representation repair.

But **eliminating truncation is not sufficient**: no failed covered case gains a
full required item, overall coverage declines, and noise does not improve.
Remaining short-passage failures cannot reasonably be attributed to long-input
truncation in those passages. Nor does this single experiment prove the embedding
model alone is the cause: segmentation changes semantic context and candidate
competition, while parent packing and fixed threshold remain limiting factors.

The result rejects adopting **this C8 setup** as a quality improvement over B8.
It does not prove that all possible child representations are ineffective or
that truncation had no causal effect on any ranking. No other variant was tuned
or tested, and thresholds/gold were not adjusted to rescue observed results.

## Exactly one recommended next experiment — NOT run

**Candidate-unit ablation on the saved C8 index:** compare current strict top-eight
child selection against selecting the first **eight unique original parents**
by each parent's best child score. Keep the saved child vectors/query vectors,
0.35 threshold, geography, unmodified narrow packer, prompt budget and gold fixed.
Do not combine this with packing changes, threshold tuning or an embedding switch.

This isolates the documented duplicate-child slot/candidate-diversity effect
before attributing remaining differences to embedding model quality. Case 08's
adult-assessment parent at projected rank 8 provides a concrete hypothesis.
Case 12's projected rank 10 and below-threshold cases are not expected to be
automatically solved. Even if it helps, the burn packing failure may remain.
No result for this proposed experiment is claimed, and it has not been executed.

## Uncertainty, integrity and artifacts

Manual scoring has one annotator. Exact quotes/offsets, partial-item reasons,
optional facts and raw context remain inspectable for owner review. Case 01
retains the explicit movement-harm conjunction; RICE rest alone earns no full
item. Case 14 retains conservative supported-subset scoring: new conditional
tour planning is not silently accepted as the complete competence rule.
Potentially misleading flags concern wrong-scenario risk, not observed model
misuse. Conditions are visible; no automatic contradiction from any off-topic
passage. Source attribution alone is not jurisdiction leakage; actual delivered
NO/general content was inspected. This small set does not estimate unseen-case
performance or prove global geography correctness.

The original Python 3.11.9 venv/runtime ran C8 with its existing dependencies.
Its launcher works when permitted outside the sandbox; no environment repair,
dependency install or download was needed. The prior B8 report's explanation
that its launcher referenced a removed installation was not established: this
turn demonstrated that execution permission, not a missing installation, is
the relevant constraint. Prior artifacts are preserved, not rewritten.

Repository files: this report, `retrieval_child_search.v1.json`,
`run_retrieval_child_search_v1.py`, `score_retrieval_child_search_v1.py`.

Raw/source-bearing artifacts remain ignored/local at:
`knowledge/local/diagnostics/retrieval-child-search-v1-2026-10-07/`.
They include frozen parameters/hash/runtime records, original corpus/index/vector
snapshots, source manifest, child/provenance spans, exact embedding inputs/IDs,
length statistics and zero-truncation checks, both child-view vectors and index,
all original query vectors, saved B8 contexts, C8 ranked all-candidate landscapes,
selected children/mapped parents, packing traces, budget-rejected packets, all 30
final contexts and unexecuted prompts, tokenization inputs/outputs, ranking audits,
manual scoring/reasons/offsets, aggregate/per-case results and final integrity/hash
inventory. No source text is added to public production assets.

Reproduction uses the existing venv: `python evals/run_retrieval_child_search_v1.py
run`, followed by the inspectable scoring script and the runner's `summarize`
command. Scripts refuse to overwrite existing run/scoring directories; do not
rerun retrieval merely to inspect or recompute metrics. `summarize` only consumes
saved outputs. Hashes pin the algorithm/configuration to this completed run.

Gold SHA-256: `04ad519f56cfff4fc4158af1975363a142b06d84c84d8f7e842a1095d07868c4`.
Corpus SHA-256: `bd954cd27111854db2a54a8b05335dac8be7776301060da2cce3dfedb2a33d20`.
Experiment SHA-256: `c64929639510bcc659be771f9e8e83ea0e124b10f409031e77db019a1f94206c`.

All protected production/gold/corpus/manifest/model hashes unchanged. Baseline
retrieval calls: **0**. Query embedding calls: **0**. Generation calls: **0**.
Chunking configurations tested: **1**. C8 not installed. **Stopped for review.**
