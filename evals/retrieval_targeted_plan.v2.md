# Bounded targeted retrieval experiment

2026-10-10. Owner authorized implementation and execution after reviewing the
proposed round. The original 31 configurations and production remain unchanged.

Three variants are frozen together before retrieval/scoring: window-mean ranking
with original P3; original ranking with scope-diverse packing; their combination.
All use MiniLM, 16 unique original parents, no threshold, the existing 2,000-token
complete prompt budget, unchanged sources, gold, V3 judge and exact adjudications.
The combined variant is preplanned unconditionally; results do not decide its rules.

Ranking represents every body character in non-overlapping 96-token windows.
Context windows prepend at most 24 header tokens. Generated model inputs must
fit the actual 128-token tokenizer limit. Header truncation is recorded; body
truncation is forbidden. Length-weighted means within each view, then the
existing equal text/context mean, produce one normalized vector per parent.
There is no maximum-over-windows score, so long sources do not receive multiple
independent chances at selection. Averaging may still dilute rare instructions;
that tradeoff is tested, not assumed to solve the known ranking failures.

Packing first considers the highest-ranked parent from each represented document,
then other parents in retrieval order. A packet contains complete same-heading
contiguous passages and the nearest preceding strict ancestor heading's text.
Packets are atomic; whole-prompt tokenization decides acceptance. Deduplication
requires identical text AND source scope, avoiding removal of an identical advice
body under a different heading. Source hierarchy cannot prove all cross-heading
clinical dependencies: no claim of universally complete emergency procedures.
No relevance keywords, case IDs, gold requirements or answer text enter either method.

Technical checks cover window completeness, no truncation, finite/unit vectors,
unique parent ranking, source scope, exact prompt serialization, resource limits,
original identities and sealed subscription judge cache. Index creation and warm
single-question embedding latency are measured. Frozen old indices are reused
for the packing-only ranking; their historical build method is reported separately.
Measurements are Windows CPU measurements, not a mobile benchmark.

Every covered baseline requirement loss and new misleading/conflict/geography
flag receives source review. Unresolved safety issues prevent recommendation;
certificate/judge disagreements or uncertain reviews stop inference. Improvements
on this repeatedly used development set are not independent safety validation.
No holdout, answer generation, production integration, new sources or paid API.

## Technical revision 02 before scoring

A synthetic subword-cut test exposed 25 truncated headers with no whitespace
before the body. An explicit period and space after the cut repairs that input
serialization defect. All 75 unjudged contexts and original code snapshots are
preserved in the first diagnostics directory; no new judge calls preceded the
repair. Revised config v2 and code are frozen together in revision-02 before any
scoring. Packing-only contexts are reused after exact function/source identity
checks because their ranking and packing do not use the repaired adapter.
No rules are tuned from observed quality scores.
