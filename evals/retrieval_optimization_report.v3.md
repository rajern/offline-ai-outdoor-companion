# M2-06 — fase A og kontrollert stopp før fase B

**Status: 3 av 31 konfigurasjoner fullført. Alle 75 utviklingsvurderinger er komplette. Fase B og C er ikke kjørt.**

RAM-problemet er løst: alle tre sekvensielle modell-, input- og ressurskontroller bestod med de opprinnelige grensene. Kjøringen stoppet deretter ved den frosne regelen for modellvalg: ingen kandidat kan beholde alle krav som andre kandidater dekker og samtidig unngå nye sikkerhetsflagg. Ingen prosentbasert akseptgrense er innført.

## Resultater og rangering

Alle A-konfigurasjoner bruker `top_k=8`, ingen threshold, P2 parent-only, samme frosne 22 dokumenter / 190 passasjer og samme 25 spørsmål. Bare levert kontekst scores. Dommer: `gpt-6.1-sol`, Codex CLI, Medium, ChatGPT-abonnement. Prompt V3, schema V2 og adjudikasjon V1 er uendret.

| Kvalitetsrang | Modell | Micro25 | Macro25 | Komplette støttede caser | Irrelevant / misvisende / konflikt / geo |
|---:|---|---:|---:|---:|---|
| 1 | minilm | 56/72 = 77.8% | 75.7% | 14/22 | 22 / 1 / 0 / 0 |
| 2 | gemma2 | 51/72 = 70.8% | 74.1% | 13/22 | 22 / 0 / 0 / 0 |
| 3 | qwen3-q4 | 37/72 = 51.4% | 54.9% | 10/22 | 21 / 0 / 0 / 0 |

Codex preflight verifiserer ChatGPT-login, katalogmodell `gpt-6.1-sol` og Medium-støtte; CLI-versjonen er `0.162.0-alpha.2`. Eksakt backend/server-revisjon eksponeres ikke i JSONL. Identiteten er derfor låst til verifisert requested/catalog-modell og CLI/runtime; denne begrensningen beholdes fra den godkjente dommerpiloten.

Flaggantallene gjelder støttede caser med minst ett funn, ikke andel irrelevante tokens eller en uttømmende fasit for støy. LLM-review, uncertain og kildebevis/dommer-uenighet er 0 i alle tre konfigurasjoner. Separat kildekontroll gir et menneskelig review-behov i case 13; dette er ikke skrevet inn som en endring av de opprinnelige dommerscorene.

| Opprinnelig 15-sett | Micro15 | Macro15 | Komplette støttede caser |
|---|---:|---:|---:|
| minilm | 39/51 = 76.5% | 74.2% | 8/13 |
| gemma2 | 34/51 = 66.7% | 69.0% | 7/13 |
| qwen3-q4 | 20/51 = 39.2% | 36.5% | 3/13 |

De tre kunnskapshullene rapporteres separat: case 14 har 1/2 støttede delkrav i hver konfigurasjon, mens case 15 og 25 har tom kravliste. Ingen av disse får komplett pass. Historisk B8 var 34/51 og 7/13 på 15-settet med eldre manuell scoring. Det er ikke en kontrollert før/etter-sammenligning med dagens V3 og packing; 25-settet blandes heller ikke med 15-settet.

## Hvorfor neste fase er blokkert

| Kandidat mot annen modell | Vunne krav | Tapte krav | Nye misvisende/konflikt/geo-flagg |
|---|---:|---:|---:|
| minilm mot gemma2 | 16 | 11 | 1 |
| minilm mot qwen3-q4 | 23 | 4 | 1 |
| gemma2 mot minilm | 11 | 16 | 0 |
| gemma2 mot qwen3-q4 | 20 | 6 | 0 |
| qwen3-q4 mot minilm | 4 | 23 | 0 |
| qwen3-q4 mot gemma2 | 6 | 20 | 0 |

MiniLM vinner 16 krav mot Gemma, blant annet hele tordenværscasen 05 og orienteringsscasen 04. Samtidig taper den 11 krav, blant annet bruddmistanke/legevurdering (01), koketid/kjemisk forurensning (03), luftvei og pustovervåking (08), anafylaksisymptomer (17) og rekkefølge for vannbehandling (21). Mot Qwen taper MiniLM fire krav i 08, 20 og 21. Fullstendige item-lister står i [maskinlesbar sammenligning](retrieval_optimization_comparison.v1.json). En netto micro-forbedring på 5 krav mot Gemma skjuler derfor vesentlige bytter av sikkerhetsinformasjon.

