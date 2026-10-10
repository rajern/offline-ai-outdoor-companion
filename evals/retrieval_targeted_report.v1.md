# M2-06 — målrettet retrieval-runde

**Status: blocked.**

Tre varianter er frosset samlet før scoring. MiniLM, 16 unike parent-passasjer, ingen terskel, 2 000 tokens, samme kilder/gold/V3-dommer og eksakte adjudikasjonsbindinger. Ingen tidligere resultater er endret. Se `retrieval_targeted_plan.v2.md` og konfigurasjonsfilen v2. Teknisk revisjon 02 retter manglende skille mellom avkortet overskrift og brødtekst før scoring. Første revisjons 75 ubedømte kontekster er bevart; packing-forsøkets 25 kontekster gjenbrukes.

| Oppsett | Vurdert | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | I / M / K / G |
|---|---:|---:|---:|---:|---|---|
| P3 baseline | 25 | 59/72 (81,94 %) | 80,23 % | 15/22 | 41/51 / 78,08 % / 8/13 | 22 / 1 / 0 / 0 |
| T-ranking | 25 | 60/72 (83.33%) | 81.14% | 15/22 | 42/51 / 79.62% / 8/13 | 22 / 1 / 0 / 0 |
| T-packing | 25 | 50/72 (69.44%) | 71.89% | 12/22 | 34/51 / 69.10% / 6/13 | 22 / 3 / 0 / 0 |
| T-combined | 0/25 | ufullstendig | — | — | — | — |

**Stoppårsak:** Methodological safety review: case-16 identical pressure/lying-down instructions have inconsistent risk classification across baseline/ranking/packing. Requires exact-context adjudication before combined scoring or final selection.

## Metodisk stopp før tredje variant

Case 16 har identiske trykk-/liggende-instrukser fra `source-02-007/008` i P3, ranking og packing. Packing flagges som misvisende; de andre flagges ikke. Packing legger til en innledning om stort blodtap, men ingen meningsfull sikkerhetsforskjell som forklarer flaggskiftet er etablert. Dette er `requires_review` i et separat kontekstbundet analyselag; rå dommerresultater og historiske scorer er bevart. En ny risiko kan ikke fastslås bare fra flaggskiftet. Se `retrieval_targeted_review_required.v1.json` for eksakte bindinger og beslutningen som gjenstår.

Ranking er beste **fullførte observerte** variant med én bekreftet kravgevinst og ingen kravtap. Packing taper 12 krav for tre gevinster og kan ikke anbefales. Den kombinerte varianten har 25 kontrollerte kontekster, men er ikke scoret. Ingen endelig anbefaling eller produksjonsendring gjøres før risikovurderingen er konsistent; P3 forblir eksisterende utviklingsgrunnlag. Kvoteavslag utløste ikke dette stoppet.

Ranking mangler fortsatt 01/1–3, 03/3–4, 06/1, 08/4, 13/1–2, 17/1–2 og 21/2. Det er ikke klart for holdout. Neste steg er avgrenset adjudikasjon av case 16 under eksisterende V3-regler, med vurdering av resterende case 13/17-risiko. Ved senere autorisert gjenopptakelse beholdes de 50 vurderingene og alle 75 kontekstene; kun kombinert scoring gjenstår.

En teknisk scoreradapter kompletterer `section_count` fra dokument/seksjon i leverte utdrag. De 75 retrieval-filene, dommerinputene, prompten og scorerreglene er uendret og hashbundet separat. Første lagrede dommersvar gjenbrukes etter metadatafeilen; ingen inferens gjentas. Regresjonskontrollen viser identisk output fra gammel scorer med fullstendig metadata.

## Kjøring og bevarte tekniske stopp

| Variant | Lagrede kontekster | Dommervurderinger |
|---|---:|---:|
| T-ranking | 25/25 | 25/25 |
| T-packing | 25/25 | 25/25 |
| T-combined | 25/25 | 0/25 |

Stoppmåling T-ranking: 241.41 MiB tilgjengelig RAM (krav 256 MiB); topp prosess-tre-RSS 185.45 MiB (grense 4096 MiB). Tilgjengelig vertsmaskin-RAM utløste stoppet; ekstern årsak er ikke fastslått. Ingen automatisk retry eller lemping av grensen.

