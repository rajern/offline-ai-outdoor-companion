# M2-06 — gjenopptatt MiniLM-optimalisering

**Status: running-B. 8/31 konfigurasjoner fullstendig vurdert.**

## Metode og avgrensning

MiniLM er eierens valgte forsøksmodell. Fase A og B-k3-none gjenbrukes; ingen fullførte dommerkall gjentas. Alle caser bruker den samme frosne kildebasen, V3-prompten, schemaet, scoreren og Codex Sol Medium gjennom ChatGPT-abonnementet. Ingen betalt API, holdout, Qwen-svargenerering eller produksjonsendring.

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
| B-k5-none | not_run; 0/25 | — | — | — | — | — |
| B-k5-p10 | not_run; 0/25 | — | — | — | — | — |
| B-k5-p30 | not_run; 0/25 | — | — | — | — | — |
| B-k5-p50 | not_run; 0/25 | — | — | — | — | — |
| B-k5-p70 | not_run; 0/25 | — | — | — | — | — |
| B-k8-none | not_run; 0/25 | — | — | — | — | — |
| B-k8-p10 | not_run; 0/25 | — | — | — | — | — |
| B-k8-p30 | not_run; 0/25 | — | — | — | — | — |
| B-k8-p50 | not_run; 0/25 | — | — | — | — | — |
| B-k8-p70 | not_run; 0/25 | — | — | — | — | — |
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

B/C: 34 nye faktiske dommerkall, 91 cachetreff/unngåtte kall; tokens `{"input_tokens": 225934, "cached_input_tokens": 10368, "cache_write_input_tokens": 0, "output_tokens": 31513, "reasoning_output_tokens": 4967, "total_tokens": 257447}`.

Hele A+B/C: 109 kall, 109 vellykkede; tokens `{"input_tokens": 799888, "cached_input_tokens": 82944, "cache_write_input_tokens": 0, "output_tokens": 172490, "reasoning_output_tokens": 20769, "total_tokens": 972378}`; 0 med ukjent bruk; sum dommerkalletid 4947.66 s. Reasoning inngår i output, prefix-cached input i input; ingen dobbelttelling.

Før denne gjenopptakelsen: femtimerskvote 43% brukt, ukeskvote 59% brukt. Dette er kontoens delte bruk; eval-tokenregnskapet over er separat. Ingen automatisk API-fallback eller kvotereset.

## Sikkerhet og anbefaling

Ingen endelig konfigurasjon anbefales før fase B/C og kilde-/sikkerhetskontroll er ferdige. Case 01, 03/21, 08, 13, 17 og 20 overvåkes særlig. De kjente manglene i 08/4 og 17/1–2 må ikke antas løst av parameterendringer. Alle kildepassasjer og dommersvar bevares lokalt.

Historisk B8: 34/51 og 7/13 komplette på den opprinnelige 15-slicen med manuelle vurderinger. Dette er ikke en kontrollert 25-sett-sammenligning. Forsøket er utviklings-/kalibreringsarbeid, ikke uavhengig sikkerhetsvalidering. Endelig eierbeslutning og eventuell senere kontrolltest gjenstår.

Råtekst, modeller, vektorer og logs er kun lokale og ignorerte. Ingen produksjonsvinner implementeres. M2-06 forblir åpen.