Alle modellene mangler begge nødpeilerkravene i case 13. MiniLM og Gemma deler seks identiske leverte passasjer, hvorav fem omtaler 113, men bare MiniLM får potensielt-misvisende-flagg. Full kontekst og rekkefølge er forskjellige. Dette viser et konkret review-behov for klassifiseringsgrensen; det beviser ikke alene at én bestemt dommervurdering er feil. Råresultatene er bevart, uten ny fasit, omkjøring eller ad hoc-overstyring.

Fem krav er udekket i alle tre konfigurasjoner: case 06 item 1 og 4, case 13 item 1 og 2, og case 17 item 2. Dette er retrieval-mangler i støttede caser, ikke nye eller omdefinerte kunnskapshull. De må følges særskilt i eventuell videre fase B/C.

## Scorer, rettelse og kildekontroller

- De tidligere godkjente 05/08/09-reglene og V3-kalibreringen er beholdt. 22 forseglede kalibreringsrader ble gjenbrukt uten nye dommerkall; de historiske 19 unike kalibreringskallene og 140 133 tokens inngår ikke i de 75 nye retrieval-kallene nedenfor.
- Case 05: MiniLMs nye overhengsvurdering har eksplisitt levert kildebevis. Det tidligere godkjente prinsippet om tydelig semantisk implikasjon er fortsatt tillatt; Gemma og Qwen mangler faktisk kildegrunnlag i denne konfigurasjonen.
- Case 08: MiniLM/Gemma har kildebevis for både oppringning og veiledning. Qwens oppringning/lyttebevis gir ikke fullt pass når veiledningen mangler. Den utilstrekkelige tredje bevisruten er fortsatt deaktivert; gamle referanser er uendret.
- Case 09: separat gjennomlesning bekrefter at alle tre vurderingene identifiserer institusjonell omsorg/evakuering som irrelevant. Tydelig avgrenset kulderåd er ikke automatisk merket misvisende.
- En operativ énlinjes rettelse sammenligner kildeposter gjennom samme `KnowledgeItem`-standardfelter som retrieval. Manglende `published_at` og standardverdien `null` utløste tidligere et falskt proveniensavvik. Tekst, URL, ID, metadata og endret dato blir fortsatt avvist.
- Rettelsen kom etter kontekstpakking, før første dommerkall. Opprinnelig frysemanifest og teknisk preflight er arkivert separat; alle 980 eksisterende resultatfiler beholdt hashene sine. Ingen gold-, judge-, modell-, token-, packing- eller minneinnstilling ble endret. Se [rettelsesrevisjon](retrieval_optimization_serialization_correction.v1.json).
- 13 orkestrasjonstester bestod etter rettelsen, inkludert standardfelter og avvisning av endret kildeinnhold. Den tidligere 43-testkontrollen er historisk; ingen ny generell dommertestkampanje ble kjørt.
- Sluttkontroll av 75 kontekster og forseglede dommerresultater bekrefter kilde-/prompt-/modellhashes, token-cache, scorer, aggregater og vektorformat, med 0 nye dommerkall. Dette er integritetskontroll, ikke uavhengig semantisk eller klinisk validering. Se [audit](retrieval_optimization_integrity_audit.v1.json).

## Ressurser og lokal egnethet

| Modell | Modellvekter MB | Dokumentvektorer MB / dimensjon | Indekskjøring s / CPU-s | Samtidig RSS GB | Snitt prompttokens / maks | Budsjettforkastede pakker |
|---|---:|---|---|---:|---|---:|
| minilm | 235.1 | 0.292 / 384 | 5.84 / 7.62 | 0.915 | 1487.7 / 1983 | 2 |
| gemma2 | 1488.9 | 0.584 / 768 | 70.11 / 220.94 | 2.017 | 1670.8 / 2000 | 7 |
| qwen3-q4 | 396.5 | 0.778 / 1024 | 130.95 / 510.86 | 1.778 | 1669.6 / 1989 | 9 |

