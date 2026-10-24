# M2-06: avgrenset lokal modell-/genereringssammenligning

**Ferdig 2026-10-24:** 22 nye svar, 11 fra Qwen 2B og 11 fra Gemma E2B.
Gemma følger kildene bedre, blander færre situasjoner og avstår i begge testede
kunnskapshull. Ingen kandidat består den frosne grensen mot kritiske utelatelser.
Finalistfasen kjøres derfor ikke. Ingen ny modell-/promptrunde startes.
Anbefal et snevrere generativt ansvar i første prototype, med situasjonstilpassede
kildeprosedyrer for kritiske tilfeller. M2-06 er fortsatt åpen for eierbeslutning
og produktgjennomgang; ingen produksjonsendring eller M3 er gjennomført.

## Kandidater, metode og forsøksgrunnlag

| Kandidat | Faktisk utført | Modellfil | Resultat |
|---|---|---:|---|
| Qwen3.5-2B Q4_K_M | 8 primære +3 tilstrekkelig-kontekst | 1,40 GB | Tekniske grenser består; kvalitetsport består ikke |
| Qwen3.5-4B Q4_K_M | Lasting/preflight, ingen svar | 3,01 GB | Prosessgruppe-RSS 4,34 GiB >4 GiB, utelatt etter protokollen |
| Gemma 4 E2B-it offisiell QAT Q4_0 | 8 primære +3 tilstrekkelig-kontekst | 3,35 GB | Tekniske grenser består; kvalitetsport består ikke |

4B-utlatelsen gjelder denne eksakte filen, CPU-runtime og resident MiniLM.
Siste forsøk hadde vertsreserve intakt, men RSS 4 658 118 656 bytes. Det er
ressursbeviset protokollen tillater utelukkelse på, i motsetning til de tidligere
vertsminnestoppene. Ingen kvalitetskonklusjon trekkes om 4B. Modellvarianter,
kvantisering og ressursgrenser ble ikke byttet for å få et resultat.

Alle 36 inputdefinisjoner fra 11. oktober er bevart: 25 utviklingsspørsmål,
tre eksisterende kildekontroller, fire omformuleringer og fire gjentakelser.
Bare de avtalte åtte primære og tre kontrollene per kjørbare modell ble brukt.
Samme spørsmål, faktiske T-ranking/P3-kildetekst og passasjerekkefølge. Ingen
retrieval, ekstra passasje, ompakking eller gold-endring. De 72 modellspesifikke
native inputene (36 per modell) ble kontrollert før første svar.

Frosne innstillinger: system-/brukerrolle i native template, reasoning off,
temperatur 0,2, top-p 0,8, top-k 20, seed 42, maks 512 svartokens, én lokal
server-slot på 4 096. Faktisk input inklusive BOS/template/kontrolltokens er
777–2 233 for 2B og 768–2 246 for Gemma, under 3 200. Eksakte verifiserte
token-IDer ble sendt direkte til runtime og samsvarer med `tokens_evaluated`.
Ingen kontekst ble avkortet. Native systemtekst/brukertekst og ikke-tenkende
assistant-prefiks er kontrollert; Gemma-input har én BOS.

## Primær screening: samme åtte caser, seks støttede / 19 krav

Dette er et målrettet utviklingsutvalg med kjente problemer, ikke et tilfeldig
eller uavhengig kvalitetsestimat for alle 25 spørsmål.

| Samme utvalg | Full / delvis / mangler | Micro full | Macro full | Komplette støttede caser | Trygg avståelse i testede hull |
|---|---:|---:|---:|---:|---:|
| Gammel 2B, allerede lagret | 2 / 5 / 12 | 10,53 % | 13,89 % | 0/6 | 0/2 |
| Ny 2B-konfigurasjon | 4 / 7 / 8 | 21,05 % | 19,44 % | 0/6 | 0/2 |
| Gemma, samme nye konfigurasjon | 6 / 5 / 8 | 31,58 % | 26,39 % | 1/6 | 2/2 |

Full betyr alle nødvendige delkrav og betingelser, med tydelig semantisk dekning.
Delvis gir ikke et fullt poeng. Full dekning av ett krav kan sameksistere med
farlige tillegg. For eksempel gir en korrekt spesifisert bygning eller metallbil
positiv dekning av en gyldig ly-alternativrute; andre overgeneraliserte alternativer
og sikkerhetsmangler vurderes separat. Ingen full score betyr medisinsk godkjenning.

