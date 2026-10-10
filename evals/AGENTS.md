# Retrieval evaluation boundaries

Owner task, 2026-10-10: after reviewing the proposed targeted improvement round,
the owner explicitly said "implementer det og kjør". This authorizes at most
three separate MiniLM/k16/no-threshold experiments beyond the completed 31:
window-mean ranking with P3, scope-diverse packing with original ranking, and
their preplanned combination. All three are frozen together before evaluation.
See `retrieval_targeted_plan.v2.md`, `retrieval_targeted.v2.json` and
`run_targeted_retrieval_v1.py`. Runtime storage is separate under
`knowledge/local/diagnostics/retrieval-targeted-v1-2026-10-10`.
Technical revision-02 repairs header/body separation before any fresh judgment;
the first revision's 75 unjudged contexts/code snapshots remain unchanged.
Packing-only contexts are reused after identical packing-function checks.
Original 31 contexts, scores and adjudication layers remain immutable. Same gold,
sources, V3 judge, subscription authentication, 2,000-token prompt and resource
limits apply. Check every coverage loss and new safety flag before recommending.
Unresolved scorer/safety/resource/quota blockers stop continuation. No holdout,
production integration, paid API, answer generation or further experiments.
The prior "no additional experiments" status below is superseded only for this
new bounded owner task; it remains the historical end of the original plan.

Final development status, 2026-10-10: all 31 planned configurations / 775 case
judgments completed on 2026-10-09. The owner-authorized resume skipped P1;
P2 reused all 25 exact B16 inputs, P3 used 15 new calls / ten cache hits.
P2/P3 passed unchanged RAM/RSS guards. Historical P1 RAM failure remains failed.
Offline audit v3 passes all 775 inputs, 82 frozen identities, 2,912 A/B files
and 103 unchanged P1 files. See `retrieval_optimization_report.v7.md` and
`retrieval_optimization_final_audit.v3.json`. P3 (59/72, macro 80.23%, 15/22)
is recommended only as a provisional development baseline. P1 has highest
coverage (63/72, 17/22) but loses burn items 07/1-3 and introduces anaphylaxis
conflict. P3 still lacks 13 supported requirements; no control-test readiness,
final production choice or automatic C dominance winner is established.
No additional experiments, holdout access, production change or answer generation
is authorized. Stop after the final report; obtain a separate owner task for
further retrieval development. Prior reports/audits v6/v2 remain unchanged.
To refresh the final report without reading historical v6, use
`report_phase_c_v1.py --version 7 --source evals/retrieval_optimization_results.v7.json`.
The statuses below record earlier stops, not current pending execution.

Current stop, 2026-10-09: the owner explicitly authorized MiniLM/k16/no threshold
for C and a limited B-to-C dominance override. Exact-input review resolved case
13/P70 risk negatives and case 19's inconsistent interpretation of a supplied
ice-rescue sequence; only risk flags change in six B rows / three unique inputs.
See `retrieval_phase_c_safety_review.v1.md` and the separately frozen registry.
`continue_retrieval_phase_c_v1.py` preserved A/B and ran C-P1: all 25 judgments
are saved (24 fresh subscription calls, one cache hit), 63/72 coverage, macro
85.23%, 17/22 complete. Host available RAM fell to 52.42 MiB against the unchanged
256 MiB reserve; peak judge process-tree RSS was 231.53 MiB, below 4 GiB.
Offline integrity audit passed 725 saved case results, 82 frozen identities and
2,912 protected A/B files without inference; see `retrieval_optimization_final_audit.v2.json`.
The post-worker resource guard failed. C-P2/C-P3 have not started; 29/31 are
fully scored, not a completed resource-approved comparison. P1 gains eight
requirements but loses burn items 07/1-3 and introduces anaphylaxis risk/conflict.
See `retrieval_optimization_report.v6.md`. No final winner or control-test
readiness is established. After the RAM blocker is resolved and the owner asks
to resume, use the same C continuation; it verifies/skips C-P1 and never repeats
A/B or completed judge calls. Preserve the failed resource sample. All frozen
gold/prompt/packing and production/holdout/generation restrictions still apply.
Earlier continuation statuses below are history, not present approval gates.

