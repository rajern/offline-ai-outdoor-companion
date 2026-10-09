# M2-06 — MiniLM fase B/C

Status: **blocked**, 4/31 konfigurasjoner fullført.

Kjøringen stoppet: Resource guard: process RSS limit or available RAM reserve exceeded

**B-k3-none er fullstendig vurdert, men består ikke ressurskontrollen.** Ledig RAM falt til 5,65 MiB under score-workerens kjøring, under reserven på 256 MiB. Score-workerens prosess-tre toppet på 230,2 MiB RSS; RSS-grensen på 4 GiB ble ikke brutt. Tallene nedenfor er bevarte diagnostiske resultater, ikke en teknisk godkjent kandidat. 24 B- og tre C-konfigurasjoner gjenstår. Stopp skjedde ved kontrollen etter score-worker; alle 25 resultater var da lagret. Målingen identifiserer ikke hvilken annen prosess som brukte RAM.

## Adjudikasjoner og metode

Eieren valgte MiniLM til forsøket 2026-10-09. Case 13/Gemma flagges som potensielt misvisende, uten direkte konflikt. Case 20/1/MiniLM godtas som semantisk dekning. Det godkjente v1-laget binder hver beslutning til case, levert konteksthash og full dommerinput/cache-nøkkel. Bare identisk input kan arve beslutningen i B/C. Nye kontekster får ingen automatisk adjudikasjon.

Alle 75 A-resultater og cacheforseglinger ble kontrollert uten nye dommerkall. Delta-kontrollen fant bare case 20s dekning/beslutning og case 13s flagg. Originale svar, scorer, gullkrav, prompt, corpus og fase A-filer beholdes uendret. MiniLM-baselinen er rått 56/72, 75,68% macro og 14/22 komplette; justert 57/72 (79,17%), 77,95% macro og 15/22 komplette. Den historiske 15-slicen endres ikke.

Videreføring bruker eksisterende workers, MiniLM-indeks og eksakt-input-cache, eksklusiv eksperiment-/dommerlåsing og feiljournal. 34 relevante automatiske tester består (9 fortsettelse, 13 orkestrering, 12 scorer/packing). Ingen fase A-modellkall er gjentatt. De 28 planlagte kombinasjonene og original packing/scoring er uendret.

Sluttaudit: 82 frosne identitetsfiler kontrollert, 309 A-filer uendret, alle 25 B-kontekst-/prompt-/token-/cachebindinger kontrollert. Ingen nye dommerkall i audit. Integriteten består; ressursporten består ikke. Se `retrieval_optimization_continuation_audit.v1.json` for eksakte SHA- og kilde-ID-bindinger.

Terskler, fryst før B: p10=0.34117815, p30=0.38985224, p50=0.42060880, p70=0.46370956. 400 jurisdiksjonsfiltrerte top-16-scorer fra lagrede A-minilm-resultater; `numpy.percentile(method="linear")`, inklusiv grense (`score >= threshold`).

## Alle konfigurasjoner

25-settet har 22 støttede caser / 72 krav og tre separate kunnskapshull. 15-slicen har 13 støttede caser / 51 krav og to kunnskapshull. Tabellen viser justert analyse. Flaggkolonnen er irrelevant / potensielt misvisende / direkte konflikt / geografisk lekkasje på støttede caser.

