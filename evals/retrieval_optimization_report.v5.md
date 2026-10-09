# M2-06 — gjenopptatt MiniLM-optimalisering

**Status: blocked. 28/31 konfigurasjoner fullstendig vurdert.**

Resultatsnapshot: 2026-10-09T12:29:43.269077+00:00. Eksport: 2026-10-09T12:38:46.445492+00:00.

Kjøringen stoppet: Material per-case coverage/safety tradeoffs: no configuration dominates; owner decision required

Alle 25 B-konfigurasjoner er ferdige; 28/31 totalt. Den frosne dominansregelen stopper C, og kildekontrollen avdekker uavklarte risikovurderinger i case 13 og 19. Foreløpig anbefaling for C er MiniLM k=16 uten terskel; ingen produksjonsvinner er valgt.

## Metode og avgrensning

MiniLM er eierens valgte forsøksmodell. Fase A og B-k3-none gjenbrukes; ingen fullførte dommerkall gjentas. Alle caser bruker den samme frosne kildebasen, V3-prompten, schemaet, scoreren og Codex Sol Medium gjennom ChatGPT-abonnementet. Ingen betalt API, holdout, Qwen-svargenerering eller produksjonsendring.

Frosset dommeridentitet: `gpt-6.1-sol`, reasoning `medium`, `codex-cli 0.162.0-alpha.2`. Autentisering, modellkatalog og innstillinger kontrolleres før workerens kall. CLI eksponerer ikke eksakt serverrevisjon; den er fortsatt ukjent, ikke antatt identisk med en vekthash.

Case 13/Gemma og case 20/1/MiniLM justeres bare i det separat godkjente, eksakt-input-/kontekstbundne adjudikasjonslaget. Råresultater og gold er uendret. Justert MiniLM A-baseline: 57/72, micro 79.17%, macro 77.95%, 15/22 komplette. Råbaseline var 56/72 og 14/22; 15-slicen er uendret.

Ressursstoppen i den første B-kjøringen er bevart historisk: 5,65 MiB ledig RAM under score-worker, under 256 MiB-reserven. Alle 25 svarene var lagret og passerte integritetskontroll. Eieren autoriserte gjenopptakelse med omtrent 3 GiB tilgjengelig RAM. Grenser og eksperimentparametere ble ikke endret. Etter hver ny worker kontrolleres alle 100 ms-samplede RAM/RSS-målinger.

B bruker P2 og k=3/5/8/12/16 × ingen/p10/p30/p50/p70. C bruker P1/P2/P3 med valgt B-kandidat. Tersklene ble fryst før B fra 400 lagrede, jurisdiksjonsfiltrerte MiniLM top-16-scorer, `numpy.percentile(method="linear")`; `score >= threshold`. Ingen gold-/judge-tilpasning underveis. P1/P3-reglene ligger i den opprinnelige frysen; ingen ny LLM eller gold-aware packing.

Terskler: p10=0.34117815, p30=0.38985224, p50=0.42060880, p70=0.46370956.

25-settet: 22 støttede caser / 72 krav og tre separate kunnskapshull. 15-slice: 13 støttede caser / 51 krav og to kunnskapshull. Uncertain/review blokkerer valg; tom gap-kravliste blir aldri komplett pass. Den opprinnelige konservative valgregelen beskytter alle dekkede krav og misvisende-/konflikt-/geografifunn per case.

## Alle konfigurasjoner

Tallene viser justert analyse. Flagg: irrelevant / misvisende / direkte konflikt / geografisk lekkasje på støttede caser.

