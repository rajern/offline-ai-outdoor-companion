# Research behind the decisions

This is a focused comparison of relevant primary sources, checked on **26 October 2026**. It is not a systematic literature review. Study results were not reproduced here, and the apps were not installed or independently tested.

**Small RAG models can achieve useful results. We did not find directly comparable evidence that a similar phone-sized model reliably writes complete Norwegian first-aid procedures from mixed retrieved passages.** That is a limit of the evidence reviewed, not proof that no such system exists.

## What does a good result mean elsewhere?

| Primary source | Output and evaluation | Reported result and comparison limit |
|---|---|---|
| [RAG-Enhanced Open SLMs for Hypertension Management Chatbots](https://link.springer.com/content/pdf/10.1007/s10916-025-02297-7.pdf), Journal of Medical Systems, 2025; Table 4 and Appendix A | Short Italian patient answers from a knowledge base of question/answer pairs. Two physicians assessed 21 test questions on a 1–5 scale covering relevance, medical accuracy/safety, completeness and concision. | Gemma 3 1B hybrid RAG: **4.33/5**, versus **4.10/5** for role prompting without RAG. The difference was not statistically significant (p=.1919). An ordinal mean is not a percentage of fully preserved instructions. |
| [Ext2Gen: Aligning Extraction and Generation](https://arxiv.org/html/2503.04789v3), preprint v3, 2025; Table 7 | Extract source sentences, then write an answer. Evaluate inclusion of the reference answer, plus word/semantic similarity. Models receive supervised/preference training. | Llama 3.2 3B: GPT-4o answer-inclusion judgment **59.5% → 75.0%**; lexical inclusion **28.6% → 39.0%**. This measures a different target from all required procedural details, and is not a prompt-only gain. |
| [Pleias-RAG](https://arxiv.org/html/2504.18225v2), preprint v2, 2026; Sections 3–4 | Specially trained 350M and approximately 1B models generate source quotes and a final answer. A judge compares final answers to benchmark references. | Authors report competition with larger 7–8B models on selected benchmarks. HotpotQA/2Wiki accept the judge's strongest positive match; MuSiQue also accepts a weaker positive match. Mostly short factual answers; Norwegian procedural completeness was not demonstrated. |
| [B1ade minimalist RAG](https://arxiv.org/html/2607.27506v1), preprint v1, 2026; Table 3 | A trained 1B model writes context-based answers. Claude Sonnet 4 rates correctness, completeness, coherence and faithfulness on 0–1 scales. | v2: **.541 correctness, .539 completeness, .856 coherence, .681 faithfulness; .654 average**. The unmodified Llama 1B baseline has a higher .684 average. A headline average can hide weaknesses, and .654 is not 65.4% complete correct answers. |
| [Pocket RAG](https://arxiv.org/html/2602.13229v1), preprint v1, 2026; Sections 4.1–4.2 and 5.4 | Android first-aid RAG with lexical filtering, semantic ranking and context compression. Evaluation uses 200 physical and 200 psychological first-aid multiple-choice questions derived from WHO materials. | Qwen 3 0.6B reaches **94.5% physical** and **97.0% psychological** answer-selection accuracy in the best reported configurations. Selecting an answer is different from composing a complete procedure. The authors acknowledge that free-text and interactive evaluation are still needed. |

### What is useful for Outwise?

The hypertension study is a concrete example of a simpler generation task: retrieve three short question/answer records rather than asking the model to construct a procedure from many article fragments. Its corpus grew from 315 physician-interaction entries to 1,473 records through GPT-4 augmentation; only a subset was manually checked. The small, in-domain evaluation and Italian language limit transfer. Its result motivates prepared answer blocks, but does not establish that they would solve Outwise's failures. The study also includes a 32B reranker in some configurations, so not every tested pipeline is phone-sized.

Ext2Gen and Pleias suggest that evidence selection and source-based writing can be learned. They use additional model training. Outwise's source-focused prompt experiment did not reproduce those methods. Their results justify distinguishing an untested training approach from an already tested prompt change; they do not justify expecting the same gains for a quantized Norwegian model.

B1ade reinforces a measurement decision: show correctness, coverage and source support separately. Fluency or an average score should not hide missing instructions. Its attribution frequency is also different from verified citation correctness.

Pocket RAG is close to our deployment idea, but its high multiple-choice scores do not set a numerical target for our free-text rubric. Its method is evidence that small offline systems can answer bounded questions well, not that our more open-ended task has already been solved.

## What similar apps publicly document

| Example | Documented approach | Evidence found in this review |
|---|---|---|
| [The Ark — App Store](https://apps.apple.com/us/app/survival-ai-the-ark/id6746391165) | Its listing describes local RAG over stored manuals and generated guidance with sources. | No public question set, rubric and comparable answer-quality results were found in the inspected material. Store ratings and reliability claims are not an evaluation of medical completeness. |
| [Ash — iOS/TestFlight project](https://github.com/RaccoonOnion/ash) | Gemma 4 E2B/E4B plus MiniLM; 56 knowledge packs; citations open the exact retrieved passage. Users can scope a chat to a selected pack. | An inspectable implementation and useful source-navigation ideas. No published completeness/correctness benchmark was found in the inspected documentation. TestFlight availability is different from a verified App Store release. |
| [SEER — developer documentation](https://li-bra.com/en/seer/) | Local AI searches an included handbook and links to original text. Eight first-aid scenarios also have predefined yes/no instruction flows. | A practical combination of generated answers and fixed procedures. No comparable published score was found; the developer explicitly warns that AI answers can be wrong. |
| [Red Cross First Aid — New Zealand](https://www.redcross.org.nz/first-aid/about-first-aid/first-aid-app) | Preloaded, step-by-step emergency information, available offline. | A source-led alternative to free generation. This describes content delivery, not evidence for a small language model's quality. |

These observations concern publicly available descriptions, not an audit of internal algorithms or undisclosed testing. Source links alone do not prove an answer is faithful, and source-first design still needs relevant retrieval.

## Why this evaluation approach?

[RAGChecker](https://arxiv.org/abs/2408.08067) separates retrieval and generation diagnostics. This supports asking both whether the evidence was supplied and what the model did with it, rather than using one undifferentiated RAG score.

[HealthBench](https://openai.com/index/healthbench/) uses physician-created, conversation-specific rubrics and distinguishes realistic health conversations from exam questions. It supports concrete situation-specific criteria, but **does not validate Outwise's rubric**. Outwise lacks a comparable independent clinical authoring and review process.

## Decision and limits

The evidence supports several possible future projects: a manually checked collection of complete answer cards; narrower scenario selection; or a model specifically trained for RAG. None was implemented or validated by the prompt/sampling round. Each costs additional work and still needs evaluation of wrong-scenario selection and missing conditions.

For this learning prototype, the owner chose to stop general optimization and make retrieved text and the automatically displayed AI interpretation clearly distinguishable. This is a presentation and scope decision. It is not a claim that the interpretation is reliable or that showing sources compensates for known errors.

The defensible conclusion is: **the tested setup did not meet the original reliability goal; other small-model successes use different data, output tasks, metrics or training. We have not established an easy transferable fix or a universal small-model limit.**
