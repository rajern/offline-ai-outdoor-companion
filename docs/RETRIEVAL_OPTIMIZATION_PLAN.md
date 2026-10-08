# Outwise — Retrieval Optimization Plan

**Eieroppdatering, 2026-10-08:** Oppdraget i chatten godkjenner eksisterende
25 utviklingscaser og betinget kjøring av planen etter scorer-/runtimekontroll.
Den eldre status-/godkjenningsporten nedenfor beskriver overleveringen før denne
instruksjonen. Scorerregresjonen består. Etterfølgende avgrenset diagnostikk
rettet Qwen Q4s reproducerbarhet med eksplisitt CPU-isolasjon; se
[`stabilitetsrapporten`](../evals/qwen_embedding_stability_report.v1.md).
Eieren har deretter godkjent gjenopptakelse av A/B/C etter tekniske kontroller,
uten mellomgodkjenninger. Orkestreringen er implementert og teknisk testet;
minnekontrollen stoppet allerede ved MiniLM (244,6 MiB ledig, krav 256 MiB).
Full faktisk gjennomføring er dermed uverifisert. Ingen av de 31 konfigurasjonene
var ferdige ved denne minnestoppen. Etter at eieren frigjorde RAM, bestod alle tre
sekvensielle modell-/input-/ressurskontroller med uendrede grenser. 25 MiniLM-kontekster
er lagret. En énlinjes rettelse sammenligner kilder gjennom datamodellens samme
standardfelter; den opprinnelige frysen og alle resultathasher er bevart i et
separat [rettelseslag](../evals/retrieval_optimization_serialization_correction.v1.json).
Scoring, gold og modellinnstillinger er uendret; ingen dommerkall var gjort før
rettelsen. Kjøringen er gjenopptatt fra lagrede kontekster. Se
[ny rapport](../evals/retrieval_optimization_report.v2.md) og den tidligere
[`evals/retrieval_optimization_report.v1.md`](../evals/retrieval_optimization_report.v1.md).
Holdout, produksjonsendring og svargenerering er fortsatt utelukket.

