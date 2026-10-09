# M2-06 — utviklingsrapport ved stoppunktet

**Status: running_C. 30/31 konfigurasjoner fullt scoret.**

Resultatsnapshot 2026-10-09T16:50:43.893722+00:00; rapport 2026-10-09T17:01:22.985211+00:00.

P2 er fullført med 25 eksakte B16-cachetreff og bestått ressurskontroll. P3 kjører med uendrede regler. P1s tidligere RAM-feil, brannskadetap og anafylaksikonflikt bevares; sammenligningen er ennå ufullført.

## Frosset sammenligning og adjudikasjoner

A/B ble gjenbrukt. C bruker eierens eksplisitte forsøksvalg MiniLM/k16/ingen terskel og de opprinnelige P1/P2/P3-reglene. Bare overgangen fra B har et avgrenset eiergodkjent fravik fra dominansregelen. Ingen generell sikkerhetsport er fjernet, og en automatisk produksjonsvinner blir ikke valgt. Samme 25 spørsmål, kilde-/indekssnapshot, grounded promptserialisering, 2 000-tokenbudsjett, tokenizer, V3-prompt, schema og Sol Codex Medium/ChatGPT gjelder. Ingen betalt API eller svargenerering.

Case 13/P70: separat, eksakt inputbundet registrering av potensielt misvisende 113-råd uten dekning. Case 19/k12 og k16/p30: isredningssekvensen er avgrenset av faktisk levert vann-/is-tekst i source-19-001, med listen videreført i source-19-002 under samme leverte tittel/tema. Den er irrelevant for skredutstyr, uten dokumentert feil handling fra en uavgrenset skredinstruks. K12/k16-forskjellen er dommervariasjon; ekstra legevakttekst er ingen påvist sikkerhetsforbedring. Registreringene skjer under eierens delegerte review-autoritet, ikke som en påstått separat eiergodkjenning av hvert funn. Bare tre unike hele input korrigeres; identisk cacheinput kan forekomme under flere etiketter. De gamle godkjente case13/Gemma- og case20/MiniLM-bindingene beholdes separat.

Ingen råresultater, fasit, prompt, bevisregler eller P3-regler er overskrevet. Nye C-kontekster arver ikke historiske rettelser uten samme komplette inputidentitet. Uavklart betydning/risiko markeres review og hindrer automatisk valg. 25-settet har 22 støttede caser/72 krav og tre kunnskapshull; 15-slicen har 13 støttede caser/51 krav og to hull. Tom gap-kravliste gir aldri automatisk komplett pass.

B-tersklene ble frosset før sammenligningen fra 400 tillatte top-16-scorer, samlet over 25 spørsmål, med lineær numpy.percentile og inklusjon ved score ≥ terskel. p10=0,3411781549453735; p30=0,38985224068164825; p50=0,4206088036298752; p70=0,4637095630168915. C bruker ingen terskel. P3 beholder den frosne eksakte normaliserte tekstdedupliseringen og utvider bare de forhåndsdefinerte korte, sammenhengende seksjonsgrenene; øvrige treff bruker parent alene. Hele pakker prøves innen faktisk budsjett uten gold eller ekstra LLM. Reglene er ikke justert fra C-resultater.

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
| C-P2 | complete; 25/25 | 58/72 (80.56%) | 79.09% | 15/22 | 40/51 (78.43%) / 76.15% / 8/13 | 22 / 1 / 0 / 0 |
| C-P3 | partial; 12/25 | — | — | — | — | — |

## Ressurser og tokens

| Oppsett | Gj.snitt / maks prompttokens | Gj.snitt konteksttokens | Passasjer / forkastede pakker | Ranking / packing, s | Maks RSS / min ledig RAM, MiB | Worker-CPU, s |
|---|---:|---:|---:|---:|---:|---:|
| B-k16-none | 1957.88 / 1999 | 1766.44 | 278 / 122 | 0.01411 / 96.065 | 240.7 / 437.9 | 221.86 |
| C-P1 | 1969.80 / 1999 | 1778.36 | 287 / 161 | 0.01335 / 246.636 | 248.2 / 52.4 | 470.20 |
| C-P2 | 1957.88 / 1999 | 1766.44 | 278 / 122 | 0.01540 / 15.259 | 186.2 / 394.5 | 37.02 |

