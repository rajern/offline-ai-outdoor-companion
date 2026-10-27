# Evidence and reading guide

You do not need to read the experiment history to understand Outwise. Start with [Results](RESULTS.md), then [Research](RESEARCH.md). The files below preserve the basis for the main conclusions. The detailed experiment reports are mostly in Norwegian.

## Which evidence supports which conclusion?

| Question | Main evidence |
|---|---|
| What counts as a good answer? | [Locked method](../evals/evaluation_lock.v1.md), [rubric](../evals/answer_rubric.v1.json), [criterion decision ledger](../evals/answer_rubric_decisions.v1.md) |
| Did changing the rubric explain the weak results? | [Rubric and Medium/High comparison](../evals/answer_revision_report.v2.md), [raw aggregates](../evals/answer_revision_results.v3.json), [review](../evals/answer_revision_review.v1.json) |
| What text did retrieval make available? | [Retrieval reassessment](../evals/retrieval_rubric_rescore_report.v1.md), [results](../evals/retrieval_rubric_rescore_results.v1.json), [review](../evals/retrieval_rubric_rescore_review.v1.json) |
| Did the bounded local changes help? | [Improvement report](../evals/local_generation_improvement_report.v1.md), [results](../evals/local_generation_improvement_results.v1.json), [review](../evals/local_generation_improvement_review.v1.json) |
| Could another model use the same text better? | [Complete GPT reference](../evals/large_model_reference_report.v2.md), [results](../evals/large_model_reference_results.v1.json), [review](../evals/large_model_reference_review.v1.json) |
| Where did the knowledge come from? | [Approved source manifest](../knowledge/manifests/approved-sources.json), [source setup and reuse](KNOWLEDGE_SETUP.md), [data contract](DATA.md) |
| What external work informed the interpretation? | [Primary studies, app descriptions and comparison limits](RESEARCH.md) |

## What is public and what stays local?

The repository contains development question definitions, the rubric, source metadata, result summaries and review records and experiment code. The [25-case development definition](../evals/retrieval_development.v2.yaml) records the authored scenarios; the revised rubric is the current criterion definition. Historical definitions remain historical, rather than silently changing to fit later results.

Exact source snapshots, full source contexts, raw model/judge outputs, frozen execution copies and integrity records are retained under ignored `knowledge/local/diagnostics/` directories. Model binaries and generated indexes also stay outside Git. This preserves provenance without publishing third-party source text or large local assets by default.

Public summaries make the arithmetic and decisions inspectable. They do **not** let a new clone independently reproduce every semantic judgment without the corresponding private frozen source and output records. Downloading today's webpages is not equivalent to possessing the original snapshots.

## Reproduction and historical records

The main reports link to their protocols and audits. Historical runners and intermediate reports are in the [verified development archive](../evals/README.md). Restore the original snapshot separately before using historical commands; they require matching private evidence and the expected original file/Git layout. They verify exact inputs, hashes, raw outputs and recomputed summaries without new model calls. A passing integrity audit establishes consistency; it does not establish that the judge's interpretation is medically correct.

Important technical limits remain part of the result: the 4B candidate was excluded for measured memory use, and the GPT run had an interrupted attempt with unknown token usage. Neither should be rewritten as a model-quality failure or zero-cost attempt. Low-level debugging history need not be part of the introductory reading path.

The prototype closeout uses a verified local archive before repository cleanup. It protects the earlier tracked and untracked project files; it is not a public release artifact. Historical frozen evidence is distinct from active application code. If experiment files are relocated or retired, their restoration requirements and the checks that still work must remain explicit.

No holdout results, independent clinical validation or full MVP safety approval are claimed. The original milestone acceptance criteria are not automatically satisfied by completing a learning prototype.

Two selected replay packages are an explicit exception to the default of keeping source text private: their licensed text, original links, owners and reuse terms are bundled with attribution. See [demo provenance](../frontend/demo/provenance.json) and [demo scope](PROTOTYPE.md#demonstration-and-reuse).