| Konfigurasjon | Status / vurdert | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | Flagg |
|---|---|---:|---:|---:|---|---|
| A-minilm | complete / 25/25 | 57/72 (79.2%) | 78.0% | 15/22 | 39/51 (76.5%) / 74.2% / 8/13 | 22 / 1 / 0 / 0 |
| A-gemma2 | complete / 25/25 | 51/72 (70.8%) | 74.1% | 13/22 | 34/51 (66.7%) / 69.0% / 7/13 | 22 / 1 / 0 / 0 |
| A-qwen3-q4 | complete / 25/25 | 37/72 (51.4%) | 54.9% | 10/22 | 20/51 (39.2%) / 36.5% / 3/13 | 21 / 0 / 0 / 0 |
| B-k3-none | complete / 25/25 | 40/72 (55.6%) | 55.2% | 8/22 | 25/51 (49.0%) / 44.7% / 3/13 | 20 / 2 / 0 / 0 |
| B-k3-p10 | not_run / 0/25 | — | — | — | — | — |
| B-k3-p30 | not_run / 0/25 | — | — | — | — | — |
| B-k3-p50 | not_run / 0/25 | — | — | — | — | — |
| B-k3-p70 | not_run / 0/25 | — | — | — | — | — |
| B-k5-none | not_run / 0/25 | — | — | — | — | — |
| B-k5-p10 | not_run / 0/25 | — | — | — | — | — |
| B-k5-p30 | not_run / 0/25 | — | — | — | — | — |
| B-k5-p50 | not_run / 0/25 | — | — | — | — | — |
| B-k5-p70 | not_run / 0/25 | — | — | — | — | — |
| B-k8-none | not_run / 0/25 | — | — | — | — | — |
| B-k8-p10 | not_run / 0/25 | — | — | — | — | — |
| B-k8-p30 | not_run / 0/25 | — | — | — | — | — |
| B-k8-p50 | not_run / 0/25 | — | — | — | — | — |
| B-k8-p70 | not_run / 0/25 | — | — | — | — | — |
| B-k12-none | not_run / 0/25 | — | — | — | — | — |
| B-k12-p10 | not_run / 0/25 | — | — | — | — | — |
| B-k12-p30 | not_run / 0/25 | — | — | — | — | — |
| B-k12-p50 | not_run / 0/25 | — | — | — | — | — |
| B-k12-p70 | not_run / 0/25 | — | — | — | — | — |
| B-k16-none | not_run / 0/25 | — | — | — | — | — |
| B-k16-p10 | not_run / 0/25 | — | — | — | — | — |
| B-k16-p30 | not_run / 0/25 | — | — | — | — | — |
| B-k16-p50 | not_run / 0/25 | — | — | — | — | — |
| B-k16-p70 | not_run / 0/25 | — | — | — | — | — |
| C-P1 | not_run / 0/25 | — | — | — | — | — |
| C-P2 | not_run / 0/25 | — | — | — | — | — |
| C-P3 | not_run / 0/25 | — | — | — | — | — |

Rå og justerte 25-/15-aggregater, casevise beslutninger, review og tokens er separat lagret i `retrieval_optimization_results.v4.json`. Ufullførte konfigurasjoner får ingen full-sett-score eller rangering.

## Ressurser og Codex-bruk

Grensene er uendret: 2 000 tokens for komplett grounded prompt, med original serialisering og låst tokenizer; 256 MiB ledig-RAM-reserve og 4 GiB samtidig prosess-tre-RSS. Alle workers kjøres sekvensielt. Tokenizer brukes bare til telling; ingen Qwen-svar genereres.

| Konfigurasjon | Gj.snitt / maks prompttokens | Gj.snitt konteksttokens | Passasjer totalt | Forkastede pakker | Ranking / retrieval+packing (s) |
|---|---:|---:|---:|---:|---:|
| A-minilm | 1487.7 / 1983 | 1296.3 | 198 | 2 | 0.02199 / 160.064 |
| A-gemma2 | 1670.8 / 2000 | 1479.3 | 193 | 7 | 0.00985 / 131.262 |
| A-qwen3-q4 | 1669.6 / 1989 | 1478.2 | 191 | 9 | 0.01120 / 140.591 |
| B-k3-none | 722.7 / 1038 | 531.3 | 75 | 0 | 0.01374 / 21.228 |

B/C-workers: høyeste observerte prosess-tre-RSS 246.6 MiB, laveste ledige RAM 5.7 MiB; sum observert CPU 149.75 s. Sampling 100 ms.
Retrieval+packing inkluderer tokenizer/cache-arbeid; gjentatte kontekster får fordel av varm cache. Dette er Windows-målinger, ikke mobilbenchmark.

