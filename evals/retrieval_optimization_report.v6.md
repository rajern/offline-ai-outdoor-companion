# M2-06 — utviklingsrapport etter fase C / ressursstopp

**Status: blocked. 29/31 konfigurasjoner fullt scoret.**

Resultatsnapshot 2026-10-09T14:27:59.169168+00:00; rapport 2026-10-09T14:35:00.905838+00:00.

Stoppgrunn: Resource guard: process RSS limit or available RAM reserve exceeded

P1 har høyest observert aggregat, 63/72 krav og 17/22 komplette, men mister tre brannskadekrav og introduserer anafylaksikonflikt. Minnereserven brøt etter alle 25 lagrede vurderinger. P2/P3 er ikke startet; ingen endelig konfigurasjon anbefales.

C-P1 har 25 gyldige lagrede vurderinger, men score-worker bestod ikke ressurskontrollen. Status «complete» i råtabellen betyr at resultatene er komplett scoret; den godkjenner ikke ressurskjøringen. C-P2 og C-P3 er ikke startet. Fase C og hele sammenligningen er derfor ufullført.

## Frosset sammenligning og adjudikasjoner

A/B ble gjenbrukt. C bruker eierens eksplisitte forsøksvalg MiniLM/k16/ingen terskel og de opprinnelige P1/P2/P3-reglene. Bare overgangen fra B har et avgrenset eiergodkjent fravik fra dominansregelen. Ingen generell sikkerhetsport er fjernet, og en automatisk produksjonsvinner blir ikke valgt. Samme 25 spørsmål, kilde-/indekssnapshot, grounded promptserialisering, 2 000-tokenbudsjett, tokenizer, V3-prompt, schema og Sol Codex Medium/ChatGPT gjelder. Ingen betalt API eller svargenerering.

Case 13/P70: separat, eksakt inputbundet registrering av potensielt misvisende 113-råd uten dekning. Case 19/k12 og k16/p30: isredningssekvensen er avgrenset av faktisk levert vann-/is-tekst i source-19-001, med listen videreført i source-19-002 under samme leverte tittel/tema. Den er irrelevant for skredutstyr, uten dokumentert feil handling fra en uavgrenset skredinstruks. K12/k16-forskjellen er dommervariasjon; ekstra legevakttekst er ingen påvist sikkerhetsforbedring. Registreringene skjer under eierens delegerte review-autoritet, ikke som en påstått separat eiergodkjenning av hvert funn. Bare tre unike hele input korrigeres; identisk cacheinput kan forekomme under flere etiketter. De gamle godkjente case13/Gemma- og case20/MiniLM-bindingene beholdes separat.

Ingen råresultater, fasit, prompt, bevisregler eller P3-regler er overskrevet. Nye C-kontekster arver ikke historiske rettelser uten samme komplette inputidentitet. Uavklart betydning/risiko markeres review og hindrer automatisk valg. 25-settet har 22 støttede caser/72 krav og tre kunnskapshull; 15-slicen har 13 støttede caser/51 krav og to hull. Tom gap-kravliste gir aldri automatisk komplett pass.

## Alle 31 konfigurasjoner

Justert analyse. Flagg er antall støttede caser med irrelevant / potensielt misvisende / direkte konflikt / geografisk lekkasje.