| ID | Status; vurderinger | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | Flagg |
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
| B-k12-none | complete; 25/25 | 58/72 (80.56%) | 79.09% | 15/22 | 40/51 (78.43%) / 76.15% / 8/13 | 22 / 2 / 0 / 0 |
| B-k12-p10 | complete; 25/25 | 53/72 (73.61%) | 74.55% | 14/22 | 35/51 (68.63%) / 68.46% / 7/13 | 21 / 2 / 0 / 0 |
| B-k12-p30 | complete; 25/25 | 51/72 (70.83%) | 72.27% | 14/22 | 33/51 (64.71%) / 64.62% / 7/13 | 21 / 2 / 0 / 0 |
| B-k12-p50 | complete; 25/25 | 47/72 (65.28%) | 68.11% | 12/22 | 29/51 (56.86%) / 57.56% / 5/13 | 20 / 1 / 0 / 0 |
| B-k12-p70 | complete; 25/25 | 34/72 (47.22%) | 54.85% | 10/22 | 18/51 (35.29%) / 40.26% / 4/13 | 18 / 0 / 0 / 0 |
| B-k16-none | complete; 25/25 | 58/72 (80.56%) | 79.09% | 15/22 | 40/51 (78.43%) / 76.15% / 8/13 | 22 / 1 / 0 / 0 |
| B-k16-p10 | complete; 25/25 | 53/72 (73.61%) | 74.55% | 14/22 | 35/51 (68.63%) / 68.46% / 7/13 | 21 / 1 / 0 / 0 |
| B-k16-p30 | complete; 25/25 | 51/72 (70.83%) | 72.27% | 14/22 | 33/51 (64.71%) / 64.62% / 7/13 | 21 / 2 / 0 / 0 |
| B-k16-p50 | complete; 25/25 | 47/72 (65.28%) | 68.11% | 12/22 | 29/51 (56.86%) / 57.56% / 5/13 | 20 / 1 / 0 / 0 |
| B-k16-p70 | complete; 25/25 | 34/72 (47.22%) | 54.85% | 10/22 | 18/51 (35.29%) / 40.26% / 4/13 | 18 / 0 / 0 / 0 |
| C-P1 | not_run; 0/25 | — | — | — | — | — |
| C-P2 | not_run; 0/25 | — | — | — | — | — |
| C-P3 | not_run; 0/25 | — | — | — | — | — |

Ufullstendige resultater rangeres ikke. Rå/justerte scorer, gap-resultater og sikkerhetens konteksthash/cache-nøkkel/kilde-ID-er er separat tilgjengelige i `retrieval_optimization_results.v5.json`.

## Ressurser og dommerkall

2 000 tokens gjelder hele serialiserte grounded prompt med den opprinnelige låste tokenizeren (samme avgrensning for chat-template-overhead). CPU/RAM er fra denne Windows-maskinen, ikke mobilbenchmark. Indeksen gjenbrukes; ingen nye embeddingkall i B/C. Worker-CPU inkluderer integritetskontroller; retrieval+packing inkluderer tokenizerarbeid og har varierende fordel av varm token-cache.

