# Outwise — Sol Codex Medium, dommervalidering v2

Dato: 2026-10-08. Status: stresstester fullført; historisk validering pågår.
Eieren valgte Sol gjennom Codex CLI / Medium / ChatGPT-abonnementet som
foreløpig dommer. Ingen OpenAI API-kall eller betalt API-forbruk inngår her.

## Endringer og teknisk kontroll

V2 krever en konkret feil handling i aktuell situasjon for «potensielt
misvisende». Tydelig merket råd for annen alder, alvorlighetsgrad eller situasjon
er normalt irrelevant, uten automatisk risikoflagg. Fjernede betingelser,
feil anvendelse og direkte motstridende aktuelle instrukser flagges separat.
Direkte konflikt er en underkategori av misvisende; irrelevans kan overlappe.
Faktisk fremmed lov/tjeneste/prosedyre skilles fra språk og utgiverland.
Kravdekning, støy og konflikt er separate mål; en konflikt erstatter ikke
dekning, men må avklares før resultatet brukes til konfigurasjonsvalg.

Alle delkrav må støttes, inkludert aktør, handling, tall, enhet, negasjon,
tid, betingelse og jurisdiksjon. Oppringning til 113 beviser ikke veiledning.
Semantiske ekvivalenter og støtte over flere blokker teller. Reell usikkerhet
blokkerer endelig scoring; den blir verken poeng eller et oppdiktet nullresultat.
Case 07-unntaket for krem/salve og kunnskapshullreglene beholdes.

En enkel OS-fil-lås hindrer samtidige v2-workers i samme checkout. Før hvert
kall skrives intensjon og aktiv-kall-journal; stdout/stderr lagres direkte før
tolking, og alle rapporterte turns tas med i usage. Avbrutte, fullførte kall
kan rekonstrueres fra loggen uten nytt kall. Ufullførte kall blokkerer nye
forsøk til avklaring. Resultater overskrives aldri. V1 er bevart som arkiv og
skal ikke startes parallelt med v2.

**14 lokale tekniske tester består**, inkludert konkurrerende prosesser,
krasjfrigivelse av lås, gjenoppretting uten inferens, invalide svar med bevart
usage, verktøyhendelser, usikkerhet/tomt gull og fjerning av API-nøkler.
De 17 v1-testene og 11 foundation-testene består også. Tester bruker syntetiske
Python-prosesser, ikke en ekstra modellkjøring.

## Syntetiske stresstester

| Test | Kontroll | Utfall |
|---|---|---|
| 01 | Hele kravet med handling og tidsbetingelse | Riktig `covered` |
| 02 | Ett nødvendig delkrav mangler | Riktig `not_covered` |
| 03 | Negasjon er snudd | Negativ dekning, misvisende og konflikt |
| 04 | Feil mengde: 20 ml i stedet for 2 ml | Negativ dekning, misvisende og konflikt |
| 05 | Tydelig merket feil alder | Negativ dekning, irrelevant, ikke misvisende |
| 06 | Tydelig merket tjeneste for feil jurisdiksjon | Negativ dekning, irrelevant og geografi |
| 07 | Hele kravet fordelt over to blokker | Riktig `covered` |
| 08 | Semantisk likeverdig omformulering | Riktig `covered` |
| 09 | Uvedkommende, harmløst råd ved siden av riktig støtte | Dekning og bare irrelevans |
| 10 | Riktig aktuell instruks pluss direkte motsatt aktuell instruks | Dekning pluss misvisende/konflikt |
| 11 | Råd for lav alvorlighet overføres eksplisitt til høy alvorlighet | Negativ dekning, irrelevans/misvisende/konflikt |
| 12 | Kjent hull med tom kravliste | Ingen komplett pass, irrelevant ekstratekst |
| 13 | Instruks til dommeren skjult i kildeblokk | Ignorert som instruks; delkrav fortsatt mangler |
| 14 | Case 07s krem/salveunntak | Unntaket påvirker ikke dekning/støy |
| 15 | Norsk ekvivalent og 0,5 m = 50 cm | Riktig `covered` |

**15/15 unike tester og 18/18 kall** matcher forventede kravbeslutninger,
alle fire støy-/geografiflagg og `requires_review`. Ingen JSON-/sitatfeil,
verktøybruk, ukjent usage eller uplanlagte kall ble registrert.
Test 05,09,10 ble gjentatt med identisk input: alle tre par har like krav,
støyflagg og review-status. Begrunnelser/sitatvalg trenger ikke være identiske.

Dette er utviklerlagede fiktive kalibreringseksempler. De ble valgt med
kjennskap til v1-funnene og er **ikke uavhengig validering eller medisinsk
ekspertfasit**. Ingen promptendring eller ny testrunde var nødvendig etter
modellresultatene. Usikkerhetsflyten er testet lokalt; stresstestene viser
ikke at modellens naturlige abstensjon er kalibrert.

