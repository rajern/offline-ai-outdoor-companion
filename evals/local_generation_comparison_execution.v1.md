# M2-06 execution amendment: resource exclusion, 2026-10-24

Owner explicitly requested another attempt ("prøv nå"). Previous attempts and
all original 36 inputs remain preserved. No prompt/question/gold/scorer change.

The latest Qwen 4B + resident MiniLM load had available host RAM 716,300,288 bytes
(above the unchanged 256 MiB reserve), but process-group RSS 4,658,118,656 bytes
(above the unchanged 4 GiB limit). Its server was killed by the original guard.
The original frozen protocol expressly permits exclusion of a candidate proven
incompatible with 4 GiB while distinguishing transient host-memory stops.
Accordingly, exclude this exact 4B variant from this fixed-runtime/configuration
experiment. Do not retry, change quantization, limits or CPU flags. This says
nothing about 4B quality, other hardware or alternative configurations.

Local exclusion registry binds the failed resource log and model SHA-256.
Eligible candidates are existing Qwen 2B and official Google Gemma E2B QAT Q4_0.
2B's previously sealed 36 inputs are reused. Gemma's 36 native input sequences
pass: 768–2,246 tokens including one BOS; actual slot 4,096; output reserved 512;
training-context GGUF metadata 131,072; non-thinking native system/user template.
Gemma model revision 675cff42a74c774d6cb76f76d8eacb49b48c9b93, SHA-256
fa401b55b07ee70a54c6dae3903c783a6e65064312529ea57175cb5f8dec6634,
file gemma-4-E2B_q4_0-it.gguf, 3,349,516,256 bytes. Download metadata license:
Apache 2.0. No multimodal projector or replacement variant downloaded.

Freeze eligible-model identities, native token records, runtime libraries, code,
seed/sampling, resource registry and original protocol before the first answer.
At most 22 new screening responses (8 primary +3 sufficient-context per model),
instead of maximum 33 for three eligible models. No additional replacement cases.
All finalist inputs remain predetermined; <=25 finalist calls only if eligible
under the original critical-error/source-coverage/abstention rules. No new threshold.

Local root: knowledge/local/diagnostics/local-generation-eligible-2026-10-24.
Launcher: run_eligible_local_generation_v1.py. Seven technical unit checks pass.
Actual inference/schema/resources still require runtime checks. No holdout,
retrieval optimization, production integration, paid API or M3 authorization.