| ID | Status | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | Flagg |
|---|---|---:|---:|---:|---|---|
| A-minilm | complete; 25/25 | 57/72 (79.17%) | 77.95% | 15/22 | 39/51 (76.47%) / 74.23% / 8/13 | 22 / 1 / 0 / 0 |
| A-gemma2 | complete; 25/25 | 51/72 (70.83%) | 74.09% | 13/22 | 34/51 (66.67%) / 68.97% / 7/13 | 22 / 1 / 0 / 0 |
| A-qwen3-q4 | complete; 25/25 | 37/72 (51.39%) | 54.92% | 10/22 | 20/51 (39.22%) / 36.54% / 3/13 | 21 / 0 / 0 / 0 |
| B-k3-none | complete; 25/25 | 40/72 (55.56%) | 55.23% | 8/22 | 25/51 (49.02%) / 44.74% / 3/13 | 20 / 2 / 0 / 0 |
| B-k3-p10 | complete; 25/25 | 35/72 (48.61%) | 50.68% | 7/22 | 20/51 (39.22%) / 37.05% / 2/13 | 19 / 2 / 0 / 0 |
| B-k3-p30 | complete; 25/25 | 35/72 (48.61%) | 50.68% | 7/22 | 20/51 (39.22%) / 37.05% / 2/13 | 19 / 2 / 0 / 0 |
| B-k3-p50 | complete; 25/25 | 35/72 (48.61%) | 50.68% | 7/22 | 20/51 (39.22%) / 37.05% / 2/13 | 18 / 2 / 0 / 0 |
| B-k3-p70 | complete; 25/25 | 25/72 (34.72%) | 41.97% | 6/22 | 10/51 (19.61%) / 22.31% / 1/13 | 17 / 2 / 0 / 0 |
| B-k5-none | complete; 25/25 | 48/72 (66.67%) | 65.83% | 10/22 | 33/51 (64.71%) / 62.69% / 5/13 | 20 / 2 / 0 / 0 |
| B-k5-p10 | complete; 25/25 | 43/72 (59.72%) | 61.29% | 9/22 | 28/51 (54.90%) / 55.00% / 4/13 | 19 / 2 / 0 / 0 |
| B-k5-p30 | complete; 25/25 | 43/72 (59.72%) | 61.29% | 9/22 | 28/51 (54.90%) / 55.00% / 4/13 | 19 / 2 / 0 / 0 |
| B-k5-p50 | complete; 25/25 | 43/72 (59.72%) | 61.29% | 9/22 | 28/51 (54.90%) / 55.00% / 4/13 | 18 / 2 / 0 / 0 |
| B-k5-p70 | complete; 25/25 | 32/72 (44.44%) | 51.06% | 8/22 | 17/51 (33.33%) / 37.69% / 3/13 | 17 / 2 / 0 / 0 |
| B-k8-none | complete; 25/25 | 57/72 (79.17%) | 77.95% | 15/22 | 39/51 (76.47%) / 74.23% / 8/13 | 22 / 1 / 0 / 0 |
| B-k8-p10 | complete; 25/25 | 52/72 (72.22%) | 73.41% | 14/22 | 34/51 (66.67%) / 66.54% / 7/13 | 21 / 1 / 0 / 0 |
| B-k8-p30 | complete; 25/25 | 51/72 (70.83%) | 72.27% | 14/22 | 33/51 (64.71%) / 64.62% / 7/13 | 21 / 1 / 0 / 0 |
| B-k8-p50 | complete; 25/25 | 47/72 (65.28%) | 68.11% | 12/22 | 29/51 (56.86%) / 57.56% / 5/13 | 20 / 1 / 0 / 0 |
| B-k8-p70 | complete; 25/25 | 34/72 (47.22%) | 54.85% | 10/22 | 18/51 (35.29%) / 40.26% / 4/13 | 18 / 1 / 0 / 0 |
| B-k12-none | complete; 25/25 | 58/72 (80.56%) | 79.09% | 15/22 | 40/51 (78.43%) / 76.15% / 8/13 | 22 / 1 / 0 / 0 |
| B-k12-p10 | complete; 25/25 | 53/72 (73.61%) | 74.55% | 14/22 | 35/51 (68.63%) / 68.46% / 7/13 | 21 / 1 / 0 / 0 |
| B-k12-p30 | complete; 25/25 | 51/72 (70.83%) | 72.27% | 14/22 | 33/51 (64.71%) / 64.62% / 7/13 | 21 / 1 / 0 / 0 |
| B-k12-p50 | complete; 25/25 | 47/72 (65.28%) | 68.11% | 12/22 | 29/51 (56.86%) / 57.56% / 5/13 | 20 / 1 / 0 / 0 |
| B-k12-p70 | complete; 25/25 | 34/72 (47.22%) | 54.85% | 10/22 | 18/51 (35.29%) / 40.26% / 4/13 | 18 / 1 / 0 / 0 |
| B-k16-none | complete; 25/25 | 58/72 (80.56%) | 79.09% | 15/22 | 40/51 (78.43%) / 76.15% / 8/13 | 22 / 1 / 0 / 0 |
| B-k16-p10 | complete; 25/25 | 53/72 (73.61%) | 74.55% | 14/22 | 35/51 (68.63%) / 68.46% / 7/13 | 21 / 1 / 0 / 0 |
| B-k16-p30 | complete; 25/25 | 51/72 (70.83%) | 72.27% | 14/22 | 33/51 (64.71%) / 64.62% / 7/13 | 21 / 1 / 0 / 0 |
| B-k16-p50 | complete; 25/25 | 47/72 (65.28%) | 68.11% | 12/22 | 29/51 (56.86%) / 57.56% / 5/13 | 20 / 1 / 0 / 0 |
| B-k16-p70 | complete; 25/25 | 34/72 (47.22%) | 54.85% | 10/22 | 18/51 (35.29%) / 40.26% / 4/13 | 18 / 1 / 0 / 0 |
| C-P1 | complete; 25/25 | 63/72 (87.50%) | 85.23% | 17/22 | 44/51 (86.27%) / 82.69% / 9/13 | 22 / 2 / 1 / 0 |
| C-P2 | not_run; 0/25 | — | — | — | — | — |
| C-P3 | not_run; 0/25 | — | — | — | — | — |