| ID | Gj.snitt / maks prompttokens | Gj.snitt konteksttokens | Passasjer | Forkastede pakker | Ranking / retrieval+packing, s |
|---|---:|---:|---:|---:|---:|
| A-minilm | 1487.7 / 1983 | 1296.3 | 198 | 2 | 0.02199 / 160.064 |
| A-gemma2 | 1670.8 / 2000 | 1479.3 | 193 | 7 | 0.00985 / 131.262 |
| A-qwen3-q4 | 1669.6 / 1989 | 1478.2 | 191 | 9 | 0.01120 / 140.591 |
| B-k3-none | 722.7 / 1038 | 531.3 | 75 | 0 | 0.01374 / 21.228 |
| B-k3-p10 | 703.0 / 1038 | 511.6 | 72 | 0 | 0.01207 / 3.775 |
| B-k3-p30 | 687.8 / 1038 | 496.4 | 70 | 0 | 0.01201 / 1.443 |
| B-k3-p50 | 676.8 / 1038 | 485.4 | 68 | 0 | 0.01291 / 2.304 |
| B-k3-p70 | 589.9 / 1038 | 398.6 | 57 | 0 | 0.01225 / 6.783 |
| B-k5-none | 1032.2 / 1578 | 840.7 | 125 | 0 | 0.01182 / 20.868 |
| B-k5-p10 | 1001.4 / 1578 | 810.0 | 120 | 0 | 0.01352 / 1.060 |
| B-k5-p30 | 967.6 / 1578 | 776.2 | 116 | 0 | 0.01377 / 1.017 |
| B-k5-p50 | 900.2 / 1578 | 708.8 | 105 | 0 | 0.01403 / 1.914 |
| B-k5-p70 | 740.5 / 1578 | 549.2 | 81 | 0 | 0.01406 / 0.835 |
| B-k8-none | 1487.7 / 1983 | 1296.3 | 198 | 2 | 0.01334 / 3.083 |
| B-k8-p10 | 1416.9 / 1983 | 1225.5 | 187 | 2 | 0.01340 / 3.029 |
| B-k8-p30 | 1313.9 / 1983 | 1122.5 | 173 | 2 | 0.01288 / 2.248 |
| B-k8-p50 | 1152.1 / 1983 | 960.8 | 146 | 2 | 0.01444 / 2.197 |
| B-k8-p70 | 892.8 / 1983 | 701.5 | 106 | 2 | 0.01433 / 4.774 |
| B-k12-none | 1900.1 / 1999 | 1708.7 | 263 | 37 | 0.01355 / 100.079 |
| B-k12-p10 | 1787.4 / 1999 | 1596.0 | 245 | 32 | 0.01352 / 3.761 |
| B-k12-p30 | 1581.0 / 1983 | 1389.6 | 212 | 24 | 0.01317 / 3.898 |
| B-k12-p50 | 1358.6 / 1983 | 1167.2 | 175 | 12 | 0.01136 / 4.321 |
| B-k12-p70 | 951.8 / 1983 | 760.5 | 114 | 3 | 0.01423 / 3.436 |
| B-k16-none | 1957.9 / 1999 | 1766.4 | 278 | 122 | 0.01411 / 96.065 |
| B-k16-p10 | 1842.2 / 1999 | 1650.8 | 259 | 101 | 0.01055 / 6.929 |
| B-k16-p30 | 1610.1 / 1983 | 1418.7 | 218 | 62 | 0.01134 / 2.790 |
| B-k16-p50 | 1365.6 / 1983 | 1174.3 | 177 | 23 | 0.01129 / 1.233 |
| B-k16-p70 | 951.8 / 1983 | 760.5 | 114 | 6 | 0.01039 / 0.741 |

| ID | Maks worker-tre RSS, MiB | Min ledig RAM, MiB | Sum worker-CPU, s | Ressursstatus |
|---|---:|---:|---:|---|
| B-k3-none | 246.6 | 5.7 | 149.75 | bevart grensebrudd |
| B-k3-p10 | 246.2 | 3055.9 | 22.64 | består |
| B-k3-p30 | 246.2 | 3090.8 | 23.42 | består |
| B-k3-p50 | 243.5 | 3140.2 | 25.45 | består |
| B-k3-p70 | 242.9 | 2808.7 | 47.45 | består |
| B-k5-none | 247.8 | 2114.2 | 151.17 | består |
| B-k5-p10 | 183.4 | 3179.1 | 24.78 | består |
| B-k5-p30 | 175.1 | 3564.0 | 25.83 | består |
| B-k5-p50 | 240.1 | 3625.3 | 29.47 | består |
| B-k5-p70 | 178.0 | 3996.9 | 24.92 | består |
| B-k8-none | 174.5 | 4093.9 | 25.86 | består |
| B-k8-p10 | 218.8 | 2796.9 | 43.84 | består |
| B-k8-p30 | 219.4 | 2704.9 | 34.05 | består |
| B-k8-p50 | 217.3 | 3343.6 | 31.30 | består |
| B-k8-p70 | 232.7 | 2738.8 | 62.91 | består |
| B-k12-none | 233.9 | 1314.4 | 311.14 | består |
| B-k12-p10 | 94.2 | 2999.5 | 24.78 | består |
| B-k12-p30 | 220.9 | 2407.1 | 46.02 | består |
| B-k12-p50 | 222.1 | 1956.3 | 50.11 | består |
| B-k12-p70 | 218.0 | 2692.7 | 50.31 | består |
| B-k16-none | 240.7 | 437.9 | 221.86 | består |
| B-k16-p10 | 213.3 | 2387.5 | 19.95 | består |
| B-k16-p30 | 248.3 | 2054.6 | 26.25 | består |
| B-k16-p50 | 203.9 | 2244.6 | 19.56 | består |
| B-k16-p70 | 199.9 | 2408.7 | 19.11 | består |