MiniLM: 235.05 MB modell, 0.292 MB indeks, 384 dimensjoner. Eksisterende indeks gjenbrukes; intet nytt embeddingkall i B/C. Den kjente trunceringen ved 128 tokens er uendret (108/405 dokument-/spørsmålsvisninger; ingen spørsmål trunkert).

B/C: 22 faktiske nye dommerkall; 3 cachetreff/unngåtte kall. Rapporterte nye tokens: `{"input_tokens": 148537, "cached_input_tokens": 3456, "cache_write_input_tokens": 0, "output_tokens": 23952, "reasoning_output_tokens": 3871, "total_tokens": 172489}`.

Hele A+B/C: 97 faktiske kall, 97 vellykkede; 0 med ukjent bruk. Tokens: `{"input_tokens": 722491, "cached_input_tokens": 76032, "cache_write_input_tokens": 0, "output_tokens": 164929, "reasoning_output_tokens": 19673, "total_tokens": 887420}`.
Reasoning er del av output og prefix-cached input del av input; disse legges ikke til totalen på nytt. Sum dommerkalletid 4685.21 s. GPT-6.1 Sol / Codex CLI / Medium / ChatGPT-abonnement; betalte API-kall: 0.

Codex-kvote før B: 22% brukt i femtimersvinduet og 56% i ukesvinduet. Etter stoppen: 38% / 58%. Ingen kvotegrense var nådd. Dette er kontoens delte forbruk; prosentendringen kan ikke tilskrives B alene.

## Sikkerhet og anbefaling

Krav som følges spesielt: 01 brudd/lege, 03 og 21 vannbehandling, 08 luftvei/pust/overvåking/HLR, 13 nødpeiler uten mobildekning, 17 anafylaksi/akutt eskalering, 20 rute/ferdigheter. Tidligere kilde-/ranganalyse viser at full dekning av 08/4 og 17/1–2 ikke er tilgjengelig gjennom MiniLMs frosne top-16/P1/P3-regler. Dette forsøket kan derfor ikke alene gjøre løsningen tilstrekkelig trygg.

### Første B-resultat mot justert MiniLM-baseline

Dekningen faller fra 57/72 til 40/72: **−17 krav**, micro **−23,61 prosentpoeng**, macro **−22,73 prosentpoeng**, komplette **15 → 8**. Ingen nye dekkede krav etter godkjent A-justering. 15-slicen faller fra 39/51 til 25/51 (76,47% → 49,02%), macro 74,23% → 44,74%, komplette 8 → 3. Irrelevant-flagg faller 22 → 20; misvisende øker 1 → 2; direkte konflikt og geografi forblir 0. Ingen uncertain, review eller sertifikat-/dommeruenighet.

De 17 tapene er 01/4; 05/3,6; 07/1–4; 08/1; 10/2,3; 11/1,2; 12/1,2; 19/1; 23/2,3. Ingen pakker ble forkastet på tokenbudsjett i B-k3-none. Passasjer som ligger utenfor de tre første kandidatene blir ikke levert; det er dermed k-grensen, ikke en ny embedding eller budsjettforkasting, som endrer konteksten. Den eldre MiniLM-trunceringen er fortsatt en separat begrensning.

| Case | Udekket i B-k3-none | Levert grunnlag / konsekvens |
|---|---|---|
| 01 | 1–4: bruddmistanke, skille brudd/forstuing, legekontakt, ro/avlastning | Bare 19-004, 19-003 og 10-004; A dekket kun 01/4. Ingen bruddpassasje levert. |
| 03 | 3–5: full kokeprosedyre med høydebetingelser og kjemisk begrensning/alternativ kilde | 21-005 og 21-002 dekker klart/usikkert vann; 21-010 og 21-009 mangler fortsatt. |
| 08 | 1,2,4: 113 med veiledning; komplett luftvei/pustesjekk; overvåking/HLR/113 ved tvil | 07-003, 07-006, 01-010; bare sideleiekravet 08/3 fullt dekket. 08/1 er nytt tap mot A. Cachetreffet gjelder en eldre input, ikke A-baselinen. |
| 13 | 1–2: tidlig nødpeileraktivering og aktivering ved tvil | 01-027, 04-009, 03-008 leverer telefoninstruksjoner uten dekning; risiko beholdes. 11-003 mangler. |
| 17 | 1–2: symptom-/insektkobling og umiddelbar akutt eskalering | 17-003, 19-002, 05-003; ingen relevant full anafylaksipassasje. |
| 20 | Ingen av de to kravene mangler | 16-002 støtter rute/evner, 10-003 været. Ny dommerinput fikk begge krav covered uten overføring av A-adjudikasjonen. |
| 21 | 2: produktinstruksjoner som del av hele filtrer/desinfiser-kravet | 21-011 gir virusbegrensning og rekkefølge; 21-009 med produktforbehold mangler. |