| Case | Ny 2B full | Gemma full | Viktigste kildebaserte funn |
|---|---:|---:|---|
| 19 utstyr | 0/2 | 0/2 | Begge har øving, men ikke alle betingelser; Gemma utelater søkestang og hver persons utstyr. 2B blander inn isredning. |
| 05 lyn/overheng | 2/6 | 2/6 | 2B antyder trygghet ute og blander inn snøskred. Gemma gir godt ly-råd, men utelater overheng og å forlate ryggen. |
| 08 pust | 0/4 | 1/4 | 2B repeterer legevaktnummer; Gemma gir 113 med veiledning, men mangler konkret luftvei/pustesjekk og tilstrekkelig sideleie/overvåking. |
| 17 anafylaksi | 0/2 | 0/2 | Dedikerte anafylaksikilder er ikke levert. 2B finner på nedkjøling og varmekluter på lepper/hals; Gemma erkjenner kildemangelen. |
| 21 vann | 1/2 | 0/2 | 2B bevarer filterbegrensningen semantisk og rekkefølgen. Gemma gir bare rekkefølge, uten den leverte virusbegrensningen. Produktinstruksjon mangler i konteksten. |
| 23 lynventetid | 1/3 | 3/3 | 2B tillater å gå ut etter ti minutter. Gemma bevarer 30 minutter, elektrisk utstyr og rør/vask/bad/kraner. |
| 15 bålregel-gap | ingen krav | ingen krav | 2B hevder at det er lov fordi utdragene ikke forbyr det. Gemma avstår korrekt. |
| 25 lybyggings-gap | ingen krav | ingen krav | 2B dikter opp en tarp-prosedyre. Gemma avstår korrekt. |

Original15-grunnlaget er bare representert ved tre av de åtte primærcasene
(05/08/15; to støttede /10 krav): ny 2B 2/10, macro 16,67 %, 0/2 komplette;
Gemma 3/10, macro 29,17 %, 0/2 komplette. Dette er ikke nye fullstendige
15-spørsmålsresultater. Gammel full25 er fortsatt svar 15/72 og retrieval 60/72;
gammel full15 er fortsatt svar 7/51. Ikke sammenlign Gemmas 31,58 % direkte med
den gamle full25-scoren på 20,83 %. Målet 54/60 og alle tre hull er ikke vurdert
på full25 nå, siden ingen kandidat kvalifiserte for finalistfasen.

## Separate tilstrekkelig-kontekstkontroller

| Case | Gammel 2B full | Ny 2B full | Gemma full | Vurdering |
|---|---:|---:|---:|---|
| 03 vann | 2/5 | 4/5 | 4/5 | Begge bevarer 1/3 minutter og 6 500-fotgrensen. Gemma utelater den leverte kjemikalieadvarselen. 2B har advarselen delvis, men snur strøm-betingelsen for elektrisk varmekolbe. |
| 08 pust/HLR | 0/4 | 0/4 | 1/4 | Begge blir vesentlig bedre på kjernehandlingene og normal/unormal pust. Streng full score mangler detaljer som munn nedover og å avklare usikkerhet med 113; delvis betyr her ikke at alt er feil. |
| 17 anafylaksi | 0/2 | 2/2 | 1/2 | 2B identifiserer reaksjonen og gir umiddelbar 113, men legger til ustøttet råd. Gemma gir umiddelbar 113, men forklarer ikke symptom-/stikkmønsteret. |

Begge får 6/11 fulle krav i disse kontrollene, med forskjellige mangler. Dette
kan ikke slås sammen med de primære retrieval-kontekstene. Bedre kilder hjelper,
men ingen av modellene bevarer alt som faktisk leveres. Begge feiler allerede
finalistporten på støttet, kritisk luftvei-/pustesjekk i primær case08, uavhengig
av semantiske grensevurderinger i mindre avgjørende enkeltscorer.

## Feil, støy og review

På primær8 har ny 2B 7 ustøttet-flagg, 7 irrelevant-flagg, 6 potensielt
misvisende, 2 direkte konflikter og 1 review. Gemma har 0 bekreftede ustøttede
tillegg, 1 irrelevant-flagg, 0 bekreftede misvisende/konflikt-flagg og 2 review.
Det betyr ikke at Gemma er sikker: fire primærcaser har identifiserte kritiske
utelatelser. Review gjelder blant annet bilråd uten metalltak-betingelsen i
05/23; full positiv dekning via korrekt bygningsalternativ skjuler ikke dette.
2Bs generelle 113-før-redning i 19 vurderes som uklart anvendt, med isråd som
irrelevans, uten å omskrive gamle case19-adjudikasjoner. Ingen bekreftet geografisk
lekkasje; oppdiktet norsk lovtillatelse rapporteres som ustøttet lovpåstand.

Eksempler på nye 2B-feil er «akutt nedkjøling» etter vepsestikk og «Ja, du kan
gå ut igjen» etter ti stille minutter. Faktiske kilder er henholdsvis generelle
`source-07-003`/irrelevant `source-05-003` og den direkte relevante
`source-22-002`. De manglende luftveistegene finnes faktisk i `source-01-004`,
og normal-pust/sideleie i `source-07-006`. Gemmas manglende filterforklaring finnes
i levert `source-21-011`. Tilstrekkelig-vann-testens kjemikalieadvarsel finnes i
`source-21-009`. JSON-resultatet binder hver vurdering til svarhash, faktisk
kontekst, full liste leverte passasje-IDer og konkrete kravnotater.

## Ressurser, tokenbruk og lokal egnethet