## Kravgevinster og tap

**T-ranking** (25/25): gevinster 03/5; tap ingen. Udekket i scorede caser: 01/1, 01/2, 01/3, 03/3, 03/4, 06/1, 08/4, 13/1, 13/2, 17/1, 17/2, 21/2. Nye dommerflagg: ingen. Eksakte bindinger finnes i sammenlignings-JSON.

**T-packing** (25/25): gevinster 13/1, 13/2, 21/2; tap 01/4, 05/3, 05/6, 06/4, 07/1, 07/2, 07/3, 08/2, 10/2, 19/1, 23/2, 23/3. Udekket i scorede caser: 01/1, 01/2, 01/3, 01/4, 03/3, 03/4, 03/5, 05/3, 05/6, 06/1, 06/4, 07/1, 07/2, 07/3, 08/2, 08/4, 10/2, 17/1, 17/2, 19/1, 23/2, 23/3. Nye dommerflagg: 08/potentially_misleading, 16/potentially_misleading, 17/potentially_misleading. Eksakte bindinger finnes i sammenlignings-JSON.

**T-combined**: kravgevinster, kravtap, udekkede krav og nye dommerflagg er **ikke vurdert** (0/25 scoret). Fravær av score er ingen dokumentasjon på fravær av risiko.

## Ressurser og abonnement

Indeksarbeid og ferske enkeltspørsmål måles separat fra ranking/packing på lagrede spørsmålsvektorer. Tid påvirkes av token-cache og integritetskontroller. Originalmodell og original indeks gjenbrukes for packing-forsøket; gammel indeksbyggetid er ikke en ny sammenlignbar benchmark. Windows-målinger dokumenterer ikke mobilens minne eller energibruk. Prosessgrense 4 GiB og tilgjengelig-RAM-reserve 256 MiB er uendret.

Tekniske forseglede cachekontroller: 2; disse utløser ingen fersk dommerinferens. Nye kall og cachetreff for konfigurasjonene loggføres separat nedenfor. GPT-6.1 Sol / Codex CLI / Medium / ChatGPT-auth og CLI-versjon er verifisert mot den frosne identiteten; CLI-resultatformatet eksponerer fortsatt ikke faktisk servermodell/revisjon.

Nye abonnementskall: 50; vellykkede 50; cachegjenbruk 1. Input 401,496, output 110,425, reasoning 11,312; total 511,921 tokens. Dommerkalletid 47.42 minutter.

Historiske A+B+C-tokens holdes separat: 2,126,482. Samlet kjent forbruk 2,638,403; ett historisk kvoteavslag har ukjent tokenbruk. Feil i nye dommerkall: 0.

Reasoning inngår i output; prefix-cached input inngår i input. Ingen betalt API-fallback eller automatisk kvotereset.

Siste registrerte kvote: 88 % av femtimersvinduet og 98 % av uken brukt. Dette er delt kontobruk; prosentendringer kan ikke tilskrives dommerkallene alene. Alle snapshots og detaljerte tokenfelt er bevart i sammenlignings-JSON.

## Beslutningsstatus

Ingen automatisk produksjonsvinner. Alle nye sikkerhetsflagg, kravtap og viktige positive vurderinger må kildegjennomgås før anbefaling. Et ufullstendig eller review-blokkert forsøk kan ikke velges. De tre forhåndsdefinerte kunnskapshullene er fortsatt separate og gir ikke automatisk komplett pass. Det gjentatte utviklingssettet gir kalibreringsresultater, ikke uavhengig sikkerhetsvalidering.

Korrigert indeks: 568 embedding-visninger, null avkortet brødtekst, 52 avkortede metadataoverskrifter; bygging 41.57 s / varm embedding 27.94 s. CPU 125.89 s; maksimal indeksbygge-RSS 1249.12 MiB; minimum tilgjengelig RAM 279.96 MiB. Fersk query-embedding snitt 22.69 ms / maks 26.53 ms. Query-vektorbytes identiske med baseline: True. Modell 235.053 MB; parent-indeks 0.292 MB; diagnostiske vindusvektorer 0.873 MB. Indeksbygge-RSS er ikke en måling av mobilappens RAM under vanlig spørsmålskjøring.