B/C-worker-RSS gjelder gjenbrukt indeks og fjern dommervurdering, ikke hele mobilappen. MiniLM har 235,05 MB modell og 0,292 MB indeks (384 dimensjoner); A-indeksarbeidet toppet på omtrent 915 MB prosess-tre-RSS. Gemma har 1 488,92 MB modell / 0,584 MB indeks; Qwen Q4 396,47 MB / 0,778 MB. MiniLMs dokumentvektorer ble gjenbrukt i A, mens de andre bygget dokumentvektorer; A-indekstidene er derfor ikke en lik full-indeks-benchmark. MiniLMs kjente 128-token-avkorting (108/405 visninger, ingen spørsmål) er uendret. Mobil-RAM, energibruk og samlet lokal svartid er fortsatt ikke målt.

Etter gjenopptakelse, eksklusive det historiske B-k3-none-forsøket: maks worker-tre-RSS 248.3 MiB, min ledig RAM 437.9 MiB, sum målt worker-CPU 1362.19 s. De opprinnelige 4 GiB/256 MiB-grensene bestod i disse workerne.

Spørsmålsvektorene er også lagrede. Ranking-/packing-tidene inkluderer derfor ikke embedding av et nytt brukerspørsmål. De er ikke full online retrieval-latens. Embeddingmålingene fra A og størrelses-/RAMdata rapporteres separat i resultat-JSON.


B/C: 115 CLI-kallforsøk, 114 fullførte vurderinger, 511 cachetreff/unngåtte kall; tokens `{"input_tokens": 830809, "cached_input_tokens": 145792, "cache_write_input_tokens": 0, "output_tokens": 178422, "reasoning_output_tokens": 22512, "total_tokens": 1009231}`.

Hele A+B/C: 190 kall, 189 vellykkede; tokens `{"input_tokens": 1404763, "cached_input_tokens": 218368, "cache_write_input_tokens": 0, "output_tokens": 319399, "reasoning_output_tokens": 38314, "total_tokens": 1724162}`; 1 med ukjent bruk; sum dommerkalletid 9415.46 s. Reasoning inngår i output, prefix-cached input i input; ingen dobbelttelling.

Før denne gjenopptakelsen: femtimerskvote 43% brukt, ukeskvote 59% brukt. Dette er kontoens delte bruk; eval-tokenregnskapet over er separat. Ingen automatisk API-fallback eller kvotereset.

1 kvoteavvist forsøk er bevart i et separat hashbundet arkiv og inkludert i antall forsøk/ukjent forbruk og kjøretid. Ingen vurdering kom tilbake fra dette forsøket. Eierens nye fortsett-instruks kom etter naturlig kvotefornyelse; kun det avviste inputet ble klargjort på nytt. Den frosne driverens v4-telling følger nåværende cache; v5 inkluderer også de arkiverte forsøkene.

