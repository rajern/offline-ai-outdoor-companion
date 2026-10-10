# M2-06 — avsluttende utviklingsrapport

**Status: comparison_complete. 31/31 konfigurasjoner fullt scoret.**

Resultatsnapshot 2026-10-09T17:08:07.247494+00:00; rapport 2026-10-10T06:47:47.288180+00:00.

Alle 31 konfigurasjoner er fullt scoret. P1 har høyest aggregat (63/72, 17/22 komplette), men mister tre brannskadekrav og introduserer anafylaksikonflikt. Foreløpig utviklingsanbefaling er MiniLM/k16/ingen terskel/P3 (59/72, 15/22), som bevarer B16s dekning og forbedrer 06/4. Tretten krav mangler fortsatt; ingen produksjons- eller kontrolltestgodkjenning.

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
| C-P3 | complete; 25/25 | 59/72 (81.94%) | 80.23% | 15/22 | 41/51 (80.39%) / 78.08% / 8/13 | 22 / 1 / 0 / 0 |

## Ressurser og tokens

| Oppsett | Gj.snitt / maks prompttokens | Gj.snitt konteksttokens | Passasjer / forkastede pakker | Ranking / packing, s | Maks RSS / min ledig RAM, MiB | Worker-CPU, s |
|---|---:|---:|---:|---:|---:|---:|
| B-k16-none | 1957.88 / 1999 | 1766.44 | 278 / 122 | 0.01411 / 96.065 | 240.7 / 437.9 | 221.86 |
| C-P1 | 1969.80 / 1999 | 1778.36 | 287 / 161 | 0.01335 / 246.636 | 248.2 / 52.4 | 470.20 |
| C-P2 | 1957.88 / 1999 | 1766.44 | 278 / 122 | 0.01540 / 15.259 | 186.2 / 394.5 | 37.02 |
| C-P3 | 1947.72 / 1998 | 1756.28 | 271 / 126 | 0.01515 / 143.998 | 248.0 / 282.0 | 282.81 |

Ranking/packing bruker lagrede spørsmålsvektorer og inkluderer ikke embedding av et nytt spørsmål. Token-cache påvirker packing-tiden; worker-CPU inkluderer kontroller og tokenizerarbeid. Målingene er fra denne Windows-maskinen, ikke en mobilbenchmark. MiniLM-modell 235,05 MB, indeks 0,292 MB / 384 dimensjoner; modell/index endres ikke med packing. A viste omtrent 915 MB prosess-tre-RSS ved indeksarbeid; MiniLM dokumentvektorer var gjenbrukt. Gemma/Qwen har egne, ikke like full-indekstidsmålinger; detaljer beholdes i historisk v5 og resultat-JSON. 128-token embeddingavkorting og dens dokumenterte eksponering beholdes; ingen kontrafaktisk rangeringstest er kjørt. Ressursgrenser: 256 MiB tilgjengelig RAM og 4 GiB prosess-tre-RSS, samplet hvert 100 ms og kontrollert før/etter worker. Mobilminne, energibruk og full online latens er ikke målt.

C: 39 CLI-kallforsøk, 39 fullførte nye vurderinger, 36 cachetreff; rapporterte tokens `{"input_tokens": 313122, "cached_input_tokens": 10368, "cache_write_input_tokens": 0, "output_tokens": 89198, "reasoning_output_tokens": 8670, "total_tokens": 402320}`.

Samlet A+B+C: 229 forsøk, 228 fullførte, 547 cachetreff, 1 med ukjent tokenbruk; rapporterte tokens `{"input_tokens": 1717885, "cached_input_tokens": 228736, "cache_write_input_tokens": 0, "output_tokens": 408597, "reasoning_output_tokens": 46984, "total_tokens": 2126482}`; sum kalltid 11858.62 s.

Reasoning inngår i output, prefix-cached input i input. Det historiske kvoteavviste forsøket er bevart og medregnet med ukjent bruk; ingen estimert nullbruk eller API-kostnad. CLI-serverrevisjon eksponeres ikke, mens forespurt/katalogmodell gpt-6.1-sol, Medium, CLI-versjon og abonnementsauth er frosset og kontrollert. Kvoter gjelder den delte kontoen.