## Ressurser og tokens

| Oppsett | Gj.snitt / maks prompttokens | Gj.snitt konteksttokens | Passasjer / forkastede pakker | Ranking / packing, s | Maks RSS / min ledig RAM, MiB | Worker-CPU, s |
|---|---:|---:|---:|---:|---:|---:|
| B-k16-none | 1957.88 / 1999 | 1766.44 | 278 / 122 | 0.01411 / 96.065 | 240.7 / 437.9 | 221.86 |
| C-P1 | 1969.80 / 1999 | 1778.36 | 287 / 161 | 0.01335 / 246.636 | 248.2 / 52.4 | 470.20 |

Ranking/packing bruker lagrede spørsmålsvektorer og inkluderer ikke embedding av et nytt spørsmål. Token-cache påvirker packing-tiden; worker-CPU inkluderer kontroller og tokenizerarbeid. Målingene er fra denne Windows-maskinen, ikke en mobilbenchmark. MiniLM-modell 235,05 MB, indeks 0,292 MB / 384 dimensjoner; modell/index endres ikke med packing. A viste omtrent 915 MB prosess-tre-RSS ved indeksarbeid; MiniLM dokumentvektorer var gjenbrukt. Gemma/Qwen har egne, ikke like full-indekstidsmålinger; detaljer beholdes i historisk v5 og resultat-JSON. 128-token embeddingavkorting og dens dokumenterte eksponering beholdes; ingen kontrafaktisk rangeringstest er kjørt. Ressursgrenser: 256 MiB tilgjengelig RAM og 4 GiB prosess-tre-RSS, samplet hvert 100 ms og kontrollert før/etter worker. Mobilminne, energibruk og full online latens er ikke målt.

C: 24 CLI-kallforsøk, 24 fullførte nye vurderinger, 1 cachetreff; rapporterte tokens `{"input_tokens": 192976, "cached_input_tokens": 6912, "cache_write_input_tokens": 0, "output_tokens": 55838, "reasoning_output_tokens": 5266, "total_tokens": 248814}`.

Samlet A+B+C: 214 forsøk, 213 fullførte, 512 cachetreff, 1 med ukjent tokenbruk; rapporterte tokens `{"input_tokens": 1597739, "cached_input_tokens": 225280, "cache_write_input_tokens": 0, "output_tokens": 375237, "reasoning_output_tokens": 43580, "total_tokens": 1972976}`; sum kalltid 11015.00 s.