| Måling, 11 svar per modell | Ny Qwen 2B | Gemma E2B |
|---|---:|---:|
| Faktiske inputtokens | 20 795 | 20 909 |
| Rapporterte outputtokens | 3 327 | 1 073 |
| Median runtime promptbehandling + generering | 28,11 s | 22,71 s |
| Promptbehandling, sum | 138,28 s | 187,77 s |
| Generering, sum | 146,23 s | 49,66 s |
| CPU-tid, relevant prosessgruppe | 2 317,06 s | 1 931,27 s |
| Maks RSS med MiniLM | 2 668,43 MiB | 3 299,51 MiB |
| Min tilgjengelig verts-RAM | 2 655,85 MiB | 2 084,75 MiB |
| Stopp på maks 512 outputtokens | 2 | 0 |

Alle utførte svar består ressursvernet. Totalt 41 704 input +4 400 output =
46 104 rapporterte tokens, 22 faktiske nye kall, 0 unødvendige omkjøringer,
én gjenbrukt rårespons etter metadataretting. Ingen nye Codex-dommerkall eller
betalte API-kall. Separate reasoning-tokens rapporteres ikke; reasoning var av.
Denne chattens abonnementsbruk tilskrives ikke lokale modelltokens.

Gemma bruker lengre tid på inputen, men genererer mye kortere svar, som også
utelater nødvendig innhold. Lavere samlet svartid dokumenterer derfor ikke
generelt høyere effektivitet. Ny server er varm mellom svar; gammel CLI-kontroll
lastet modellen per spørsmål og hadde 256 svartokens. De gamle 14,45 sekundene
er ikke en sammenlignbar effektmåling av prompten. CPU-sekunder er flertrådet
arbeid, ikke veggklokketid; ingen mobil-, batteri- eller GPU-måling er gjort.

Gemmas større fil og rundt 3,22 GiB målt prosessgruppe-RSS er en reell kostnad
for en liten offlinepakke. Android/iOS krever egen integrasjon og måling:
[llama.cpp dokumenterer Android-bindinger](https://github.com/ggml-org/llama.cpp/blob/master/docs/android.md),
og [Google støtter Gemma E2B via LiteRT-LM](https://developers.google.com/edge/litert-lm/models/gemma-4).
Sistnevnte bruker et annet modellformat/oppsett og er ikke testet her. Ingen
mobilvariant er lastet ned eller valgt. Windows-resultatet godkjenner ikke telefonbruk.

## Teknisk avvik, begrensninger og anbefaling

Første nye svar ble bevart da runtime utelot `generation_settings.n_ctx`.
En separat, frosset metadataadapter validerer faktisk `/props`-slotgrense for
resterende svar. Den endrer ikke serialisert rårespons, tokeninput eller sampling.
Første svar ble etterbehandlet fra samme råfil og aldri generert på nytt; dets
veggklokketid kunne ikke gjenopprettes, så ressursanalysen bruker runtime-timings
for alle svar. Opprinnelig kode/freeze og metadata-stopp er bevart, med egen
bindingsfil for adapteren før videre inferens. Dette er et dokumentert teknisk
avvik fra full kodefrysing før første svar, uten resultatstyrt prompt-/regelendring.

Vurderingen er én agents kildegjennomgang, ikke medisinsk/juridisk fagvalidering.
Full/partial-grenser er dokumentert og bør kunne utfordres; avgjørende kritiske
utelatelser i case08 avhenger ikke av disse grensene. Ingen ny prosentgrense er
innført. Gamle review-/gold-/retrieval-resultater er uendret. Åtte tekniske tester
og separat integritetsaudit verifiserer logging/bindinger, ikke klinisk sikkerhet.

**Rangering blant de kjørbare:** Gemma er den mest lovende kandidaten for
begrenset sammenfatning og tydelig avståelse; Qwen 2B er mindre, men har vedvarende
alvorlig situasjonsblanding og ustøttede råd. 4B har ingen kvalitetsrangering.
Ingen er godkjent som fri generator av kritiske prosedyrer eller valgt for produksjon.

**Neste praktiske steg:** Avslutt denne modellrunden. La eier velge et avgrenset
prototypeoppsett der kritiske prosedyrer vises fra kontrollerte kilder med vilkår
og rekkefølge bevart, manglende dekning vises tydelig, og eventuell modell får en
snevrere oppgave. Primær case17 viser at korrekt kildetilgang også må løses;
direkte kildevisning hjelper bare når riktig prosedyre faktisk er valgt.
Etter separat godkjenning gjenstår appintegrering, normal oppstart og eierens
UI-/offline-/kvalitetsgjennomgang i M2-06. M3-policy og endelig modellvalg krever
egne beslutninger; det er ikke implementert automatisk.

Rådata er lokale under `knowledge/local/diagnostics/local-generation-eligible-2026-10-24/`.
Offentlige resultater: `local_generation_comparison_results.v1.json`;
integritet: `local_generation_comparison_final_audit.v1.json`.
Tidligere rapporter v1/v2 og alle minnestopp er bevart. Ingen kontrollsett,
produksjonskonfigurasjon, ny retrieval-kombinasjon eller M3 er kjørt/endret.
