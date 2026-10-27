# Learning prototype: agreed closeout

On 26 October 2026 the owner chose to finish Outwise as a demonstrable learning
prototype. This replaces the immediate goal of finishing all original MVP
milestones. It does not retroactively approve their quality or safety criteria.

## What the application does

The existing Expo/React Native web interface and Python/FastAPI backend remain.
Questions run locally against the approved knowledge collection. Sources and the
model's interpretation appear automatically in separate sections. Users can read
the exact packed excerpts, original language, provenance and reuse terms. A
source link opens the publisher's webpage and therefore needs internet; the
displayed excerpts themselves are local.

The screen keeps question/answer history for convenience. Each new question is
processed independently. There is no conversational memory or GPS location.
Search uses Norway/general jurisdiction; explicitly foreign situations are not
fully supported. A search hit is not a verified relevant procedure.

The model remains Qwen3.5-2B Q4_K_M. This retains the project's locked model and
the measured baseline; it is not a new claim that Qwen is an overall winner.
Gemma had better abstention/source fidelity on some tests.

## Measured profile, portable application code

- MiniLM multilingual model and pinned local model files from knowledge setup.
- Full-body windows: 96 body tokens, up to 24 header tokens, weighted parent
  vectors combining contextual/plain views. The original legacy index is retained.
- Top16 seeds, no score threshold, original P3 source-preserving expansion and
  deduplication. No new relevance classifier or reranker was introduced.
- P3 retains the original 2,000-token packing envelope using the unchanged legacy
  prompt for budget accounting. These instructions are not the generation prompt.
- Generation uses the exact later baseline system instructions, native roles
  and chat template, thinking off, seed 42, T0.2/top-p0.8/top-k20/min-p0.05,
  output cap 512 and runtime context 4,096. Input above 3,200 native tokens is rejected;
  source text is not silently truncated.
- llama.cpp is a single owned, numeric-loopback CPU process, loaded lazily and
  stopped on backend shutdown. On Windows an owned Job Object also prevents
  an orphan model process if the backend is terminated abruptly. Application code imports no evaluation runners.
- If generation fails after retrieval, sources remain visible. If packing cannot
  run or fit, raw search hits are explicitly labeled and no interpretation is
  generated. This is an operational fallback, not a relevance/safety certification.

The selected input/method profile matches the research baseline. Changed process
lifecycle, hardware and runtime defaults can still affect generated text; no
bit-identical answer reproduction or new quality score is claimed.

## Demonstration and reuse

`frontend/demo/examples.json` contains two unchanged Qwen screening answers from
24 October 2026 and the exact source excerpts supplied to them. The UI labels
this as replay, not live inference. One example intentionally shows a serious
failure. `frontend/demo/provenance.json` records original answer hashes, context
hashes and excerpt IDs. Source text is quoted with publisher/content-owner,
original links, dates and reuse terms from the already approved manifest.
Only text is included; no third-party media or logos were copied.

The replay can be shown without installing models. It does not replace the
actual local application or turn an unsafe answer into acceptable advice.

## Remaining owner review

The prototype warning/product wording is prepared for review, not a completed
M3 safety/legal approval. The original separate safety layer, safe critical
procedures, independent clinical validation, mobile-device validation and final
MVP/release approval remain unfinished. The owner reviews the final UI/README
and performs a physical internet-disconnected check before final sign-off.

See [verification](VERIFICATION.md), [results](RESULTS.md) and [research](RESEARCH.md).