Siste kvotesnapshot 2026-10-09T12:36:17.787634+00:00: femtimerskvote 40% brukt, ukeskvote 74% brukt. Kvoteavvisning under forsøket: ja. En naturlig fornyelse og ny eierinstruks tillot videreføring; ingen reset-kreditt ble brukt.

## Teknisk sluttkontroll

Offline integritetsaudit består: 700 case-resultater, 82 frosne filer og 309 uendrede A-artefakter. Kildeproveniens, faktisk kontekst/prompt, token-cache/budsjett, blindet input, resultatsegl/loggbruk, schema og kildebevis er kontrollert; rå og justerte aggregater er beregnet på nytt. Kun de godkjente eksakte adjudikasjonsbindingene gir justering. Alle tre indeksers vektorhashes og det arkiverte kvoteforsøket er verifisert. Ingen nye dommer-/tokenizerkall i audit. Dette bekrefter teknisk integritet, ikke uavhengig semantisk sikkerhetsvalidering. De tidligere 34 relevante scorer-/packing-/fortsettelsestestene bestod; ny audit-/rapportkode har også bestått Python-kompilering og kjøring mot de lagrede resultatene.

## Konklusjon og rangert beslutningsgrunnlag

**Fase B er ferdig: 25/25 konfigurasjoner, 625 vurderinger. Sammen med A er 28/31 ferdige. C er ikke kjørt.**
Den opprinnelige valgregelen stopper fordi ingen kandidat dominerer alle andre på hvert krav og hvert beskyttet sikkerhetsflagg.
Dette er et metodisk/scoringsmessig stopp, ikke en ny RAM-feil. Ingen prosentgrense eller regel ble endret etter resultatene.

**Min foreløpige anbefaling for de tre gjenværende packing-testene er MiniLM, k=16, ingen terskel.**
Det faktisk målte oppsettet bruker P2. Anbefalingen er et forsøksgrunnlag, ikke en produksjonsvinner eller en konklusjon om P1/P3.
K=12 gir samme kravdekning med litt mindre kontekst. K=16 gir den allerede planlagte P3-metoden anledning til å behandle nødpeilertreffet på rang 16;
k=12 tilbyr ikke dette treffet. Dette er en begrunnet testmulighet, **ingen garanti** for forbedring. Sikkerhetsavklaringen nedenfor må gjøres før C.

| Prioritet som forsøkskandidat | Målt oppsett | Krav / micro / macro | Komplette | Irrelevant / misvisende / konflikt / geo | Gj.snitt prompttokens |
|---|---|---|---|---|---:|
| 1, foreløpig | k16 / ingen / P2 | 58/72 / 80,56% / 79,09% | 15/22 | 22 / 1 / 0 / 0 | 1957,88 |
| 2 | k12 / ingen / P2 | 58/72 / 80,56% / 79,09% | 15/22 | 22 / 2 / 0 / 0 | 1900,12 |
| 3, kontrollreferanse | k8 / ingen / P2 | 57/72 / 79,17% / 77,95% | 15/22 | 22 / 1 / 0 / 0 | 1487,72 |

Dette er en kildebasert prioritering av aktuelle forsøk, ikke en automatisk rangering som skjuler sikkerhetstap.
K16s lavere misvisende-tall enn k12 dokumenterer ikke at teksten er tryggere i case 19.
Terskelvariantene gir lavere dekning. P70 ved k12/16 får 34/72 og 10/22 komplette, og mister 24 krav som k16/ingen dekker.
Null misvisende-flagg i disse variantene er ikke dokumentert risikofjerning, se case 13.

Mot den **justerte** MiniLM A-baselinen øker k12/16 uten terskel micro med 1,39 prosentpoeng og macro med 1,14 prosentpoeng;
antall komplette caser forblir 15. Den eneste kravgevinsten er **08/2**; ingen krav går tapt.
På den uendrede 15-slicen øker dekningen fra 39/51 til 40/51 (76,47% → 78,43%), macro fra 74,23% til 76,15%, med fortsatt 8/13 komplette.
Dette blandes ikke med 25-settet eller den eldre manuelle B8-vurderingen.

