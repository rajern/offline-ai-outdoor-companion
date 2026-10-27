# What the experiments showed

## Main comparison: the same eight questions

The main result compares **Qwen3.5-2B**, **Gemma 4 E2B** and a **GPT-6.1 Sol High reference** on the same saved questions and source packages. The eight questions were deliberately selected from the authored development set; they are not a random or independent test sample.

Six questions describe supported situations with **15 required information criteria**. The other two test knowledge gaps. Retrieval fully supplied **13 of the 15 criteria** and partially supplied the other two.

| Generator | Fully covered required criteria /15 | Fully supplied criteria retained /13 | Core-complete supported answers /6 | Appropriate gap abstentions /2 |
|---|---:|---:|---:|---:|
| Local Qwen baseline | **8** | 8 | 2 | 0 |
| Local Gemma baseline | **6** | 6 | 1 | 2 |
| GPT-6.1 Sol High reference | **13** | 13 | 4 | 2 |

Coverage is not overall correctness or safety. An answer can include a required instruction and also contain wrong additional advice. The same assessments therefore recorded separate findings:

| Generator | Answers with unsupported additions /8 | Answers with critical omissions /8 | Answers with direct conflicts /8 |
|---|---:|---:|---:|
| Qwen baseline | 7 | 3 | 2 |
| Gemma baseline | 1 | 5 | 1 |
| GPT reference | 0 | 0 | 0 |

These columns count answers with at least one raw judge flag. They are developmental findings, not exhaustive error counts, clinically validated rates or severity rankings. One GPT item still required review because the sources did not fully supply the needed information.

A concrete example is case 23: the question asks whether people can leave shelter after ten quiet minutes following thunder. Qwen says yes, even though the supplied source says to stay sheltered for at least 30 minutes after the last thunder. The answer also imports advice about ice. The replay preserves this failure rather than editing it into a better answer.

The large-model reference shows that these same sources can support substantially better answers. It does not isolate model size: reasoning effort, runtime wrapper and sampling differed, and GPT did not have the local 512-token output cap. The judge was from the same model family. See the [complete reference report](../evals/large_model_reference_report.v2.md).

The project is being finished as a **learning prototype**. Showing sources beside an automatically displayed AI interpretation makes the process easier to inspect; it does not make an incorrect interpretation safe. The original safety layer and MVP quality approval remain unfinished.

## The two questions we measured

1. **Retrieval:** Did the text supplied to the model contain the information needed for this question?
2. **Generation:** Did the model preserve that information in its answer, with the right meaning and conditions?

An embedding model finds related text. A language model then selects and writes an answer from it. Success at the first task does not guarantee success at the second.

## The data and rubric

The fixed knowledge collection contains **22 approved URLs and 190 stored text chunks**, with Norwegian and English source material. The authored development set contains **25 Norwegian questions** about injuries, cold, water, navigation and other outdoor situations. Three deliberately test gaps or insufficient coverage. The main comparison uses the same eight selected questions throughout: cases 19, 05, 08, 17, 21, 23, 15 and 25. No new model-quality run was made to produce this presentation.

The screening subset has **15 required criteria across six supported questions**. In the broader development rubric, there are 63 required criteria across 22 supported questions; those full-set numbers are reported only as historical background below. Four conditional criteria and five optional criteria belong to the broader rubric and are kept separate from required coverage. Gap questions are assessed separately; an empty list of requirements never counts as success. One historical gap case also has a small supported subset outside the main denominator.

For each required criterion, the judge records:

| Label | Meaning |
|---|---|
| Full | All necessary parts are present, with equivalent meaning and decisive conditions preserved. |
| Partial | Some necessary content is present, but a required part or condition is missing. |
| Absent | The required information is not present. |
| Uncertain | The evidence does not support a confident judgment. |

Word-for-word copying is not required. A valid alternative can satisfy a criterion. Negations, order, timing, units, responsibility and location must remain correct where they matter.

Coverage, source support and harmful additions are separate judgments. An answer can include a required warning **and** contain an unrelated, unsupported instruction. It can therefore gain coverage without being a good answer. These counts are not a validated clinical severity score.

The fixed development judge is **GPT-6.1 Sol, Medium reasoning**, used through isolated Codex sessions. Saved answers were also assessed at High reasoning: agreement was high, but source review did not establish a clear overall winner. High was preferred in some disagreements and Medium in others. Medium was retained as the practical fixed evaluator, not as proven ground truth. See the [measurement lock](../evals/evaluation_lock.v1.md) and [rubric review](../evals/answer_revision_report.v2.md).

### How strong is this test set?

It is useful for finding concrete regressions and investigating where information is lost. It is a small, repeatedly used development set, authored with knowledge of the sources and historical results. It is not a representative sample of real users or an independent medical benchmark. No independent clinician panel has validated the rubric. The separate holdout was not used for these results.

## One bounded improvement round

The same eight screening questions were used for two local models: **Qwen3.5-2B Q4_K_M** and **Gemma 4 E2B official QAT Q4_0**. Six questions have 15 required criteria; two test knowledge gaps. The saved sources fully supply 13 of the 15 criteria and partially supply two.

The round generated 32 new answers. It reused the 16 existing local baseline answers and assessments. Variant A changed only sampling settings. Variant B changed only the prompt, asking for closer source reproduction and preservation of conditions. Sources, source order, model files, native templates, seed, 4,096-token runtime context and 512-token output limit stayed fixed. Local thinking mode was off.