Historisk kvoteobservasjon fra kjøringen (2026-10-09 after C completion): 5t 99% brukt, uke 84% brukt. Ingen betalt API-fallback eller reset-kreditt.

Offline integritetskontroll består: 775 case-resultater, 82 frosne identitetsfiler og 2912 bevarte A/B-filer. Kildeproveniens, full serialisering/token-cache, input-/resultatsegl, schema, kildebevis, raw/justerte aggregater og registrerte risikodelta er kontrollert uten nye dommerkall. Seks nye C-kontrolltester og ni eksisterende fortsettelsestester bestod. Integritet er ikke uavhengig sikkerhetsvalidering.

Alle 103 P1-filer er hashkontrollert uendret etter gjenopptakelsen. Den tidligere minnefeilen beholdes separat; den er ikke merket bestått.

## Anbefaling og avveininger

**Jeg anbefaler foreløpig MiniLM/k16/ingen terskel/P3 som utgangspunkt for videre utvikling. Ingen av oppsettene er klare for produksjonsvalg eller kontrolltesten.** P3 beholder alle dekkede B16/P2-krav og forbedrer 06/4 (varme, overvåking og varsling ved tilstandsendring), uten nye misvisende-, konflikt- eller geografiflagg. Dette er ett ekstra krav, ikke en ferdig sikkerhetsløsning. P1 har høyest totalscore, men mister tre brannskadekrav og introduserer en konkret anafylaksikonflikt. P2 er den enkleste referansen; P3s begrensede gevinst må veies mot ekstra packing-logikk. Ingen konfigurasjon dominerer alle andre på hvert krav og sikkerhetsflagg. Ingen automatisk vinner velges; eierens godkjente unntak gjaldt bare B→C-forsøksgrunnlaget.

| Utviklingsrangering | Krav / micro25 | Macro25 / komplette25 | Krav / micro15 | Macro15 / komplette15 |
|---|---:|---:|---:|---:|
| 1. P3, foreløpig utviklingsbaseline | 59/72 · 81,94 % | 80,23 % / 15/22 | 41/51 · 80,39 % | 78,08 % / 8/13 |
| 2. P2, enkel referanse | 58/72 · 80,56 % | 79,09 % / 15/22 | 40/51 · 78,43 % | 76,15 % / 8/13 |
| 3. P1, høyest aggregat | 63/72 · 87,50 % | 85,23 % / 17/22 | 44/51 · 86,27 % | 82,69 % / 9/13 |

Mot B16 gir P3 +1 krav, +1,39 prosentpoeng micro25, +1,14 prosentpoeng macro25 og uendret antall komplette. Mot justert MiniLM-A er gevinsten +2 krav, +2,78 prosentpoeng micro25, +2,27 prosentpoeng macro25 og fortsatt 15 komplette. P1 gir +5 krav og +2 komplette mot B16, men innebærer sikkerhetstap. Historisk rå MiniLM-A hadde 56 krav og 14 komplette; den tidligere eiergodkjente case20/1-adjudikasjonen forklarer justert 57/72 og 15/22. Rå og justerte analyser er separat bevart.

## Kildekontroll av gevinster og tap