MiniLM gjenbruker alle 190 dokumentvektorer og beregner bare nye spørsmålsvektorer; tiden er ikke en full indeksbyggingsbenchmark. Gemma og Qwen beregner 190 dokumenter og 25 spørsmål. Tidene inkluderer modelloppstart og inputkontroll. Alle kjører på CPU med fire embeddingtråder; Gemma bruker float32, Qwen Q4_K_M og eksplisitt device/operation/KV-offload av, context 2048, batch/ubatch 1024. Modellidentitetene, revisjoner, Apache-2.0-lisensene, filhashene og runtimeversjonene står i [råmålinger uten kildetekst](retrieval_optimization_results.v2.json).

Grensene er uendret: 256 MiB tilgjengelig RAM i reserve og 4 GiB prosess-tre-RSS, med sampling hvert 100 ms. Både preflight og de fulle indekstrinnene består. MiniLM avkorter 108 av 405 kontrollerte embedding-inputs (to dokumentvisninger + 25 spørsmål), fjerner 8 340 tokens og bruker maks 128. Ingen spørsmål avkortes. Gemma/Qwen avkorter 0 av 215 inputs, med maks henholdsvis 419/431. Avkortingen påvirker rangeringen; leverte kildepassasjer er hele.

| Modell | Snitt konteksttokens | Leveringspassasjer per case | Rangering 25 spørsmål, sekunder | Packing/token-audit 25 spørsmål, sekunder |
|---|---:|---|---:|---:|
| minilm | 1296.3 | 7–8 | 0.0220 | 160.06 |
| gemma2 | 1479.3 | 6–8 | 0.0099 | 131.26 |
| qwen3-q4 | 1478.2 | 6–8 | 0.0112 | 140.59 |

Rangeringstiden bruker cachede spørsmålsvektorer og er ikke live latens inkludert query-embedding. Packingtid inkluderer det låste tokeniseringsprogrammets prosessoppstart og cachearbeid. Ingen mobilmaskin eller samtidig drift med Qwen-svargenerering er målt. Ressursrang for modelllagring og observert RSS er MiniLM → Qwen → Gemma; dette er Windows-målinger, ikke dokumentert mobilkapasitet. Kvalitetsrangeringen gjelder den frosne k8/P2-baselinen, ikke modellfamilienes beste mulige oppsett.

## Codex-forbruk og gjenopptakelse

75 nye dommerkall, 75 vellykkede, 0 feil og 0 ukjent tokenforbruk. 573,954 inputtokens + 140,977 outputtokens = **714,931 totalt**. Reasoning: 15,802 tokens, inkludert i output. Prefix-cache: 72,576, inkludert i input. Disse delmengdene skal ikke summeres en gang til.

Sum dommerkalltid: 3921.55 sekunder (65.4 minutter). Eksperimentvindu fra lagret start til stopp: 81.3 minutter, inkludert rettelsespausen og tekniske kontroller. Eksakt evalueringscache: 0 treff i de nye 75 inputene; de gjenopptatte indeksene/kontekstene og ferdige scores ble beholdt. De 22 kalibrerings- og 75 sluttkontroll-cachelesingene ga ingen ny inferens og telles ikke som nye evalueringskall.

ChatGPT-abonnement, ingen betalte OpenAI API-kall og ingen beregnet API-kostnad. Ingen kvotebegrensning oppstod. Delt kontosnapshot etter A: 58 % brukt i femtimersvinduet og 51 % i ukesvinduet; dette er ikke forsøksforbruk alene.

Råresultater, kildepassasjer, modeller, vektorer, token-cache, arbeidslogger, frysehistorikk og review-notater ligger ignorert under `knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/`. Dommercachen er separat under `knowledge/local/judge-cache-v3/`. Nye resultatkall kan ikke gjentas automatisk ved feil, og ingen API-fallback er tillatt.

## Alle 31 planlagte konfigurasjoner