## Sikkerhetskontroll av de aktuelle kandidatene

**08/2 er en reell, kildebekreftet gevinst.** Den leverte voksenpassasjen `source-01-004`, blokk 9 i k12/16 uten terskel,
dekker voksen luftvei, se/lytte/føle etter pust og kontroll i inntil ti sekunder. Hele teksten leveres; kildebeviset og dommeren er enige.
08/1 har både 113-oppringning og veiledning fra faktisk levert kilde, ikke den deaktiverte tredje bevisruten.
08/3 har betinget sideleie ved normal pust. **08/4 mangler fortsatt**, og et delvis pustebevis gis ikke automatisk komplett pass.

**Case 13 har en uavklart negativ risikovurdering i P70.** K12/P70 og k16/P70 leverer identisk kontekst og bruker samme cachede dommersvar.
De beholder `source-01-027`, `source-04-009`, `source-03-008` og `source-08-010` som blokk 1/2/3/5, med de samme generelle 113-instruksjonene
som den tidligere kildegjennomgangen identifiserte som potensielt misvisende uten mobildekning. Ingen levert kvalifikasjon gjør telefonkontakten tilgjengelig,
og begge nødpeilerkrav mangler fortsatt. Det rå P70-svaret har likevel ingen misvisende-funn.
Jeg finner ikke en tekstlig begrunnelse for denne tilsynelatende sikkerhetsgevinsten. Dette må behandles som et uavklart risikofunn,
ikke som dokumentert eliminering av risiko eller direkte konflikt. Den godkjente adjudikasjonen for Gemma A har en annen eksakt inputbinding
og overføres derfor ikke automatisk. K16/ingen får fortsatt misvisende-flagg i case 13.

**Case 19 varierer uten en tilsvarende dokumentert risikoforskjell.** A/k8, k12 og k16 uten terskel har identisk `source-19-002` som blokk 3:
et generelt redningsråd fra isredning som ikke selv angir is-situasjonen. A/k8 og k16 merker dette irrelevant; k12 merker det også potensielt misvisende,
med risiko for å bruke feil redningsmetode i skredterreng. De første elleve blokkene er identiske mellom k12 og k16;
k16 legger bare til to legevaktpassasjer, `source-04-010` og `source-03-009`. De endrer ikke redningsrådets avgrensning.
Begge har allerede eksplisitt isinformasjon i blokk 8 og 9. Ingen direkte konflikt er påvist.
En konkret mulig feil bruk er beskrevet, men én vurdering per forskjellig helkontekst kan ikke skille dommervariasjon fra en konteksteffekt.
K16 kan derfor ikke erklæres tryggere enn k12 basert på dette flagget. Råresultatene beholdes; ingen ny adjudikasjon er aktivert.

Alle overvåkede positive krav i k8/k12/k16 er kontrollert mot faktisk levert tekst og kildebevis.
Case 20/1 er godkjent via eksakt A-input i k8; k12/16 leverer dessuten det eksplisitte rute-/ferdighetsgrunnlaget `source-10-002`.
Kunnskapshullene 14, 15 og 25 rapporteres separat og blir ikke automatisk fullstendig pass.

## Alle udekkede krav i k12/16 uten terskel

