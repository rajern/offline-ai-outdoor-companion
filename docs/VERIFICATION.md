# Prototype verification — 26 October 2026

This records technical closeout checks. It does not replace the answer-quality
evaluation or approve the prototype for outdoor/medical use.

| Check | Result |
|---|---|
| Backend behaviour and regression tests | 75 passed |
| Frontend TypeScript check | Passed |
| Exported Expo web build | Passed; local JS/assets, served by FastAPI |
| Measured window embedding inputs/weights | Match the frozen targeted index |
| Search seed IDs and exact packed excerpts | Match all 24 comparable saved Norway/general cases |
| Explicit exception | case22 used NZ scope in the experiment; current app uses NO/general |
| Native system/user prompt and tokenizer IDs | Match saved Qwen baseline case23; no new generation in this check |
| Actual local API question | Completed in 55.56 seconds; 5 source groups / 9 exact excerpts returned with an interpretation |
| Phone-width UI | Inspected at 390 px; page width 390 px, no horizontal overflow |
| Replay/source/automatic interpretation UI | Inspected in the real browser; actual screenshots saved |
| Actual chat UI | A second local question completed through the browser, showing sources and interpretation automatically |
| Alternate local port | UI and status/API work together on port 8001 using same-origin requests |
| Abrupt backend termination | Windows-owned child process is killed when its backend exits; regression test and actual app shutdown check passed |
| Public historical archive | All 322 original files verified by hashes; restoration to an empty directory succeeded |
| Cleanup | 215 obsolete flat eval files and 2 obsolete docs archived/removed; 45 key eval files retained |
| Public archive exclusions | No holdout files, models, ignored source snapshots or `.env`; secret-pattern scan found no matches |

The actual API answer remained poor: it contradicted itself and repeated text.
No new rubric score was assigned. The live smoke check proves the route runs;
it does not improve or override the saved quality results.

The input parity check is `scripts/verify-prototype.py`. It permits only numeric
loopback Python connections, reads the original private development evidence,
and generates no answers/judgments. This is separate from a physical
internet-disconnected test. Startup/execution were also exercised through
`scripts/start-outwise.ps1`; missing assets and source-preserving generation/
packing failures are covered by behaviour tests.

Local closeout records are in ignored `knowledge/local/app/`, including the
parity result, live API output, cleanup inventory and restored archive check.
The public archived snapshot has SHA-256
`26158c745122c4fa6e29e409237f5cf14532c25a1ee1cb9b4ab3e28a9de2a174`.
It preserves the exact earlier public code and uncommitted experiment work.
Private original experiment folders were not rewritten.

## Demo evidence

The PNGs are actual browser screenshots. The GIF is a 13-second walkthrough made
from three captured views of the replay UI, not a real-time model speed
measurement or a fabricated good answer. The mobile viewport checks layout on
PC; they do not demonstrate native iOS/Android performance.

- [Overview](images/outwise-overview.png)
- [Source excerpts](images/outwise-sources.png)
- [Automatically shown interpretation](images/outwise-interpretation.png)
- [Animated walkthrough](images/outwise-walkthrough.gif)

## Owner review still required

Review the wording and UI, inspect representative source passages/interpretations,
and test a live question with internet physically disconnected. Confirm the
chosen learning-prototype scope and README are an accurate final presentation.
Original safety policy, safe critical procedures, independent clinical validation,
full MVP readiness and public release are not approved by these checks.
