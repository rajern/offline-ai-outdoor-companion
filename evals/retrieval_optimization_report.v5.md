# M2-06 — gjenopptatt MiniLM-optimalisering

**Status: running-B. 18/31 konfigurasjoner fullstendig vurdert.**

Resultatsnapshot: 2026-10-09T08:30:52.415848+00:00. Eksport: 2026-10-09T08:50:03.490634+00:00.

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
| B-k12-none | not_run; 0/25 | — | — | — | — | — |
| B-k12-p10 | not_run; 0/25 | — | — | — | — | — |
| B-k12-p30 | not_run; 0/25 | — | — | — | — | — |
| B-k12-p50 | not_run; 0/25 | — | — | — | — | — |
| B-k12-p70 | not_run; 0/25 | — | — | — | — | — |
| B-k16-none | not_run; 0/25 | — | — | — | — | — |
| B-k16-p10 | not_run; 0/25 | — | — | — | — | — |
| B-k16-p30 | not_run; 0/25 | — | — | — | — | — |
| B-k16-p50 | not_run; 0/25 | — | — | — | — | — |
| B-k16-p70 | not_run; 0/25 | — | — | — | — | — |
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
| B-k12-none | 233.9 | 2782.5 | 103.72 | består |

B/C-worker-RSS gjelder gjenbrukt indeks og fjern dommervurdering, ikke hele mobilappen. MiniLM har 235,05 MB modell og 0,292 MB indeks (384 dimensjoner); A-indeksarbeidet toppet på omtrent 915 MB prosess-tre-RSS. Gemma har 1 488,92 MB modell / 0,584 MB indeks; Qwen Q4 396,47 MB / 0,778 MB. MiniLMs dokumentvektorer ble gjenbrukt i A, mens de andre bygget dokumentvektorer; A-indekstidene er derfor ikke en lik full-indeks-benchmark. MiniLMs kjente 128-token-avkorting (108/405 visninger, ingen spørsmål) er uendret. Mobil-RAM, energibruk og samlet lokal svartid er fortsatt ikke målt.

Spørsmålsvektorene er også lagrede. Ranking-/packing-tidene inkluderer derfor ikke embedding av et nytt brukerspørsmål. De er ikke full online retrieval-latens. Embeddingmålingene fra A og størrelses-/RAMdata rapporteres separat i resultat-JSON.


B/C: 69 nye faktiske dommerkall, 306 cachetreff/unngåtte kall; tokens `{"input_tokens": 475113, "cached_input_tokens": 69120, "cache_write_input_tokens": 0, "output_tokens": 80576, "reasoning_output_tokens": 12356, "total_tokens": 555689}`.

Hele A+B/C: 144 kall, 144 vellykkede; tokens `{"input_tokens": 1049067, "cached_input_tokens": 141696, "cache_write_input_tokens": 0, "output_tokens": 221553, "reasoning_output_tokens": 28158, "total_tokens": 1270620}`; 0 med ukjent bruk; sum dommerkalletid 6488.41 s. Reasoning inngår i output, prefix-cached input i input; ingen dobbelttelling.

Før denne gjenopptakelsen: femtimerskvote 43% brukt, ukeskvote 59% brukt. Dette er kontoens delte bruk; eval-tokenregnskapet over er separat. Ingen automatisk API-fallback eller kvotereset.

## Sikkerhet og anbefaling

Ingen endelig konfigurasjon anbefales før fase B/C og kilde-/sikkerhetskontroll er ferdige. Case 01, 03/21, 08, 13, 17 og 20 overvåkes særlig. De kjente manglene i 08/4 og 17/1–2 må ikke antas løst av parameterendringer. Alle kildepassasjer og dommersvar bevares lokalt.

Historisk B8: 34/51 og 7/13 komplette på den opprinnelige 15-slicen med manuelle vurderinger. Dette er ikke en kontrollert 25-sett-sammenligning. Forsøket er utviklings-/kalibreringsarbeid, ikke uavhengig sikkerhetsvalidering. Endelig eierbeslutning og eventuell senere kontrolltest gjenstår.

Råtekst, modeller, vektorer og logs er kun lokale og ignorerte. Ingen produksjonsvinner implementeres. M2-06 forblir åpen.
