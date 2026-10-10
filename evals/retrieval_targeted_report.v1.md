# M2-06 — målrettet retrieval-runde

**Status: retrieval_complete.**

Tre varianter er frosset samlet før scoring. MiniLM, 16 unike parent-passasjer, ingen terskel, 2 000 tokens, samme kilder/gold/V3-dommer og eksakte adjudikasjonsbindinger. Ingen tidligere resultater er endret. Se `retrieval_targeted_plan.v2.md` og konfigurasjonsfilen v2. Teknisk revisjon 02 retter manglende skille mellom avkortet overskrift og brødtekst før scoring. Første revisjons 75 ubedømte kontekster er bevart; packing-forsøkets 25 kontekster gjenbrukes.

| Oppsett | Vurdert | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | I / M / K / G |
|---|---:|---:|---:|---:|---|---|
| P3 baseline | 25 | 59/72 (81,94 %) | 80,23 % | 15/22 | 41/51 / 78,08 % / 8/13 | 22 / 1 / 0 / 0 |
| T-ranking | 0/25 | ufullstendig | — | — | — | — |
| T-packing | 0/25 | ufullstendig | — | — | — | — |
| T-combined | 0/25 | ufullstendig | — | — | — | — |

## Kjøring og bevarte tekniske stopp

| Variant | Lagrede kontekster | Dommervurderinger |
|---|---:|---:|
| T-ranking | 25/25 | 0/25 |
| T-packing | 25/25 | 0/25 |
| T-combined | 25/25 | 0/25 |

Stoppmåling T-ranking: 241.41 MiB tilgjengelig RAM (krav 256 MiB); topp prosess-tre-RSS 185.45 MiB (grense 4096 MiB). Tilgjengelig vertsmaskin-RAM utløste stoppet; ekstern årsak er ikke fastslått. Ingen automatisk retry eller lemping av grensen.

## Kravgevinster og tap

**T-ranking**: kravgevinster, kravtap, udekkede krav og nye dommerflagg er **ikke vurdert** (0/25 scoret). Fravær av score er ingen dokumentasjon på fravær av risiko.

**T-packing**: kravgevinster, kravtap, udekkede krav og nye dommerflagg er **ikke vurdert** (0/25 scoret). Fravær av score er ingen dokumentasjon på fravær av risiko.

**T-combined**: kravgevinster, kravtap, udekkede krav og nye dommerflagg er **ikke vurdert** (0/25 scoret). Fravær av score er ingen dokumentasjon på fravær av risiko.

## Ressurser og abonnement

Indeksarbeid og ferske enkeltspørsmål måles separat fra ranking/packing på lagrede spørsmålsvektorer. Tid påvirkes av token-cache og integritetskontroller. Originalmodell og original indeks gjenbrukes for packing-forsøket; gammel indeksbyggetid er ikke en ny sammenlignbar benchmark. Windows-målinger dokumenterer ikke mobilens minne eller energibruk. Prosessgrense 4 GiB og tilgjengelig-RAM-reserve 256 MiB er uendret.

Tekniske forseglede cachekontroller: 2; disse utløser ingen fersk dommerinferens. Nye kall og cachetreff for konfigurasjonene loggføres separat nedenfor. GPT-6.1 Sol / Codex CLI / Medium / ChatGPT-auth og CLI-versjon er verifisert mot den frosne identiteten; CLI-resultatformatet eksponerer fortsatt ikke faktisk servermodell/revisjon.

Nye kall/tokens: `{"actual_calls": 0, "successful_calls": 0, "cache_hits": 0, "avoided_calls": 0, "usage": {}, "sum_call_seconds": 0, "unknown_usage_calls": 0, "errors": [], "billing": "ChatGPT subscription", "paid_api_calls": 0, "estimated_api_cost_usd": null}`.

Historiske A+B+C-tokens holdes separat: `{"actual_calls": 229, "successful_calls": 228, "cache_hits": 547, "avoided_calls": 547, "usage": {"input_tokens": 1717885, "cached_input_tokens": 228736, "cache_write_input_tokens": 0, "output_tokens": 408597, "reasoning_output_tokens": 46984, "total_tokens": 2126482}, "sum_call_seconds": 11858.624495299991, "unknown_usage_calls": 1, "errors": [{"cache_key": "1656049ce9e47022ec10495d8813cc5d20722f9bfac354347ece451996a0f0b6", "status": "archived_quota_rejection"}], "billing": "ChatGPT subscription", "paid_api_calls": 0, "estimated_api_cost_usd": null}`.

Reasoning inngår i output; prefix-cached input inngår i input. Ingen betalt API-fallback eller automatisk kvotereset.