Fortsatt udekkede krav på alle 22 støttede caser: 01/1–4; 03/3–5; 05/3,6; 06/1,4; 07/1–4; 08/1,2,4; 10/2,3; 11/1,2; 12/1,2; 13/1,2; 17/1,2; 19/1; 21/2; 23/2,3. Dette er 32 av 72 krav. De tre kunnskapshullene behandles fortsatt separat; 14 har bare 1/2 støtte, 15 og 25 har tom kravliste og aldri komplett pass.

### Det nye sikkerhetsflagget i case 19

Dommeren flagger **source-19-002, blokk 3** som både irrelevant og potensielt misvisende: isredningsråd om grein/stige/menneskekjede kan oppfattes som skredredning. I faktisk levert tekst står bare den generelle tittelen «Redning» og temaet «Redde andre»; situasjonen med is er ikke merket i denne blokken. Risikoen er derfor konkret og forenlig med V2-regelen om å skille irrelevans fra mulig feil handling. Direkte konflikt er ikke flagget. Den samme blokken finnes i A, som også leverer ekstra skred-/utstyrstekst og en eksplisitt Isskolen-blokk. Uten nye dommerkall kan vi ikke skille konteksteffekt fra dommervariasjon. Det nye risikoflagget beholdes, uten automatisk adjudikasjon. Den manglende konkrete utstyrslisten (17-001, A-blokk 6) er et separat sikkerhetskritisk tap.

Senere forbedringer utenfor dagens plan bør særlig undersøke rangeringen for 08/4 og 17/1–2, MiniLMs 128-token-avkorting og bevaring av situasjonsvilkår i kildepassasjer. Kildene finnes allerede lokalt; dette er ikke grunnlag for å legge til nye kilder eller endre gold. B/C må fullføres før andre parametervarianter vurderes.

Ingen endelig B/C-konfigurasjon kan anbefales fra denne ufullførte kjøringen. MiniLM er fortsatt eierens valgte forsøksmodell; A-baseline er referansen. Top_k=3 uten terskel/P2 gir klart svakere dekning og ett ekstra sikkerhetsflagg og anbefales ikke fremfor den justerte k=8-baselinen. Dette er ingen endelig rangering av de 27 uprøvde konfigurasjonene. En reell blokkering må avklares før resten gjenopptas.

Etter at tilstrekkelig RAM er tilgjengelig igjen, kan samme fortsettelseskommando gjenbruke den komplette B-k3-none-scoringen og fortsette ved B-k3-p10. Ingen av de 22 nye dommerkallene eller 75 A-kallene skal gjentas. Minnegrensen, tersklene og øvrige frosne innstillinger beholdes.

Historisk B8 hadde 34/51 krav og 7/13 komplette på 15-settet med andre manuelle vurderinger. Dette er historisk kontekst, ikke en kontrollert effekt mot dagens 25-sett.

Råkontekster, kildepassasjer, vektorer, token-/dommercache og logs bevares lokalt under `knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/` og `knowledge/local/judge-cache-v3/`. Den offentlige rapporten inneholder ikke kildetekst, modeller eller hemmeligheter. Holdout er ikke åpnet. Produksjonskonfigurasjonen er uendret. M2-06 forblir åpen.