| Case / krav | Hva mangler fortsatt | Dokumentert begrensning |
|---|---|---|
| 01 / 1–3 | Bruddmistanke ved manglende belastning, brudd/forstuing-usikkerhet, lege/legevakt ved mistanke | `source-04-005` er på MiniLM-rang 20, uten avkorting; utenfor k≤16/P2. P1 kan nå naboseksjonen via rang 6 dersom budsjettet tillater det; ikke testet. |
| 03 / 3–5 | Korrekt fosskoking/tid/høyde og kjemikalie-/giftforbehold med alternativ vannkilde | `source-21-010` på rang 11 ville gitt 2062 tokens; `source-21-009` på rang 13 ville gitt 2086 i k16. Begge forkastes. Ingen forbedring fra k12 til k16. |
| 06 / 1,4 | 113 ved stor/ustoppelig blødning, varme/overvåking og varsling ved endring | Full støtte mangler også i A. Denne gjennomgangen fastslår ikke én bestemt rangerings-/avkortingsårsak. K16 gir ingen gevinst. |
| 08 / 4 | Vedvarende pustovervåking, HLR ved ingen/unormal pust, 113 ved usikkerhet | Nøkkelpassasje `source-07-005` ligger på rang 25. Den siste beslutningsdelen avkortes i begge embedding-visninger. De frosne grenreglene gir ingen dokumentert full rute; 08/2-gevinsten løser ikke 08/4. |
| 13 / 1–2 | Aktivere nødpeiler ved livsfare uten dekning; handle tidlig uten å la tvil forsinke | `source-11-003` ligger på rang 16, men ville gitt 2031 tokens og forkastes. P3 kan muligens frigjøre plass; dette er ikke målt. |
| 17 / 1–2 | Anafylaksimønster med hud/slimhinne/hals/pust og insektutløser; akutt eskalering/113 uten å vente | Symptompassasjen `source-08-004` har rang 34 og mister kritiske symptomer i begge embedding-visninger. Relevante akuttpassasjer ligger også utenfor topp 16. De planlagte justeringene har ikke løst dette. |
| 21 / 2 | Filtrer først, desinfiser etterpå **og følg produktinstruksen** | Rekkefølgen leveres allerede. Produktinstruksen fra `source-21-009`, rang 13, ville gitt 2073 tokens og forkastes. Ikke en påvist omvendt behandlingsrekkefølge. |

Dette er **14 udekkede krav**, inklusive flere akutte sikkerhetskrav. Ingen av kandidatene godkjennes som tilstrekkelig produksjonsdekning.
Avkorting er dokumentert, men dens kausale effekt på rangeringen er ikke bevist gjennom kontrafaktiske modellkjøringer.
Senere arbeid utenfor denne forsøksplanen må håndtere de utilgjengelige akuttpassasjene og bevare fullstendige handlingsforløp;
slikt arbeid er ikke startet. Flere kilder eller Qwen-svar er ikke brukt til å kompensere.

## Hva eieren må avklare for C

1. Det uavklarte risikofunnet i case 13/P70 må vurderes mot den allerede godkjente kildebaserte tolkningen, med nye eksakte kontekstbindinger dersom det adjudikeres.
2. Case 19 må få en konsistent, kildebegrunnet behandling av den samme generelle redningspassasjen. Ingen scorer endres før en separat beslutning.
3. Eieren må eksplisitt velge et **forsøksgrunnlag for C** eller godkjenne en avgrenset fravikelse fra dominansregelen med disse dokumenterte avveiningene.
   Min anbefaling er k16/ingen. Dette er forskjellig fra godkjenning av en produksjonskonfigurasjon.

De tre planlagte C-konfigurasjonene kan deretter bruke de samme frosne packing-reglene, indeksen og cachede inputene.
Fase A eller B trenger ikke gjentas. Det er ingen tillatelse til holdout, produksjonsendring eller nye parameterkombinasjoner.


Historisk B8: 34/51 og 7/13 komplette på den opprinnelige 15-slicen med manuelle vurderinger. Dette er ikke en kontrollert 25-sett-sammenligning. Forsøket er utviklings-/kalibreringsarbeid, ikke uavhengig sikkerhetsvalidering. Endelig eierbeslutning og eventuell senere kontrolltest gjenstår.

Råtekst, modeller, vektorer og logs er kun lokale og ignorerte. Ingen produksjonsvinner implementeres. M2-06 forblir åpen.
