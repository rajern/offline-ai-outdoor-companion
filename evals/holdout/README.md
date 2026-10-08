# Owner control set — v1

This folder is **excluded from retrieval development and optimization**. Read
AGENTS.md before access. The current authoring task performed source-only QA;
no retrieval, answer generation or scoring was run on these controls.

`retrieval_control.v1.yaml` contains all ten questions and full source-backed
gold. Resolve its source IDs using `../retrieval_sources.v1.json` for source
titles, URLs, publisher attribution and reuse requirements. Required evidence
is literal approved-source support; locators/offsets in `authoring_qa.v1.json`
are provenance, not required retrieval chunk IDs.

Version: 1.0.0. Status: pending owner review. SHA-256:
`0129246dc331473315f844a1b563cca710718968d5dd7d35099dd8459f7f4026`.
The public lock file records the same identity without publishing the questions
in development reports. Nine cases are covered and one has insufficient coverage.

## Owner review inventory (not optimizer input)

| Control | Information need | Sources |
|---|---|---|
| 01 | Adult CPR execution, position, compression and ventilation technique, continued cycles | 01 |
| 02 | Unconscious severely cold person: longer breathing check, gentle handling, hypothermic arrest | 05 |
| 03 | Iodine water disinfection restrictions for pregnancy and prolonged use | 21 |
| 04 | Rescue another person through ice without creating a second casualty | 19 |
| 05 | Flat ski route exposed to avalanche runout beneath steeper terrain | 16 |
| 06 | Small dog bite: infection/tetanus risk and cleaning/medical assessment | 02 |
| 07 | New Zealand PLB registration and cost requirements before a trip | 11 |
| 08 | UV treatment when stream water is murky: organism coverage and particle limitation | 21 |
| 09 | Child-specific paracetamol dose/interval: absent adequate dosing coverage | 03/04 related only; gap |
| 10 | New Zealand trip recipient, overdue return and emergency contact plan | 10/09 |

This is a **procedural holdout**. The author knows it; Git/version control does
not make it secret. Future optimization must not read questions, gold, this
inventory or authoring QA for tuning, experiment choice, debugging or selection.
The default development loader rejects control IDs without opening this folder.
Instructions do not prevent unrestricted filesystem access: use an owner-held
separate checkout/access boundary if stronger protection is required.

Evaluate once only after the development-selected retrieval configuration,
code/config/corpus identities and scoring method are frozen and the owner
explicitly authorizes the final control run. Store results separately. Do not
adjust gold or the chosen configuration based on that run. If results are used
for another selection cycle, mark this holdout consumed and create new controls.
