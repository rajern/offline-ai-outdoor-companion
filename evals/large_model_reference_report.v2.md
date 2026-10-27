# GPT-6.1 Sol-referanse — fullført 25. oktober 2026

**GPT bevarte alle13 informasjonskravene som de leverte kildene dekket fullt.**
Qwen-baseline bevarte8 og Gemma-baseline6 på nøyaktig samme spørsmål og
kildepakker. Dette er et tydelig signal om at lokal svargenerering er en viktig
flaskehals i det testede oppsettet. Det beviser ikke at små lokale modeller er
umulige, eller at kunnskapsbasen og hele appen nå er gode nok.

## Resultatet enkelt

Åtte spørsmål: seks kildestøttede situasjoner med15 nødvendige informasjonskrav,
og to kunnskapshull. Kildene dekker13 krav fullt og to delvis. Tallene gjelder
dette utvalget; de erstatter ikke resultatene for hele25-settet.

| Oppsett | Fullstendige krav av15 | Bevarte fullt leverte krav av13 | Helt dekkede kjernesvar av6 | Riktig avståelse av2 |
|---|---:|---:|---:|---:|
| Lokal Qwen baseline | 8 | 8 | 2 | 0 |
| Qwen, nye innstillinger | 2 | 2 | 0 | 0 |
| Qwen, ny prompt | 3 | 3 | 0 | 1 |
| Lokal Gemma baseline | 6 | 6 | 1 | 2 |
| Gemma, nye innstillinger | 6 | 6 | 0 | 2 |
| Gemma, ny prompt | 6 | 6 | 0 | 0 |
| **GPT-6.1 Sol High, baselineprompt** | **13** | **13** | **4** | **2** |

GPT fikk13/15 fullstendige krav (**86,7%**), to delvise og ingen fraværende.
Alle13 fullstendige krav ble også vurdert fullt kildeforankret. De to aktiverte
betingede kravene var begge fullstendige. Begge kunnskapshull ble erkjent uten
oppdiktede prosedyrer eller regler.

Den låste dommeren fant ingen direkte konflikter, udokumenterte tillegg eller
kildebelagte kritiske utelatelser i disse åtte GPT-svarene. Ett `requires_review`
gjelder pustespørsmålets manglende kildegrunnlag. Dette er funn i en avgrenset
vurdering, ikke garanti for feilfrie eller trygge svar.

**13/13 betyr100% bevaring av de fullt leverte kravene. Det betyr ikke100%
samlet svarkvalitet.** Qwen-baseline hadde8/13 (61,5%) og Gemma6/13 (46,2%).

## Hva mangler fortsatt?

- **08, pust:** GPT bevarer vurderingen, riktig normalpust-gren og videre
  overvåking. Hele rubrikkravet inkluderer også en forgrening som kildepakken
  ikke leverer. Kravet er derfor fortsatt delvis, uten at dommeren slår fast en
  kildebelagt kritisk modellutelatelse.
- **21, vannbehandling:** GPT bevarer filterbegrensningen og rekkefølgen, og
  påpeker manglende dosering/virketid. Kravet om å følge produktets bruksanvisning
  blir ikke uttrykkelig formidlet; den delen er heller ikke fullt levert i
  kildene. Rubrikken er uendret og gir fortsatt delvis dekning.

Begge restpunktene sammenfaller altså med kravene som retrieval bare leverer
delvis. Dette innebærer ikke at enhver utelatelse kan tilskrives retrieval,
men vi finner ikke lenger tap av et fullt levert krav i GPT-referansen.

Sammenlignet med Qwen-baseline vinner GPT fem fullstendige krav og mister ingen;
sammenlignet med Gemma vinner den sju og mister ingen. Forskjellene er kontrollert
per kriterium, ikke bare ved å sammenligne summer. Alle åtte tekster og17
reviderte kriterievurderinger/funnlister er gjennomgått mot faktisk kildekontekst.
Rå vurderinger er bevart uten korreksjoner.

## Hva vi faktisk sammenlignet

Én High-generering per spørsmål med **den opprinnelige systemprompten**, samme
brukertekst, kilder og rekkefølge som den lokale baseline. Ingen rubrikk, fasit,
tidligere svar eller vurderinger ble gitt til generatoren. Ingen verktøy, nett-
søk eller samtalehistorikk. Den eksakte prompten ble gitt som erstatning for
CLI-grunninstruksjonene; brukerinnholdet gikk uendret via stdin.

Etter at alle åtte svar var lagret, fikk hver en anonym, uavhengig vurderingssesjon
med **uendret rubrikk og GPT-6.1 Sol Medium**. Generatorens High og dommerens
Medium er forskjellige roller. Tidligere lokale svar/vurderinger og bestått
identisk kontroll ble gjenbrukt; ingen baseline ble generert eller vurdert på nytt.

Dette er en praktisk referanse med mer regnekraft. Codex-innpakning, High-
resonnering og sampling er forskjellige fra lokal thinking-off. Seed og lokal
512-token-grense ble ikke satt gjennom udokumenterte CLI-alternativer.
GPT-svarene hadde32–170 ord, totalt613, median71. Slutttekst ble ikke klippet.
Disse forskjellene betyr at resultatet ikke isolerer effekten av parameterantall.