Reasoning inngår i output, prefix-cached input i input. Det historiske kvoteavviste forsøket er bevart og medregnet med ukjent bruk; ingen estimert nullbruk eller API-kostnad. CLI-serverrevisjon eksponeres ikke, mens forespurt/katalogmodell gpt-6.1-sol, Medium, CLI-versjon og abonnementsauth er frosset og kontrollert. Kvoter gjelder den delte kontoen.

Siste kvote 2026-10-09T14:33:25.477847+00:00: 5t 76% brukt, uke 80% brukt. Ingen betalt API-fallback eller reset-kreditt.

Offline integritetskontroll består: 725 case-resultater, 82 frosne identitetsfiler og 2912 bevarte A/B-filer. Kildeproveniens, full serialisering/token-cache, input-/resultatsegl, schema, kildebevis, raw/justerte aggregater og registrerte risikodelta er kontrollert uten nye dommerkall. Seks nye C-kontrolltester og ni eksisterende fortsettelsestester bestod. Integritet er ikke uavhengig sikkerhetsvalidering.

## Konklusjon og rangering ved stoppunktet

Dette er en etterprøvbar delrapport ved en reell ressursblokkering, ikke en ferdig P1/P2/P3-sammenligning. 29 konfigurasjoner har alle 25 vurderinger lagret (725 rader). P1s score-worker feilet etterkontrollen fordi tilgjengelig RAM falt til 52,42 MiB, mot uendret reserve 256 MiB. Prosess-tre-RSS var maksimalt 231,53 MiB, under grensen 4 GiB. Retrieval-worker bestod med minimum 1 683,45 MiB tilgjengelig RAM og maksimalt 248,20 MiB RSS. Ressursprøven er ikke godkjent selv om alle P1-resultatene er lagret. C-P2 og C-P3 er ikke startet.

**Høyest observert aggregat er MiniLM/k16/ingen terskel/P1: 63/72 krav (87,50 %), macro 85,23 %, 17/22 komplette støttede caser.** B-k16/ingen terskel/P2 har 58/72 (80,56 %), macro 79,09 %, 15/22. P1 gir +5 krav, +6,94 prosentpoeng micro, +6,14 prosentpoeng macro og +2 komplette caser. Mot separat justert MiniLM-A er gevinsten +6 krav, +8,33 prosentpoeng micro og +2 komplette. Den opprinnelige 15-slicen forbedres fra B16s 40/51 (78,43 %), macro 76,15 %, 8/13 komplette til P1s 44/51 (86,27 %), macro 82,69 %, 9/13 komplette. Case 21-gevinsten inngår bare i 25-settet.

Rangeringen kan bare oppgis langs ulike mål:

1. **Dekning blant observerte MiniLM-oppsett:** P1 høyest; deretter B12/B16 uten terskel med samme dekning. P1 er ikke en trygg produksjonsanbefaling: den mister brannskadeinstrukser og introduserer en konkret anafylaksikonflikt.
2. **Baseline for fortsatt planlagt sammenligning:** Behold eierens frosne MiniLM/k16/ingen terskel som forsøksgrunnlag. B16/P2 har færre risikoflagg enn P1, men mangler flere viktige krav. Det er ikke en sikkerhetsgodkjenning. C-P2 forventes å kunne gjenbruke identisk B16-input, men en faktisk C-kjøring er ikke gjennomført.
3. **P3:** Uvurdert. Det finnes ingen støtte for å rangere eller anbefale den. MiniLMs embeddingvalg gjenåpnes ikke i denne oppgaven.

Ingen konfigurasjon erklæres som endelig vinner, ingen automatisk dominansport overstyres utover den uttrykkelig godkjente B→C-overgangen, og ingen prosentgrense innføres.

## Kildekontroll av forbedringer og regresjoner