| Case | B16/P2 | P1 | P3 | Faktisk levert tekst og dokumentert årsak |
|---|---:|---:|---:|---|
| 01, bruddmistanke og lege | 1/4 | 4/4 | 1/4 | P1 leverer source-04-005 som seksjonsnabo til seed 04-006, med bruddmistanke, skille fra forstuing og legekontakt. P3s frosne regler beholder 04-006 alene; 04-005 er isolert rang 20. |
| 03, vannkoking og kjemisk begrensning | 2/5 | 5/5 | 2/5 | P1 leverer 21-009/010 med begge høydebetingelser/varigheter og kjemisk begrensning. P3s tilsvarende kandidater avvises ved 2 086/2 062 prompttokens. |
| 06, stor ytre blødning | 2/4 | 3/4 | 3/4 | Begge utvidelsene leverer 02-009 for varme/overvåking og varsling ved endring. 06/1, 113 ved stor/ustoppelig ytre blødning, mangler i alle tre. Indre blødning eller senere endring erstatter ikke dette. |
| **07, brannskade** | **4/4** | **1/4** | **4/4** | P1s større vannpakke bruker budsjettet før 03-006, som avvises ved 2 162 tokens. P3 leverer hele 03-006 med avkjøling, tid/temperatur, forbud mot is og vern av blemmer; legekravet støttes av 03-007. |
| 08, pust og HLR | 3/4 | 3/4 | 3/4 | Alle mangler full 08/4. P3 leverer 07-007 (overvåking), voksen luftveis-/pustesjekk i 01-004 og HLR-teknikk i 01-006, men ikke betingelsen fravær/unormal pust → HLR og pust-usikkerhet → 113. 07-005 var rang 25, utenfor top-16. |
| **13, nødpeiler uten dekning** | **0/2** | **0/2** | **0/2** | 11-003 rangeres 16, men avvises ved henholdsvis 2 031 / 2 082 / 2 045 tokens. Alle leverer generelle telefoninstrukser uten nødpeilerinstruks og får potensielt misvisende-flagg, uten direkte konflikt. |
| **17, anafylaksi** | **0/2** | **0/2** | **0/2** | Symptomer/utløser og akutt eskalering er ikke levert. 08-004 var rang 34, og akutt 08-001/003 utenfor top-16. P1 leverer 08-011 under anafylaksitittel: 116 117 uten nødvendig akutt 113-støtte, med misvisende og direkte konflikt. P3 dedupliserer samme kontakttekst mot tidligere 04-010; konflikten uteblir, men ingen anafylaksiveiledning tilføres. |
| 19, skredutstyr og isredningsstøy | 2/2 | 2/2 | 2/2 | Utstyr til hver person og øving støttes av 17-001/002. 19-001/002 er samlet avgrenset til vann/is; irrelevant for utstyrsspørsmålet, uten konkret feil handlingsanvisning for skred. De ekstra k16-passasjene forklarte ikke historisk risikoendring. |
| 20, rute/ferdigheter og vær | 2/2 | 2/2 | 2/2 | Semantisk rute-/gruppevurdering og værplan er støttet. Tidligere adjudikasjon gjelder bare identiske hele input; ingen ny gold- eller bevisregel. |
| 21, rekkefølge og produktforbehold | 1/2 | 2/2 | 1/2 | P1 leverer 21-009 med rekkefølge og bruksanvisning. P3 har korrekt rekkefølge og filterets virusbegrensning, men mangler produktforbeholdet; 21-009 avvises ved 2 109 tokens. |

P1s åtte gevinster mot B16 er 01/1–3, 03/3–5, 06/4 og 21/2; tre tap er 07/1–3. P3s eneste dekningsendring mot B16 er 06/4. Ingen andre støttede scorer endres. Nye positive gevinster og sentrale finalistpassasjer er kontrollert mot faktisk levert tekst, ikke bare kilde-ID eller fravær av risikoflagg. Ingen uncertain, review eller sertifikat-/dommeruenighet er registrert i de 75 C-vurderingene.

P1 har 22 irrelevante støttede caser, to misvisende (13/17), én direkte konflikt (17) og null geografisk lekkasje. P2/P3 har 22/1/0/0. Direkte konflikt er en underkategori av misvisende. Flaggene er case-indikatorer, ikke prosent støy eller absolutt sikkerhet. K3/k5-kontekster uten hele isavgrensningen beholder sine gamle flagg. Ingen generell regel om at en kilde er trygg er innført.

## Mangler og neste praktiske steg

**P3 mangler 13 av 72 støttede krav:** 01/1–3 (bruddmistanke/skille/lege), 03/3–5 (begge kokeregler og kjemisk begrensning), 06/1 (varsling ved stor ytre blødning), 08/4 (full pust/HLR/113-sekvens), 13/1–2 (nødpeiler), 17/1–2 (anafylaksisymptomer/utløser og umiddelbar eskalering), 21/2 (produktforbehold). P2 mangler i tillegg 06/4. P1 mangler ni krav, inkludert tre brannskadekrav som P3 dekker. Ingen av oppsettene gir tilstrekkelig førstehjelpsgrunnlag.