Registrerte kvotevinduer: `[{"at": "2026-10-10 07:29:34 UTC", "phase": "before_targeted_judge_calls", "ordinaryUsageAllowed": true, "primary": {"usedPercent": 18, "windowDurationMins": 300, "resetsAt": 1791632706}, "secondary": {"usedPercent": 87, "windowDurationMins": 10080, "resetsAt": 1791961473}}, {"at": "2026-10-10 08:04:16 UTC", "phase": "after_ram_stop_before_any_targeted_judge_call", "ordinaryUsageAllowed": true, "primary": {"usedPercent": 31, "windowDurationMins": 300, "resetsAt": 1791632706}, "secondary": {"usedPercent": 89, "windowDurationMins": 10080, "resetsAt": 1791961473}}, {"at": "2026-10-10T08:52:29.026758+00:00", "phase": "owner_authorized_resume", "primary": {"usedPercent": 39, "windowDurationMins": 300, "resetsAt": 1791632706}, "secondary": {"usedPercent": 90, "windowDurationMins": 10080, "resetsAt": 1791961473}}]`. Dette er delt kontobruk; prosentendringer kan ikke tilskrives dommerkallene alene.

## Beslutningsstatus

Ingen automatisk produksjonsvinner. Alle nye sikkerhetsflagg, kravtap og viktige positive vurderinger må kildegjennomgås før anbefaling. Et ufullstendig eller review-blokkert forsøk kan ikke velges. De tre forhåndsdefinerte kunnskapshullene er fortsatt separate og gir ikke automatisk komplett pass. Det gjentatte utviklingssettet gir kalibreringsresultater, ikke uavhengig sikkerhetsvalidering.

Ingen nye micro/macro-scorer, komplette caser eller dommerflagg kan rapporteres. Baselinen 59/72 og 15/22 beholdes som utviklingsgrunnlag; nye varianter kan ikke anbefales eller rangeres ennå. Kontrollsettet er fortsatt ikke aktuelt: de 13 tidligere dokumenterte kravmanglene er ikke avklart gjennom denne kjøringen.

Etter frigjort RAM og eierens beskjed om gjenopptakelse kjøres samme `run_targeted_retrieval_v1.py run`. Den verifiserer/rebruker indeks, 25 packing-kontekster og 22 ranking-kontekster, ferdigstiller de siste tre ranking-kontekstene og kombinert variant, og kontrollerer alle input før dommerkall. Ingen justering av de frosne metodene fra disse observasjonene.

Korrigert indeks: 568 embedding-visninger, null avkortet brødtekst, 52 avkortede metadataoverskrifter; bygging 41.57 s / varm embedding 27.94 s. CPU 125.89 s; maksimal indeksbygge-RSS 1249.12 MiB; minimum tilgjengelig RAM 279.96 MiB. Fersk query-embedding snitt 22.69 ms / maks 26.53 ms. Query-vektorbytes identiske med baseline: True. Modell 235.053 MB; parent-indeks 0.292 MB; diagnostiske vindusvektorer 0.873 MB. Indeksbygge-RSS er ikke en måling av mobilappens RAM under vanlig spørsmålskjøring.

| Variant | Målte caser | Prompt snitt / maks | Kontekst snitt | Passasjer / forkastede pakker | Ranking / packing s |
|---|---:|---:|---:|---:|---:|
| T-ranking | 25 | 1959.60 / 1999 | 1768.16 | 265 / 129 | 0.0145 / 146.83 |
| T-packing | 25 | 1971.96 / 2000 | 1780.52 | 273 / 163 | 0.0141 / 325.12 |
| T-combined | 25 | 1958.60 / 1998 | 1767.16 | 266 / 165 | 0.0106 / 90.42 |

Ufullstendige ressursutvalg kan ikke sammenlignes som like store utvalg. Packing-målingene er fra første revisjons uendrede, gjenbrukte input; ranking-målingene er fra korrigert revisjon.

## Kildefunn før scoring

Dette er eksakt kontekstbundet kildegjennomgang, uten nye adjudikasjoner eller tildelte dekningspoeng.

- Packing/case 07: `source-03-006` forkastes ved 2 305 prompttokens. Symptom- og legekontakttekst er levert, mens baselinens komplette førstehjelpspassasje mangler. Det er en konkret eksponeringsregresjon for 07/1–3.
- Packing/case 17: `source-08-011` leverer generell legevaktinstruks under anafylaksitittel, mens akuttpassasjene `source-08-001/003/004` mangler. Samme risiko som tidligere P1 er gjeninnført; varianten kan ikke anbefales på totalscore.
- Packing/case 13: `source-11-003` er faktisk levert, med aktivering ved livsfare og ved usikkerhet. Generelle 113-instrukser finnes fortsatt; risikovurdering av hele den nye konteksten gjenstår.
- Ranking: bruddpassasjen flyttes 20→12, men forkastes ved 2 131 tokens; kjemipassasjen flyttes 13→7 og leveres i case 03. Kokepassasjen forkastes ved 2 068 tokens. Dette er kildeeksponering, ikke scorede kravgevinster.
- Ytre blødning/113 (rang 47), full pust/HLR (22), nødpeiler (17) og anafylaksisymptomer/akuttkilder (23/44/52) er fortsatt utenfor den nye rangeringens topp 16. Å representere hele teksten løser ikke disse alene.

De fulle bindingene, sporene og source-teksthashene finnes i maskinlesbar sammenligning og separat preflight-review. Dette dokumenterer effekt av den nye representasjonen samlet; det isolerer ikke avkorting som eneste årsak.
