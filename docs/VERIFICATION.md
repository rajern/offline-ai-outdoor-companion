# Prototype verification

This records technical closeout checks. It does not replace the answer-quality
evaluation or approve the prototype for outdoor/medical use.

## Local application checks — 26 October 2026

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

The JPEGs are actual browser screenshots. They show the replay UI and an unchanged
test answer, not a real-time model speed measurement or a fabricated good answer.
The mobile viewport checks layout on PC; they do not demonstrate native
iOS/Android performance. The previous GIF was replaced with separate screenshots
at the owner's request.

- [Overview](images/outwise-overview.jpg)
- [Source excerpts](images/outwise-sources.jpg)
- [Automatically shown interpretation](images/outwise-interpretation.jpg)

## README and standalone replay — 27 October 2026

- The README now leads with the same eight questions for Qwen, Gemma and GPT,
  with required coverage, gap abstention and separate judge flags. Historical
  full-25 results remain in the detailed results document. No answers, scores,
  questions or rubrics were changed and no quality experiment was rerun.
- `scripts/start-demo.ps1` built the current frontend and served it at numeric
  loopback port 8080 using Node alone. The browser followed the replay-only
  redirect, showed both saved examples and their automatic interpretations,
  expanded/collapsed source cards and cleared the view successfully.
- The live-model switch and question input were absent from standalone replay.
  Its server exposes only the exported frontend; API requests are rejected.
  The server test passed for redirects, assets, HEAD, missing files, API/method
  rejection, malformed URLs and path traversal. The initial sandboxed test
  could not connect to its loopback port (EACCES); the same test passed outside
  that restriction. This was a test-environment limitation, not a product fix.
- The frontend TypeScript check and Expo web export passed. The 390 px browser
  viewport had document width and scroll width both 390 px. Three actual JPEG
  screenshots replaced the previous animation.
- The actual application also started successfully through
  `scripts/start-outwise.ps1` on port 8000 with the newly built frontend. The
  browser showed available local files, both modes and the live question input.
  No new model answer was generated for this startup regression check.
- Active documentation links, both replay packages and their private original
  answer hashes passed the project check; all 43 retained frozen evidence files
  remained unchanged. The earlier backend/local-model checks above still apply.

This verifies a local replay and its presentation. It is not a new answer-quality
result or a physical internet-disconnected test of the complete application.

## Owner review still required

Review the wording and UI, inspect representative source passages/interpretations,
and test a live question with internet physically disconnected. Confirm the
chosen learning-prototype scope and README are an accurate final presentation.
Original safety policy, safe critical procedures, independent clinical validation,
full MVP readiness and public release are not approved by these checks.