| Variant | Målte caser | Prompt snitt / maks | Kontekst snitt | Passasjer / forkastede pakker | Ranking / packing s |
|---|---:|---:|---:|---:|---:|
| T-ranking | 25 | 1959.60 / 1999 | 1768.16 | 265 / 129 | 0.0145 / 146.83 |
| T-packing | 25 | 1971.96 / 2000 | 1780.52 | 273 / 163 | 0.0141 / 325.12 |
| T-combined | 25 | 1958.60 / 1998 | 1767.16 | 266 / 165 | 0.0106 / 90.42 |

Ufullstendige ressursutvalg kan ikke sammenlignes som like store utvalg. Packing-målingene er fra første revisjons uendrede, gjenbrukte input; ranking-målingene er fra korrigert revisjon.

| Fullført dommerfase | CPU s | Topp RSS MiB | Min tilgjengelig RAM MiB |
|---|---:|---:|---:|
| T-ranking | 137.66 | 164.24 | 3950.18 |
| T-packing | 147.53 | 162.21 | 3720.66 |

CPU/RAM gjelder lokal, overvåket dommerfase, ikke servermodellens ressurser eller alle hashkontroller. Begge fullførte faser bestod uendrede grenser. Metadatafeilens første ressurslogg beholdes separat. Flaggtall i hovedtabellen er dommervurderinger med tidligere godkjente eksakte lag; de manuelle risikoreviewene endrer ikke disse tallene og blokkerer en endelig anbefaling.

## Kildefunn før scoring

Dette er eksakt kontekstbundet kildegjennomgang, uten nye adjudikasjoner eller tildelte dekningspoeng.

- Packing/case 07: `source-03-006` forkastes ved 2 305 prompttokens. Symptom- og legekontakttekst er levert, mens baselinens komplette førstehjelpspassasje mangler. Det er en konkret eksponeringsregresjon for 07/1–3.
- Packing/case 17: `source-08-011` leverer generell legevaktinstruks under anafylaksitittel, mens akuttpassasjene `source-08-001/003/004` mangler. Samme risiko som tidligere P1 er gjeninnført; varianten kan ikke anbefales på totalscore.
- Packing/case 13: `source-11-003` er faktisk levert, med aktivering ved livsfare og ved usikkerhet. Generelle 113-instrukser finnes fortsatt; risikovurdering av hele den nye konteksten gjenstår.
- Ranking: bruddpassasjen flyttes 20→12, men forkastes ved 2 131 tokens; kjemipassasjen flyttes 13→7 og leveres i case 03. Kokepassasjen forkastes ved 2 068 tokens. Dette er kildeeksponering, ikke scorede kravgevinster.
- Ytre blødning/113 (rang 47), full pust/HLR (22), nødpeiler (17) og anafylaksisymptomer/akuttkilder (23/44/52) er fortsatt utenfor den nye rangeringens topp 16. Å representere hele teksten løser ikke disse alene.

De fulle bindingene, sporene og source-teksthashene finnes i maskinlesbar sammenligning og separat preflight-review. Dette dokumenterer effekt av den nye representasjonen samlet; det isolerer ikke avkorting som eneste årsak.

## Kildekontroll av scorede resultater