Kunnskapshullene består separat: case 14 mangler full forklaring/handlingsstøtte ved drønn/sprekker og leverer bare ett av to støttede delkrav i alle tre oppsett; case 15 mangler norske bålregler; case 25 mangler trinnvis lybygging/stabilitets-/regntettingskriterier. Ingen tom kravliste får komplett pass. Ingen kilder er lagt til.

**Videre retrieval-forbedring bør komme før kontrolltesten.** Neste steg bør være en separat godkjent, målrettet undersøkelse av rangering og levering av komplette sikkerhetsprosedyrer i eksisterende KB: korte embeddingvisninger som ikke mister viktige haler, og budsjettbruk som hindrer dupliserte kontaktfelt eller store irrelevante seksjoner i å fortrenge handlinger/vilkår. Målrett de 13 manglende P3-kravene og bevar tidligere dekkede krav. P1 viser at enkelte brudd-/vannpassasjer kan leveres gjennom nabokontekst, mens brannskadetapet viser begrensningen ved mer ekspansjon alene. Ingen ny packer, reranker, gulljustering eller forsøksrunde er startet.

108 av 405 opprinnelige MiniLM-input ble avkortet ved den frosne 128-tokenbegrensningen, inkludert haler i relevante pust-/anafylaksipassasjer. Lav rangering og eksakte budsjettavvisninger er målte forhold. Avkortingens kausale bidrag er ikke bevist; ingen kontrafaktisk embeddingtest er gjort. Mangler i top-16 blir ikke løst bare ved å pakke bedre.

## Ressurshistorikk og endelig stoppunkt

P1s tidligere RAM-feil beholdes: 52,42 MiB tilgjengelig RAM mot 256 MiB, dommerprosesstreet bare 231,53 MiB RSS. Den blir ikke merket som bestått. Alle 25 svar var lagret og kilde-/token-/resultatkontrollert; kontekstscorene kan sammenlignes, mens operasjonell ressursgodkjenning for den kjøringen mangler. Etter eierens nye «fortsett» bestod en femsekunders RAM-/inputkontroll med minimum 980,14 MiB. P1s 103 filer og tidligere rapporter ble hashbevart; ingen P1-kall ble gjentatt.

P2 og P3 bestod de uendrede 256 MiB / 4 GiB-kontrollene. P3s minimum var 281,98 MiB tilgjengelig RAM under retrieval og 867,21 MiB under scoring; maksimal prosess-tre-RSS var 247,97 MiB. Retrieval-marginen er liten. Dette er ingen mobilkapasitetsmåling. P2s 25 input kom fra eksakt B16-cache. P3 brukte 15 nye kall og ti cachetreff. Hele C brukte 39 nye kall og 36 cachetreff. A/B ble ikke gjentatt. Et eldre kvoteavvist B-forsøk er bevart med ukjent bruk; videreføringen fikk ingen kvoteavvisning og brukte ingen reset-kreditt eller API-fallback.

Alle 31 forhåndsplanlagte konfigurasjoner / 775 case-vurderinger er lagret. Vi stopper her. Eieren må vurdere P3-anbefalingen og P1/P3-avveiningene og gi separat mandat for videre forbedring. Ingen holdout, produksjonsendring, Qwen-svargenerering eller ekstra parameterkombinasjon er kjørt. M2-06 forblir åpen fordi produkt-/sikkerhetsakseptansen ikke er oppfylt. Utviklingssettet er brukt til valg, ikke uavhengig validering.


Historisk manuell B8: 34/51, 7/13 komplette på opprinnelige 15 spørsmål. Endret dommer gjør dette til historisk referanse, ikke kontrollert effektmåling mot dagens 25-sett. Utviklingssettet brukes til kalibrering/valg; holdout er ikke åpnet eller kjørt. Råtekst, modeller, indekser og logger beholdes lokalt. Ingen produksjonskonfigurasjon eller Qwen-svargenerering er endret. M2-06 forblir åpen for senere produkt-/sikkerhetsarbeid.