Ranking/packing bruker lagrede spørsmålsvektorer og inkluderer ikke embedding av et nytt spørsmål. Token-cache påvirker packing-tiden; worker-CPU inkluderer kontroller og tokenizerarbeid. Målingene er fra denne Windows-maskinen, ikke en mobilbenchmark. MiniLM-modell 235,05 MB, indeks 0,292 MB / 384 dimensjoner; modell/index endres ikke med packing. A viste omtrent 915 MB prosess-tre-RSS ved indeksarbeid; MiniLM dokumentvektorer var gjenbrukt. Gemma/Qwen har egne, ikke like full-indekstidsmålinger; detaljer beholdes i historisk v5 og resultat-JSON. 128-token embeddingavkorting og dens dokumenterte eksponering beholdes; ingen kontrafaktisk rangeringstest er kjørt. Ressursgrenser: 256 MiB tilgjengelig RAM og 4 GiB prosess-tre-RSS, samplet hvert 100 ms og kontrollert før/etter worker. Mobilminne, energibruk og full online latens er ikke målt.

C: 33 CLI-kallforsøk, 32 fullførte nye vurderinger, 30 cachetreff; rapporterte tokens `{"input_tokens": 257671, "cached_input_tokens": 10368, "cache_write_input_tokens": 0, "output_tokens": 73849, "reasoning_output_tokens": 6989, "total_tokens": 331520}`.

Samlet A+B+C: 223 forsøk, 221 fullførte, 541 cachetreff, 2 med ukjent tokenbruk; rapporterte tokens `{"input_tokens": 1662434, "cached_input_tokens": 228736, "cache_write_input_tokens": 0, "output_tokens": 393248, "reasoning_output_tokens": 45303, "total_tokens": 2055682}`; sum kalltid 11463.06 s.

Reasoning inngår i output, prefix-cached input i input. Det historiske kvoteavviste forsøket er bevart og medregnet med ukjent bruk; ingen estimert nullbruk eller API-kostnad. CLI-serverrevisjon eksponeres ikke, mens forespurt/katalogmodell gpt-6.1-sol, Medium, CLI-versjon og abonnementsauth er frosset og kontrollert. Kvoter gjelder den delte kontoen.

Forbruk i delrapporter inkluderer pågående kall med foreløpig ukjent bruk. Konfigurasjoner regnes først som fullført etter lagret sluttsummary; scorer alene godkjenner ikke ressurskontrollen.

Siste kvote 2026-10-09T14:33:25.477847+00:00: 5t 76% brukt, uke 80% brukt. Ingen betalt API-fallback eller reset-kreditt.

Offline integritetskontroll består: 725 case-resultater, 82 frosne identitetsfiler og 2912 bevarte A/B-filer. Kildeproveniens, full serialisering/token-cache, input-/resultatsegl, schema, kildebevis, raw/justerte aggregater og registrerte risikodelta er kontrollert uten nye dommerkall. Seks nye C-kontrolltester og ni eksisterende fortsettelsestester bestod. Integritet er ikke uavhengig sikkerhetsvalidering.

## Pågående sluttgjennomgang

P1 er bevart og verifisert uten nye kall. P2 har identiske 25 kontekster og resultater som B16, uten nye dommerkall. P3 er under vurdering; ingen endelig konfigurasjon anbefales før sammenligningen og kildekontrollen er ferdig. Den opprinnelige P1-ressursfeilen er historisk og blir ikke merket bestått. Se v6 for det tidligere stoppunktet.


Historisk manuell B8: 34/51, 7/13 komplette på opprinnelige 15 spørsmål. Endret dommer gjør dette til historisk referanse, ikke kontrollert effektmåling mot dagens 25-sett. Utviklingssettet brukes til kalibrering/valg; holdout er ikke åpnet eller kjørt. Råtekst, modeller, indekser og logger beholdes lokalt. Ingen produksjonskonfigurasjon eller Qwen-svargenerering er endret. M2-06 forblir åpen for senere produkt-/sikkerhetsarbeid.