Separat kontroll med eksakt kontekst- og cachebinding, uten endrede råscorer eller nye adjudikasjoner.
- T-ranking/case-03: Covered item 5 is supported by delivered warning covering chemical/toxic contamination, ineffective boiling/disinfection and alternative water source. Items 3/4 remain missing; boiling-time passage was rejected by budget.
- T-ranking/case-07: All four baseline burn requirements remain covered; complete first-aid parent is actually delivered. No new risk flag.
- T-ranking/case-13: Both beacon requirements remain missing. Judge flags generic immediate 113 instruction as potentially misleading without mobile coverage; no direct conflict. This agrees with approved V3 risk interpretation.
- T-packing/case-01: Rest/avoid-loading text remains, but the explicit movement-worsens-injury/pain part is missing. Baseline source-04-006 is excluded in the new atomic source-04-005/006 packet at 2485 tokens after other-document priority. This is a real coverage loss; ordering and packet expansion both changed, so their individual effects are not isolated.
- T-packing/case-05: Baseline fallback outdoor-risk measures source-22-004 are rejected at 2084 tokens. Delivered general outdoor-unsafety/shelter guidance does not state the terrain-exit/fallback-risk-reduction requirements fully. Losses 3/6 are source-supported; overhang semantic coverage is retained, not reversed.
- T-packing/case-06: Baseline warmth/monitoring/113-on-deterioration source-02-009 is absent. It is not in top16 and belongs to a sibling heading; the new same-heading/ancestor packet does not include it, while P3 did. This is a packing-expansion loss, not a documented budget rejection of that source.
- T-packing/case-07: Baseline full burn-first-aid source-03-006 is rejected at 2305 tokens. Only symptoms and doctor-contact material remain. Items 1/2/3 correctly lose full coverage; item4 remains covered. Packing fails the protected burn requirement.
- T-packing/case-13: Both beacon requirements are fully supported by delivered source-11-003. This is a meaningful whole-context difference from baseline. Judge risk flag is negative, but generic immediate 113 instructions remain unqualified despite absent coverage. No safety improvement is credited from the missing flag; residual risk requires human review if this candidate is considered. Existing coverage losses already prevent recommending packing. No raw score or adjudication is changed.
- T-packing/case-17: Potentially misleading flag is supported: delivered generic urgent/GP-unavailable 116117 advice is under the anaphylaxis title, without the dedicated acute/symptom passages. Both required items remain missing. This reintroduces P1 medical-escalation risk. Raw direct-conflict flag is false while P1 flagged conflict; no safety improvement is credited from the lower subcategory count. Candidate is not recommended.
- T-packing/case-08: Adult airway and 10-second see/listen/feel passage is rejected in the source-01-003/004 packet at 2207 tokens. Child and hypothermia instructions do not cover the adult case. New unqualified 116117 instruction under adult CPR title supports the misleading flag. The secondary side-position risk route is less conclusive because a normal-breathing condition is also delivered; no separate flag reduction is applied.
- T-packing/case-10: Actual overnight-equipment list with sleeping bag/survival blanket is rejected at 2119 tokens. Its introductory sentence is delivered without the list; required insulation equipment is missing.
- T-packing/case-19: Explicit transmitter/receiver, shovel and probe requirement is rejected at 2018 tokens. The delivered all-members reference source-17-002 lacks its equipment antecedent. This is a real incomplete-instruction regression.
- T-packing/case-21: Delivered source-21-009 explicitly supports filtering before disinfection and following product instructions. Item2 is a source-supported gain.
- C-P3/case-16: The same external-bleeding pressure/lying-down instructions occur in all three contexts. Packing additionally includes a large-blood-loss introduction, not a newly added pressure instruction. Raw misleading classification differs (P3/ranking false, packing true); context effects versus judge interpretation are not established. Do not report this as a proven newly introduced hazard or a safety improvement. Preserve raw scores; exact-input scope/risk classification remains for human review. This does not rescue packing from twelve independently confirmed coverage losses.
- T-ranking/case-16: The same external-bleeding pressure/lying-down instructions occur in all three contexts. Packing additionally includes a large-blood-loss introduction, not a newly added pressure instruction. Raw misleading classification differs (P3/ranking false, packing true); context effects versus judge interpretation are not established. Do not report this as a proven newly introduced hazard or a safety improvement. Preserve raw scores; exact-input scope/risk classification remains for human review. This does not rescue packing from twelve independently confirmed coverage losses.
- T-packing/case-16: The same external-bleeding pressure/lying-down instructions occur in all three contexts. Packing additionally includes a large-blood-loss introduction, not a newly added pressure instruction. Raw misleading classification differs (P3/ranking false, packing true); context effects versus judge interpretation are not established. Do not report this as a proven newly introduced hazard or a safety improvement. Preserve raw scores; exact-input scope/risk classification remains for human review. This does not rescue packing from twelve independently confirmed coverage losses.
- T-packing/case-23: Indoor-lightning electrical-contact and plumbing precautions are lost together: source-22-003 is rejected at 2052 tokens after other-document priority. Generic shelter guidance does not cover these concrete indoor precautions.