**Status:** Testdesignet er avtalt; **ikke autorisasjon til å starte optimalisering**. Først må eier godkjenne evalueringsgrunnlaget og en tilstrekkelig pålitelig, fullstendig scorer.  
**Overlevering:** 8. oktober 2026. **Repo:** [`rajern/offline-ai-outdoor-companion`](https://github.com/rajern/offline-ai-outdoor-companion). Referansecommit: [`c4326d0`](https://github.com/rajern/offline-ai-outdoor-companion/commit/c4326d034fccc77cc1223911eb6b5c1230df0bcc). Kontroller senere endringer før kjøring.

## 1. Mål og avgrensning

Optimaliser hvilke **faktiske kildepassasjer som leveres til den lokale Qwen-modellen**, ikke selve svarformuleringen. Vi vil øke dekningen av nødvendige instrukser og komplette caser, og redusere irrelevant eller misvisende kontekst, uten uforholdsmessig bruk av tokens, CPU, RAM eller lagring på fremtidig mobil.

Dette er en **retrieval-only** sammenligning. Ikke kjør generering, ny kunnskapsinnhenting, kildeendringer, en ny genereringsmodell eller reranker i denne runden. Ingen produksjonsendringer uten senere godkjenning.

## 2. Datagrunnlag og obligatoriske grenser

- Utvikling: `evals/retrieval_development.v2.yaml`, **25 spørsmål: 22 dekkede + 3 forhåndsdefinerte kunnskapshull**. Første 15 er uendret fra `retrieval_cases.v1.yaml`.
- Holdout: `evals/holdout/retrieval_control.v1.yaml`, **10 spørsmål: 9 dekkede + 1 kunnskapshull**. **Ikke åpne, lese, evaluere, kalibrere mot eller bruke kontrollfasiten under optimalisering eller feilsøking.** For en sterkere barriere bør optimaliseringsagenten arbeide i en checkout der holdout-katalogen er fysisk utelatt, ikke bare være avhengig av instruks.
- Kunnskapsbase: **22 godkjente dokumenter / 190 opprinnelige parent-passasjer**, frosset kildegrunnlag. Ingen gjendistribusjon av lokal råtekst eller modellfiler.
- Les `evals/FOUNDATION.md`, `evals/retrieval_judge_rubric.v1.md`, `evals/retrieval_protocol.v1.yaml`, `AGENTS.md` og relevante `docs/*`. Bruk låste hashes, kildeversjoner og kontekstartifakter.
- Evaluer **kun det som faktisk ble levert i den serialiserte konteksten**. Ikke gi poeng fordi fakta finnes et sted i databasen, ble hentet som kandidat eller ble kastet ut av packeren.
- Frys godkjente fasitkrav, scoringregler, corpus og evalueringslogikk før første konfigurasjonstest. Ukjente/omstridte vurderinger må avgjøres eller blokkere valg av vinner; de skal ikke stilletiende bli null.

**Godkjenningsport:** Per `FOUNDATION.md` er både nye gold-caser og scorer foreløpig «pending owner approval». En fremtidig chat må ikke tolke dette dokumentet som godkjenning.

## 3. Avtalte variabler og antall tester

| Trinn | Variabel | Forhåndsbestemte alternativer | Antall konfigurasjoner |
|---|---|---|---:|
| 2 | Embeddingmodell | Eksisterende `paraphrase-multilingual-MiniLM-L12-v2`; Google **EmbeddingGemma 2** (nøyaktig modell-ID/runtime må verifiseres); **Qwen3-Embedding-0.6B Q4** (konkret GGUF/kvantisering må verifiseres) | 3 |
| 3 | `top_k` | **3, 5, 8, 12, 16** | 5 |
| 3 | Likhetsterskel | **Ingen terskel**, eller per-modellkalibrerte **p10, p30, p50, p70** | 5 |
| 4 | Context-packing | **P1: smal seksjonsutvidelse**, **P2: parent-only**, **P3: selektiv budsjettbevisst/instruksjonsbevarende packing** | 3 |

**Totalt avtalt forsøksbudsjett:** `3 + (5 × 5) + 3 = 31` konfigurasjoner. Med 25 utviklingsspørsmål blir det **775 konfigurasjon–spørsmål-vurderinger** (ikke nødvendigvis 775 separate embeddingkjøringer). Vi gjennomfører **ikke** full `3 × 5 × 5 × 3 = 225` grid search nå.

5–10 ekstra *målrettede* tester ble nevnt som en mulig senere opsjon, men **ikke automatisk fullmakt**: be eier om godkjenning og begrunn hypotesen før slike tester. Ikke utvid søket for å jage små tilfeldige gevinster.

### Trinn 2 — valg av embeddingmodell (3 tester)

Sammenlign de tre modellene på **samme 25 spørsmål, samme kildemateriale, samme kandidat- og pakkeprinsipp, og samme tokenbudsjett**. Et praktisk standardoppsett for en mest mulig isolert modelltest er `top_k=8` **unike parent-passasjer**, **ingen threshold** og **P2 parent-only**; dette er et **implementeringsforslag som må dokumenteres og fryses før kjøring**, ikke en tidligere særskilt godkjent parameterbeslutning.

- Kontroller at eksakt modell faktisk eksisterer, har akseptabel lisens og lokal runtime, og oppgi nøyaktig modell/revisjon, kvantisering og preprocessing. Ingen stille erstatning med «nærmeste» modell.
- Respekter modellspesifikk `query`/`passage`-formatering og tokenbegrensninger; mål faktisk truncation. Norsk spørsmål mot delvis engelske kilder er sentralt.
- Ikke gjenbruk gammel cosine-threshold `0.35` på tvers av ulike embeddingmodeller.
- Sammenlign kvalitetsmål **og** disk/RAM, CPU-tid og praktisk lokal drift. Hvis resultatene er svært like, prioriter den enklere/rimeligere løsningen. Be eier vurdere store avveininger.

### Trinn 3 — `top_k × threshold` (25 tester)

Bruk **én valgt embeddingmodell** fra trinn 2; kjør de 25 forhåndsbestemte kombinasjonene. `top_k` teller **unike opprinnelige parent-passasjer**, ikke rå overlappende child-treff. De fire terskelkandidatene beregnes **for den valgte modellen**, ut fra scorefordelingen for de **16 høyest rangerte unike kandidatene på utviklingsspørsmålene**. Dokumenter presist hvordan persentilene aggregeres og hvordan grenseverdiene håndteres; frys dette før grid-kjøringen. Behold «ingen terskel» som reell baseline. Ikke bruk holdout til threshold-kalibrering.

Bruk samme faste packing-strategi i alle 25 tester (foreslått **P2 parent-only**) for å isolere effekten av `k` og terskel. En terskel som kaster ut eneste relevante passasje skal registreres som feil, også om likhetsscoren er lav.

### Trinn 4 — context-packing (3 tester)

Bruk **valgt embeddingmodell, `k` og threshold** med identisk rangert kandidatgrunnlag. Sammenlign:

- **P1 — smal seksjonsutvidelse:** start fra treff og hent nærliggende passasjer fra relevant gren/seksjon etter eksisterende generiske seksjonsregler; bevar full pakke innen budsjett. Dette tilsvarer tidligere eksperimentell «narrow section expansion», ikke nødvendigvis historisk konfigurasjon «A».
- **P2 — parent-only:** lever bare de relevante, opprinnelige parent-passasjene, deduplisert; ingen automatisk ekstra seksjonstekst.
- **P3 — selektiv, budsjettbevisst og instruksjonsbevarende:** prioriter retrieval-relevans; nedprioriter duplisert informasjon; bruk faktisk tokenkostnad; hent bare nødvendig nabokontekst når kilde-/seksjonsstrukturen viser en sammenhengende prosedyre, tilhørende vilkår eller advarsler. Bevar meningsbærende instruksjonssekvenser når det er mulig. **Ingen ekstra LLM, omskriving eller gold-aware packer.** Implementer **én enkel deterministisk algoritme**, med regler/vekter definert og frosset før P3 sammenlignes; ikke optimaliser P3 internt mot de 25 casene.

**Navnekollisjon:** Repoets historiske «A»/«B» i `retrieval_protocol.v1.yaml` betyr henholdsvis produksjons-top3 og seksjonsutvidelse. Bruk derfor **P1/P2/P3** for denne nye runden og eksplisitt mapping til kode.

## 4. Felles budsjett, scoring og sammenligning

- **2 000 tokens for komplett, uendret grounded prompt**, inkludert spørsmål, instruks og kunnskapsutdrag; behold avgrensningen fra protokollen (ekskludert eventuell chat-template-overhead dersom dette fortsatt er den faktiske eval-kontrakten). Måles med låst, faktisk tokenizer — ikke tegnestimat.
- Loggfør reelle kildepassasjer, rangering, score, ekskluderte pakker, faktisk levert kontekst, prompt-tokens, modell/index-versjon, hash og tidsbruk. Caching av embeddings og kandidatlisten er ønskelig. Nye eksperimenter skal ikke overskrive gamle artefakter.
- Primære mål: **micro must-have-information coverage**, gjennomsnittlig per-case-dekning (**macro**) og antall **komplette dekkede caser**. Delkrav er binære: alle betingelser, enheter og viktige forbehold må være til stede.
- Sikkerhets-/kvalitetsmål separat: **irrelevant innhold**, **potensielt misvisende/konfliktende innhold**, **feil geografisk/juridisk anvendelse**. Sammenlign også antall passasjer, tokenbruk, forkastede pakker, latenstid, størrelse/RAM og truncation.
- **Kunnskapshull** teller ikke som ordinære retrieval-feil eller automatisk full treff; rapporter eventuelle støttede delkrav for seg.
- Rapporter hele **25-settet** og det **uendrede 15-spørsmålsutdraget separat**. Historisk B8: **34/51 must-have = 66,7 %**, **7/13 komplette**, men disse tallene er for det gamle 15-settet — ikke sammenlign direkte med 25-aggregatet.
- Scoringen skal være validert for både positive, negative og usikre tilfeller, støy og geografi før autonom kjøring. Oppgi usikkerhet, manuelle kontroller, casevise endringer og sikkerhetskritiske regresjoner. Ingen fast «90 %-regel» eller automatisk vinnervalg ved svært små forskjeller.

## 5. Gjennomføring, stoppkriterier og resultat

1. **Stopp nå** til eier har godkjent utviklings-gold og komplett scoringopplegg. Ikke åpne holdout.
2. Frys evaluering, standardinnstillinger og artefaktversjoner; verifiser modellstøtte og en tids-/minnetest før hele kjøringen.
3. Kjør **trinn 2 → trinn 3 → trinn 4**, med caching og reproduksjon, ingen produksjonsendringer.
4. Stopp ved teknisk inkonsistens, misvisende scorer, feil kildeproveniens, falske sikkerhetskritiske positive eller budsjettbrudd; be om eierbeslutning. Stopp senest ved 31 konfigurasjoner.
5. Sluttrapport: rangert oversikt per trinn, alle mål, per-case feil/forbedringer, ressurser og tradeoffs, anbefalt konfigurasjon og hva som eventuelt gjenstår (f.eks. behov for lokal reranker). Ikke gi eier en «winner» uten å synliggjøre regresjoner.
6. **Eier velger og fryser** løsning. Kun deretter kan eier gi separat **engangsgodkjenning** for kontrollsettet. Ingen videre tuning mot disse 10 kontrollspørsmålene.

## 6. Kort oppstartstekst til en ny chat (når scoringen er godkjent)

> Vi fortsetter Outwise M2-06. Les vedlagte `RETRIEVAL_OPTIMIZATION_PLAN.md`, repoets `evals/FOUNDATION.md`, relevante eval-filer og `AGENTS.md`. Behandle 31-tester-oppsettet som besluttet; ikke gjenåpne variablene uten konkret blocker. Kontroller at eier har godkjent gold, autonom scorer og adgangsgrenser. Hjelp meg deretter å skrive **én presis Codex-implementeringsprompt** for trinn 2–4, med artefakter, målinger, stoppregler og rapportformat. Ikke start holdout, produksjonsendringer eller generering. Marker eventuelle gjenværende konkrete implementeringsdetaljer som trenger min godkjenning.