Samme modellfamilie som generator og dommer kan favorisere egen svarstil.
Den etterfølgende agentgjennomgangen er heller ikke uavhengig klinisk fasit.
Nye dommergrupper inneholdt ett svar, mot opptil tre/fire tidligere. Utvalget
er åtte utviklingsspørsmål, ikke holdout eller en stabilitetstest. Servermodellens
eksakte revisjon og hele den skjulte modellinnpakningen er ikke eksponert.

## 429-feilen og fortsettelsen

Den opprinnelige kjøringen lagret fire svar før21 traff HTTP429. Ingen ferdig21-
tekst eller tokenrapport fantes å gjenbruke. Brukeren autoriserte fortsettelse.
En separat låst adapter gjenbrukte de fire svarene byteidentisk, tillot ett nytt
21-forsøk og spredte nye CLI-starter med minst60sekunder. De fire manglende
High-svarene lyktes uten nye transportgjentakelser.

To Medium-kall måtte vente etter429:19 omtrent24sekunder og23 omtrent143.
Begge ga til slutt komplette, validerte vurderinger. Retry var begrenset til
høyst én varslet transportgjentakelse før noen tekst og høyst300sekunder;
kommandolinje, innhold, modell og ressursgrenser ble ikke endret.

Den første watcher-versjonen hadde en feil: den tolket en gammel429-advarsel
som en ny risiko da19s ferdige vurdering kom, og avsluttet prosessen under
nedstenging. Råloggen inneholdt allerede fullstendig JSON, `turn.completed` og
tokenrapport. En separat retting og test korrigerte tilstandshåndteringen.
Vurderingen ble gjenbrukt fra råloggen; original feilstatus og ikke-null exit
er bevart. Ingen ny19-vurdering ble kjørt eller falsk exit0 rapportert.

**Totalt:** ni genereringsforsøk i CLI ga åtte ferdige svar, inkludert det gamle
avbrutte21-forsøket. Åtte unike dommerkall ga åtte ferdige vurderinger, én
gjenopprettet uten inferens. Observerte interne transportgjentakelser må ikke
forveksles med nye ferdige svar; alle rålogger er bevart. Minste observerte
avstand mellom nye CLI-starter var60,008sekunder.

Kontoen tillot fortsatt ordinær bruk. Årsak til429 er ikke bevist; vellykket
venting/pacing dokumenterer ikke at den opprinnelige abonnementskvoten var brukt
opp. Ingen kvotetilbakestilling, betalt API, kontobytte eller modellbytte ble brukt.

## Verifikasjon og kostnadsgrunnlag

Fire opprinnelige isolasjonstester, én avgrenset retry-policytest og én test av
korrekt tilstand etter en gammel advarsel består. Full offline-rekalkulering
kontrollerer alle råstrømmer, sluttekster, nøyaktige input, kilde-/sitatbindinger,
forespurte modellnivåer, tokenrapporter og uendrede klientgrenser.1270 tidligere
beskyttede filer samt de separate fortsettelses-/gjenopprettingsbindingene er
kontrollert. Alle gjenbrukte svar og første vurderings råstrøm er byteidentiske.

Kjent bruk: generering57354 tokens, vurdering71978, **minst129332 totalt**.
Det opprinnelige avbrutte21-forsøket rapporterte ingen bruk, så den faktiske
totalen er ukjent. Ukjent bruk er ikke null. Rapporterte reasoning-outputtokens
inngår i outputtotalen; de legges ikke til en gang til. Klientens RAM-grenser
måler ikke skymodellens minne, beregningskostnad eller mulig mobilkjøring.

## Konsekvens for videre arbeid

Resultatet støtter at vi bør fokusere på **hvordan den lokale løsningen velger
og gjengir det leverte innholdet**. Det gir ingen grunn til mer generell
rubrikkjustering. GPT klarer med originalprompten mye av det vi ønsker fra samme
kildepakke; manglene i lokale svar kan derfor ikke forklares med dårlige kilder
alene. Samtidig gjenstår de to delvis leverte kravene.

En enklere lokal svaroppgave eller mer direkte kildevisning med begrenset
tolkning er fortsatt aktuelle neste valg. Ren visning av dagens rå treffliste
løser ikke relevans eller manglende forgreninger. Denne testen avgjør ikke
endelig produkt-/sikkerhetspolicy og autoriserer ingen produksjonsintegrering.
M2-06-kvalitet er fortsatt åpen; M3 er ikke startet.

- [Fullstendige resultater](large_model_reference_results.v1.json)
- [Kildevurdering av alle åtte svar](large_model_reference_review.v1.json)
- [Teknisk kontroll](large_model_reference_audit.v1.json)
- [Forsøk, gjenbruk, venting og kjent bruk](large_model_reference_execution.v1.json)
- [Original protokoll](large_model_reference_protocol.v1.md),
  [autorisert fortsettelse](large_model_reference_continuation.v1.md) og
  [watcher-retting/gjenoppretting](large_model_reference_transport_recovery.v1.md)

Privat fullført kjøring:
`knowledge/local/diagnostics/large-model-reference-v1-2026-10-25/continuation-v2/`.
Original delrapport v1 og begge tekniske stopp er bevart. Offline-kontroll uten
inferens: `recover_large_model_reference_v1.py summarize --check`.