| Konfigurasjon | Modell | k | Threshold | Packing | Status |
|---|---|---:|---|---|---|
| A-minilm | minilm | 8 | ingen | P2 | fullført 25/25 |
| A-gemma2 | gemma2 | 8 | ingen | P2 | fullført 25/25 |
| A-qwen3-q4 | qwen3-q4 | 8 | ingen | P2 | fullført 25/25 |
| B-k3-none | ikke valgt | 3 | ingen | P2 | ikke kjørt — fase A-port |
| B-k3-p10 | ikke valgt | 3 | p10 | P2 | ikke kjørt — fase A-port |
| B-k3-p30 | ikke valgt | 3 | p30 | P2 | ikke kjørt — fase A-port |
| B-k3-p50 | ikke valgt | 3 | p50 | P2 | ikke kjørt — fase A-port |
| B-k3-p70 | ikke valgt | 3 | p70 | P2 | ikke kjørt — fase A-port |
| B-k5-none | ikke valgt | 5 | ingen | P2 | ikke kjørt — fase A-port |
| B-k5-p10 | ikke valgt | 5 | p10 | P2 | ikke kjørt — fase A-port |
| B-k5-p30 | ikke valgt | 5 | p30 | P2 | ikke kjørt — fase A-port |
| B-k5-p50 | ikke valgt | 5 | p50 | P2 | ikke kjørt — fase A-port |
| B-k5-p70 | ikke valgt | 5 | p70 | P2 | ikke kjørt — fase A-port |
| B-k8-none | ikke valgt | 8 | ingen | P2 | ikke kjørt — fase A-port |
| B-k8-p10 | ikke valgt | 8 | p10 | P2 | ikke kjørt — fase A-port |
| B-k8-p30 | ikke valgt | 8 | p30 | P2 | ikke kjørt — fase A-port |
| B-k8-p50 | ikke valgt | 8 | p50 | P2 | ikke kjørt — fase A-port |
| B-k8-p70 | ikke valgt | 8 | p70 | P2 | ikke kjørt — fase A-port |
| B-k12-none | ikke valgt | 12 | ingen | P2 | ikke kjørt — fase A-port |
| B-k12-p10 | ikke valgt | 12 | p10 | P2 | ikke kjørt — fase A-port |
| B-k12-p30 | ikke valgt | 12 | p30 | P2 | ikke kjørt — fase A-port |
| B-k12-p50 | ikke valgt | 12 | p50 | P2 | ikke kjørt — fase A-port |
| B-k12-p70 | ikke valgt | 12 | p70 | P2 | ikke kjørt — fase A-port |
| B-k16-none | ikke valgt | 16 | ingen | P2 | ikke kjørt — fase A-port |
| B-k16-p10 | ikke valgt | 16 | p10 | P2 | ikke kjørt — fase A-port |
| B-k16-p30 | ikke valgt | 16 | p30 | P2 | ikke kjørt — fase A-port |
| B-k16-p50 | ikke valgt | 16 | p50 | P2 | ikke kjørt — fase A-port |
| B-k16-p70 | ikke valgt | 16 | p70 | P2 | ikke kjørt — fase A-port |
| C-P1 | ikke valgt | ikke valgt | ikke valgt | P1 | ikke kjørt — fase A-port |
| C-P2 | ikke valgt | ikke valgt | ikke valgt | P2 | ikke kjørt — fase A-port |
| C-P3 | ikke valgt | ikke valgt | ikke valgt | P3 | ikke kjørt — fase A-port |

Ingen modell er valgt til B, så numeriske percentilterskler er ikke beregnet eller kalibrert. De 25 B- og tre C-konfigurasjonene er fortsatt planlagt, ikke testresultater. Ingen ekstra kombinasjon, full grid search eller automatisk gjenstart er utført.

## Anbefaling og neste beslutning

**MiniLM er første kandidat til videre fase B-review**, fordi den har best samlet dekning og enklest/lavest lokal ressursfotavtrykk. Dette er en betinget kandidatvurdering, ikke en valgt modell eller ferdig retrieval-konfigurasjon. Gemmas gevinster på andre sikkerhetskrav og case 13-review gjør at valgregelen ikke tillater automatisk videreføring. Qwen Q4 er teknisk stabil, men har klart svakere dekning i dette oppsettet og gir ikke grunnlag for å foretrekkes på totalscore.

Eieren må gjennomgå item-tapene, avklare klassifiseringsgrensen i case 13 og velge en foreløpig embeddingmodell før de resterende 28 konfigurasjonene kan kjøres. Gjeldende gold, dommer og råresultater skal beholdes; en endring eller adjudikasjon må dokumenteres eksplisitt, ikke skjules som retry. Ingen endelig vinner, produksjonskonfigurasjon, holdout-kjøring, ny kunnskapskilde eller Qwen-svargenerering er implementert. M2-06 er fortsatt åpen.