| Case / krav | B16/P2 → P1 | Faktisk levert kildegrunnlag og forklaring |
|---|---|---|
| 01/1–3, mulig brudd og legekontakt | Mangler → dekket; samlet 1/4 → 4/4 | P1 leverer source-04-005 sammen med 04-006/003. Bruddmistanke ved manglende belastning, skillet fra forstuing og legekontakt støttes. Seksjonsnaboen kommer inn via seed 04-006, selv om 04-005 isolert var rang 20. |
| 03/3–5, begge kokeregler og kjemisk begrensning | Mangler → dekket; 2/5 → 5/5 | Source-21-010 leverer fosskoking, begge høydebetingelser og varigheter; 21-009 leverer kjemisk begrensning og alternativ vannkilde. B16 forkastet de aktuelle pakkene over budsjett; P1s seksjonspakke leverer dem. |
| 06/4, varme og overvåking | Mangler → dekket; 2/4 → 3/4 | Source-02-009 tilfører varme, overvåking og beskjed til 113 ved tilstandsendring. 06/1, 113 ved stor/ustoppelig ytre blødning, mangler fortsatt. 113 ved indre blødning eller senere endring dekker ikke hele dette kravet. |
| **07/1–3, brannskadebehandling** | **Dekket → mangler; 4/4 → 1/4** | Source-03-006 var levert i B16. I P1 bruker blant annet vannbehandlingsseksjonen budsjettet først; den relevante pakken forkastes ved 2 162 prompttokens. Avkjøling med temperatur/tid, forbud mot is og vern av blemmer er ikke levert. Legekontakt ved håndskade i 03-007 beholdes. |
| 08/4, full pust/HLR/113-sekvens | Mangler → mangler; fortsatt 3/4 | P1 leverer overvåking av normal pust i 07-007 og luftveisinstruks i 01-004, men ikke hele betingelsen for HLR ved fravær/unormal pust og 113 ved usikkerhet. Source-07-005 var rang 25, utenfor top-16. |
| **13/1–2, nødpeiler** | **Mangler → mangler; fortsatt 0/2** | P1 leverer generelle 113-instrukser, ingen source-11-003 med nødpeilerregelen. Den rangeres 16, men pakken ville gitt 2 082 tokens og forkastes (B16: 2 031). Potensielt misvisende-flagg er fortsatt riktig; ingen direkte konflikt registreres. |
| **17/1–2, anafylaksi** | **Mangler → mangler; fortsatt 0/2, ny risiko** | P1 leverer source-08-011, et legevaktkontaktfelt under faktisk levert anafylaksitittel. Uten den akutte 113-instruksen kan det styre brukeren til 116 117. Misvisende og direkte konflikt er kildebekreftet. B16 hadde forkastet 08-011 ved 2 055 tokens. Symptommønster 08-004 (rang 34) og akutt eskalering 08-001/003 er fortsatt utenfor relevant kandidatgrunnlag. |
| 19, skredutstyr / isredningsstøy | Fortsatt 2/2, irrelevant uten misvisende | P1 leverer 19-001 og 19-002 sammen og sammenhengende med vann-/isavgrensningen. Begge utstyr-/øvekrav støttes av 17-001/002. Dommerens negative risikoflagg stemmer med den komplette leverte konteksten. |
| 20/1–2, rute/ferdigheter og vær | Fortsatt 2/2 | Samme komplette input er cachet og gjenbrukt; ingen ny semantisk regel eller gold-endring. |
| 21/2, rekkefølge og produktforbehold | Mangler → dekket; 1/2 → 2/2 | Source-21-009 leverer filtrering før desinfeksjon og produktets bruksanvisning; 21-011 bevarer filterets virusbegrensning. Dette er full støtte, ikke bare korrekt sekvens uten produktforbehold. |

Alle støttede dekningsendringer mot B16 er åtte positive krav (01/1–3, 03/3–5, 06/4, 21/2) og tre tap (07/1–3), netto +5. De øvrige kravene er uendret. P1 har irrelevant informasjon i alle 22 støttede caser, to potensielt misvisende caser (13 og 17), én direkte konflikt (17) og ingen geografisk lekkasje. B16 har tilsvarende 22/1/0/0. Flaggene er indikatorer per case, ikke mål på andel støy eller risikoens alvorlighet.