Latest continuation status, 2026-10-09: all 25 MiniLM phase-B configurations
are complete (625 judgments); 28/31 configurations including A. C has not run.
RAM checks passed after owner-authorized resume with unchanged limits. One
quota rejection was retained in a hashed archive and retried only after natural
quota renewal and a new owner resume instruction; completed answers were reused.
The original stage-B dominance gate stopped selection. Source review finds
unresolved case-13 risk negatives at P70 despite unchanged generic 113 advice,
and case-19 risk variability despite identical rescue advice. See
`retrieval_optimization_report.v5.md` and `retrieval_optimization_final_audit.v1.json`.
MiniLM k16/no threshold is recommended provisionally as the experimental C
candidate, not selected or approved for production. Obtain a context-bound risk
resolution and explicit experimental B choice/limited gate override before C.
Do not repeat A/B, change frozen gold/judge/packing, or open holdout. Earlier
progress/stops below are historical; their scope restrictions remain applicable.

Owner task, 2026-10-08: the existing 25 development cases and conditional 31-step
optimization are authorized after the specified scorer/runtime prechecks. This
supersedes the preparation-only scope below; original gold/references remain
immutable. Subsequent bounded diagnostics resolved the Qwen repeatability blocker
with explicit CPU isolation; see `qwen_embedding_stability_report.v1.md`. The
owner subsequently authorized resuming the existing 31 configurations after
technical/resource checks, without intermediate approvals. The resumed task
initially stopped before phase A at the available-RAM guard. After the owner freed
RAM, all three sequential resource/input probes passed with the original limits.
The 25 MiniLM contexts were preserved after a one-line correction for missing
source defaults; see `retrieval_optimization_serialization_correction.v1.json`.
Phase A completed all three configurations / 75 judgments. The integrity audit
passed without inference. Stage selection stopped on real per-item coverage and
safety tradeoffs; case 13 additionally needs semantic review. See
`retrieval_optimization_report.v3.md`. B/C are not run. Do not repeat A or modify
gold/judge based on results; obtain the owner's provisional model decision and
case 13 review before advancing. Finalist review remains unfinished. Holdout,
production changes and answer generation remain excluded.

Owner review task, 2026-10-09: the offline model-selection review is complete;
see `retrieval_embedding_selection_review.v1.md` and its evidence JSON. MiniLM
is recommended only as the experimental phase B candidate. Full breathing/CPR
support in case 08 and anaphylaxis support in case 17 are unreachable with its
frozen top-16/section rules. Case 13 Gemma risk and case 20 MiniLM coverage have
separate proposals in `retrieval_embedding_selection_adjudication.proposed.v1.json`;
they are NOT active scoring rules. Original judgments/gold/cache remain unchanged.
Do not treat the recommendation or proposals as the owner's decision. Stop here
until the owner selects the model and resolves the proposed adjudications; do not
repeat phase A or start B/C from this review alone.

Owner continuation, 2026-10-09: MiniLM is explicitly selected as the experimental
B/C model. Both case 13 Gemma risk and case 20/1 MiniLM semantic coverage are
approved in `retrieval_embedding_selection_adjudication.approved.v1.json`.
Use `continue_retrieval_optimization_v1.py` to resume the remaining 28 planned
configurations; it preserves the original frozen scorer, raw scores and cache,
and writes separate exact-input-bound adjusted summaries. Do not repeat A.
Ordinary B/C phase transitions need no new approval; real resource, review or
per-case safety tradeoffs still block selection. This supersedes the preceding
pending-owner status. No production approval is given.

Continuation stopped after B-k3-none's 25 saved judgments: available host RAM
fell to 5.65 MiB below the unchanged 256 MiB reserve; score-worker process-tree
RSS was only 230.2 MiB. All results/seals and 309 phase-A files pass final audit.
One of 28 B/C configurations is fully scored (40/72, 8/22 complete, two misleading
flags); 27 remain. See `retrieval_optimization_report.v4.md` and the continuation
audit. No B/C winner is selected. After the resource blocker is resolved, resume
the same continuation command; it skips completed A and B-k3-none model calls.

Read `FOUNDATION.md` before future retrieval optimization. Default input is the
25-case development set, never the control set. Do not recursively read/search
`evals/holdout/` or include its files in optimizer context, calibration, debugging
or experiment selection. Its local AGENTS.md defines the final-run approval gate.
The holdout author knew its cases; these are process controls, not true blinding.

This preparation task authorizes source-only gold QA and scoring calibration on
ALREADY SAVED historical contexts, not fresh retrieval runs, model/parameter/
packing experiments or production changes. New cases/scorer are pending owner
approval. Unknown automatic decisions are not semantic failures and must not be
used to choose a winner. Preserve original 15 cases and historical outputs.

Development aggregate comparisons must also retain the unchanged legacy-15 slice;
do not compare a 25-case score with a historical 15-case score as if populations
were equal. Noise, jurisdiction and size remain separate from coverage.