| Local setup, same eight questions | Full criteria /15 | Retained fully supplied criteria /13 | Core-complete questions /6 | Appropriate gap abstentions /2 |
|---|---:|---:|---:|---:|
| Qwen baseline | **8** | **8** | 2 | 0 |
| Qwen A: sampling only | 2 | 2 | 0 | 0 |
| Qwen B: prompt only | 3 | 3 | 0 | 1 |
| Gemma baseline | **6** | **6** | 1 | 2 |
| Gemma A: sampling only | 6 | 6 | 0 | 2 |
| Gemma B: prompt only | 6 | 6 | 0 | 0 |

Neither change produced a clear overall improvement. Qwen deteriorated. Gemma gained some details but lost others, and the new prompt lost both correct gap abstentions. Qwen's higher coverage did not make it the safer model: the baseline judge flagged unsupported additions in seven Qwen answers versus one Gemma answer. A core-complete answer is still not necessarily correct overall.

Qwen sometimes repeated irrelevant material until the output limit. Gemma generally stopped well before it. More output space alone is therefore not a supported fix; a separate output-length experiment was not performed. The 4B candidate was excluded after exceeding the fixed 4 GiB process-group RSS limit, not because of a quality score. Windows memory measurements are not phone validation.

No model weights were trained or changed. The variants changed instructions or generation settings; research informed those choices but was not ingested into the outdoor knowledge base. The app retains the baseline prompt, not the later attempted source-focused prompt.

See the [local improvement report](../evals/local_generation_improvement_report.v1.md).

## A larger-model reference

GPT-6.1 Sol High received the same eight questions, original baseline prompt and source text/order. It was given no rubric, reference answers, earlier answers or tools. The locked Medium judge then assessed its saved answers.

| Setup, same eight questions | Full criteria /15 | Retained fully supplied criteria /13 | Core-complete questions /6 | Appropriate gap abstentions /2 |
|---|---:|---:|---:|---:|
| Local Qwen baseline | 8 | 8 | 2 | 0 |
| Local Gemma baseline | 6 | 6 | 1 | 2 |
| **GPT-6.1 Sol High reference** | **13** | **13** | **4** | **2** |

GPT retained all 13 fully supplied requirements. The other two criteria remained partial and matched the known source gaps. No unsupported-addition, direct-conflict or source-supported critical-omission flag was recorded for these eight GPT answers; one source-insufficiency item still required review. This is a bounded finding, not a safety guarantee.

The comparison demonstrates that the same context can support better answers. It does not isolate model size: reasoning effort, runtime wrapper and sampling differed, and GPT did not have the local 512-token cap. Generator and judge also belonged to the same model family. See the [complete reference report](../evals/large_model_reference_report.v2.md).

The GPT reference was an evaluation tool through the existing subscription. It is not part of the offline application.

## What explains the limitations?

**Observed:** local answers omitted supplied facts, selected material for the wrong situation, changed conditions and added unsupported advice. The screening sources also contained irrelevant text and two incompletely supplied criteria. Some knowledge and source ambiguities remain.

**Supported interpretation:** source selection and answer generation are important bottlenecks in the tested local setup. Missing knowledge alone cannot explain the gap to the larger-model reference.

**Not established:** model size is the sole cause; quantization is the cause; no small model could do better; another prompt would solve it; the current knowledge collection is sufficient for all outdoor situations. The experiments do not separate every possible cause.

## Why stop here?

The project tested embeddings, search settings, context packing, rubric design, judge effort, two local generation models, sampling and a more source-focused prompt. The bounded generation changes did not justify another general tuning round. The [research comparison](RESEARCH.md) identifies other plausible approaches, including prepared answer blocks and RAG-specific training, but those would be additional projects rather than demonstrated quick fixes.

The owner chose to finish a demonstrable learning prototype. Source passages and the automatically displayed model interpretation remain visibly separate. This preserves the experiment and makes its limitations inspectable; it is not completion of the original safety-approved MVP. Further optimization was stopped as a scope/time decision, not because small-model improvement has been proven impossible.

## Historical background: full 25-question run

The figures in this section describe older saved contexts and answers on the broader development set. They explain the investigation history; they are **not the main eight-question model comparison**. The denominators, populations and older generation setup must stay separate.

### Historical retrieval assessment

The same **25 saved context packages** were reassessed using the revised rubric. This did not rerun or improve the search.

| Required information supplied by retrieval | Count |
|---|---:|
| Fully present | **55/63 (87.3%)** |
| Partially present | 4/63 |
| Absent | 4/63 |
| Supported questions with every core requirement fully present | 16/22 |

These packages came from the experimental MiniLM configuration: full-body window ranking, top 16, no similarity threshold and P3 context packing. They are not a fresh measurement of every later application request. The [report](../evals/retrieval_rubric_rescore_report.v1.md) identifies the missing information and remaining interpretation caveats.

The old **83.3% (60/72)** and new **87.3% (55/63)** describe the same saved text under different requirement definitions. Nine old requirements became conditional or optional; one retained criterion changed to full under the clarified wording. The percentage increase was a measurement change, not a retrieval improvement.

### Historical full-set generation assessment

For the historical **full 25-question Qwen run**, the revised Medium assessment found:

- **13/63 (20.6%)** required criteria fully covered in the answers.
- **13/55 (23.6%)** of the fully supplied criteria retained in the answers.
- **0/22** supported questions with every core criterion fully covered.

Retention matches criterion IDs: a criterion must be full in both the context and the answer to count. It is not calculated by dividing unrelated aggregate scores.

These are historical full-set answers. The main eight-question comparison above uses newer local baseline answers. It must not replace these historical full-set numbers, or be compared with them as if the population and prompt were unchanged.

For the supporting files and their roles, see [Evidence and reading guide](EVIDENCE.md).