## Gjenstående sikkerhetsmangler og kunnskapshull

P1 mangler ni av de 72 støttede kravene: 06/1 (varsling ved stor ytre blødning), 07/1–3 (tre brannskadetiltak), 08/4 (komplett pust/HLR/113-sekvens), 13/1–2 (nødpeiler) og 17/1–2 (anafylaksisymptomer/utløser og akutt eskalering). B16s 14 manglende krav er bevart i separat resultat-JSON. Ingen positiv vurdering er godkjent på en ufullstendig bevisrute; ingen uncertain, review eller sertifikat-/dommeruenighet er registrert i P1s råscorer. Disse nullene er ingen garanti for trygghet.

Kunnskapshullene består separat: case 14 mangler full forklaring/handlingsstøtte ved drønn og sprekker, og P1 leverer bare ett av de to støttede delkravene; case 15 mangler norske bålregler; case 25 mangler bygge-/stabilitetsprosedyre for improvisert ly. Ingen av hullene får komplett pass. Ingen kilder er lagt til.

MiniLMs frosne 128-token inputavkorting er dokumentert for eksisterende dokumentvisninger, blant annet relevante haler i pust-/anafylaksipassasjer. Lav rangering, fravær fra top-16 og eksakte budsjettavvisninger er målte forhold. At avkortingen alene forårsaker rangeringen er ikke demonstrert; ingen kontrafaktisk embeddingtest er kjørt. P1s forbedringer gir ikke grunn til å anta at P3 løser de gjenværende tapene.

## Neste praktiske steg og trygg gjenopptakelse

Før videre kjøring må vertens tilgjengelige RAM holde den opprinnelige reserven. Avklar større minnebruk i andre prosesser; ikke senk grensen og ikke konkluder med at det lille dommerprosesstreets RSS forklarer vertens minnefall. Etter at blokkeringen er løst og eieren ber om gjenopptakelse, kjør samme `continue_retrieval_phase_c_v1.py`. Fullt scoret C-P1 hoppes over og verifiseres; resterende C-P2/C-P3 bruker original indeks, parametere, cache og låsing. Ingen A/B- eller P1-dommerkall skal gjentas. Den feilende P1-ressursmålingen beholdes historisk, den må ikke merkes som bestått ved senere gjenopptakelse.

**Videre retrieval-forbedring er nødvendig før en meningsfull kontrolltest eller produktgodkjenning**, med mindre de to resterende planlagte testene faktisk dokumenterer at de kritiske tapene håndteres. De lave top-16-rangeringene for pust/anafylaksi gjør en slik løsning usannsynlig under nåværende packing-regler; det er likevel ikke en måling av P3. Fullfør først dagens avgrensede sammenligning. Et senere, separat godkjent utviklingssteg bør undersøke rangering av komplette prosedyrer og meningsbærende advarsler samt budsjettbeskyttelse mot duplisert kontakt-/sidefelttekst i eksisterende KB. Avkortingsbevisst embedding av korte visninger kan være en testbar hypotese. Ingen ny algoritme, ekstra eksperiment eller produksjonsendring er startet.

Rapporten og rådata er utviklingsgrunnlag. De er ikke en uavhengig sikkerhetsvalidering. Holdout er ikke åpnet, Qwen-svar er ikke generert, og M2-06 er ikke ferdig som produktoppgave.


Historisk manuell B8: 34/51, 7/13 komplette på opprinnelige 15 spørsmål. Endret dommer gjør dette til historisk referanse, ikke kontrollert effektmåling mot dagens 25-sett. Utviklingssettet brukes til kalibrering/valg; holdout er ikke åpnet eller kjørt. Råtekst, modeller, indekser og logger beholdes lokalt. Ingen produksjonskonfigurasjon eller Qwen-svargenerering er endret. M2-06 forblir åpen for senere produkt-/sikkerhetsarbeid.