## Case 08: referanser og kildebevis

Det leverte materialet i **A, B og C8** dokumenterer oppringning ved
bevisstløshet, men ikke veiledning. En lenke videre til en artikkel leverer
ikke artikkelinnholdet. De tre gamle positive vurderingene av krav 1 har
dermed ikke full støtte etter gjeldende konjunksjonsregel.
**B8 og C8U8** har derimot levert tekst som beskriver både oppringning og
hjelp med luftvei/sideleie. Her er hele kravet støttet.

Den tredje alternative bevisruten for case 08 / krav 1 i den eksisterende
sertifikatfilen sjekker bare oppringning og bevisstløshet. Den sertifiserer
også A/B/C8, og mangler veiledningskomponenten. Den bør ikke brukes som bevis
for hele kravet før separat kontroll/retting er godkjent. Eksisterende fasit,
referanser, sertifikater og pilotresultater er **ikke endret**.

Dette er utviklingsagentens tekstgjennomgang, ikke uavhengig menneskelig
adjudikasjon. Se `retrieval_judge_reference_review.v2.json` for hashes og
separat markering av tre referanse-/sertifikatproblemer. Eksakte kildesitater
og gamle bevis ligger bare i ignorert lokal gjennomgangslogg.

## Historisk validering

Frossen v2 evaluerer bare case 01,04,05,09,10,11,12,13,14 i de fem tidligere
lagrede konfigurasjonene. Dette er 40 ordinære kontekster med 145 krav og fem
gapkontekster med ti støttede delkrav. Ingen ny retrieval kjøres. Bare 31 av
de 45 komplette judge-inputene er unike; konfigurasjoner deler kontekst.
Prompt/schema/settings/validator/code og eksakte input-/referansehash ble
frosset etter stresstestene, før første historiske valideringskall.

Resultattabell og vurdering ferdigstilles når alle 45 avtalte kall er lagret.
Historiske referanser er agentlagede, ikke dokumentert menneskelig ekspertfasit.
Endrede støydefinisjoner forventes å gi uenighet med tidligere brede
feil-situasjonsflagg. Ingen regler endres på bakgrunn av valideringsresultatene.

## Tokens og kjøremåte

| Målt forbruk | 18 stresskall | 45 historiske kall |
|---|---:|---:|
| Input | 103 305 | Pågår |
| Cached input, del av input | 6 912 | Pågår |
| Output, inklusive reasoning | 3 277 | Pågår |
| Reasoning, del av output | 312 | Pågår |
| Total tokens | 106 582 | Pågår |
| Sum kalltid | 179,01 s | Pågår |
| Median per kall | 9,40 s | Pågår |

USD-kostnad er ikke beregnet for abonnementet; API-forbruk er null. CLI
0.162.0-alpha.2 rapporterer ChatGPT-innlogging, katalogen bekrefter
`gpt-6.1-sol` og Medium, og hvert kall setter begge eksplisitt. JSONL oppgir
ikke faktisk servermodell/revisjon; dette kan fortsatt ikke bekreftes.
CLI tilfører runtime-instruksjoner og tokens. Dommeren er uten historikk og
verktøy i en ny katalog, men er ikke isolert i en separat OS-container.

## Før de 31 retrieval-konfigurasjonene

Endelig pålitelighetsvurdering gjøres etter de 45 historiske kallene.
Sertifikatmiss må forbli «ikke bevist», ikke automatisk feil. Gyldige,
fullstendige bevis kan brukes som positive kontroller, men må dekke ALLE
komponenter og riktig anvendelse; case 08 viser en konkret manglende kontroll.
Semantisk vurdering er fortsatt nødvendig for alternative uttrykk og støy.
Uenighet mellom et sertifikat og dommeren må avklares, ikke skjules med prioritet.

Det gjenstår en liten adapter for fremtidige lagrede kontekster, cache-nøkkel
med eksakt kontekst/krav/prompt/schema/modell/settings/validatorversjon,
hybrid avklaringsregler og review-status som blokkerer uavklart vinnervalg.
Eieren må godkjenne håndtering av referansefeil, støydefinisjoner og nødvendige
akseptkriterier før optimisering. Ingen vilkårlig prosentgrense fastsettes
etter resultatene, og denne piloten godkjenner ikke ny gold eller produktsikkerhet.

Artefakter: nye v2-prompt/schema/settings/stressdata, `codex_judge_runtime.py`,
`retrieval_judge_validation.py`, tekniske tester og `JUDGE_VALIDATION.md`.
Rålogger, usage, hashes og kildeutdrag er under ignorert
`knowledge/local/diagnostics/retrieval-judge-validation-v2-2026-10-08/`.
V1, originale gullkrav, gamle referanser, kunnskapsbase og produksjon bevares.
Holdout er ikke lest eller brukt. Arbeidet stopper etter valideringsrapporten.
