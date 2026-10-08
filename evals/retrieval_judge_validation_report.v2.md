# Outwise — Sol Codex Medium, dommervalidering v2

Dato: 2026-10-08. Status: fullført; stoppet før retrieval-optimalisering.
Eieren valgte Sol gjennom Codex CLI / Medium / ChatGPT-abonnementet som
foreløpig dommer. Ingen OpenAI API-kall eller betalt API-forbruk inngår her.

**Vurdering:** Sol Codex Medium er brukbar som foreløpig semantisk dommer med
avklaring av tvilstilfeller og manuell kontroll av finalister. Denne kjøringen
gir ikke grunnlag for uovervåket konfigurasjonsvalg. Dekningen er stabil i dette
utvalget, men én tolkningsregel og støyvurderinger trenger eiergjennomgang.

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

**45/45 kall er fullført og gyldige.** Historiske referanser er agentlagede,
ikke dokumentert menneskelig ekspertfasit. Tallene nedenfor måler enighet med
referansene, ikke uavhengig dokumentert vurderingsnøyaktighet.

| Mål | Ordinære kontekster | Kunnskapshull, case 14 |
|---|---:|---:|
| Kontekster / kravvurderinger | 40 / 145 | 5 / 10 delkrav |
| Kravenighet | 143/145 (98,6 %) | 10/10 |
| Positive avvik mot referanse | 2 | 0 |
| Negative avvik mot referanse | 0 | 0 |
| `uncertain` / avklarte krav | 0 / 145 (100 %) | 0 / 10 (100 %) |
| Komplette pass | 15/40 | 0; full pass er sperret |
| Enighet om komplett pass | 40/40 | Ikke fullstendig svargull |
| Feil komplette pass mot referanse | 0 | 0 |
| Kontekster med irrelevans | 35/40 | 5/5 |
| Irrelevans: positive / negative avvik | 0 / 2 | 0 / 0 |
| Kontekster med potensielt misvisende innhold | 5/40 | 0/5 |
| Misvisende: positive / negative avvik | 0 / 3 | 0 / 0 |
| Geografiflagg / avvik | 0 / 0 | 0 / 0 |
| Direkte konflikt | 0 | 0 |

Ingen `requires_review`, JSON-/sitatvalideringsfeil eller verktøyhendelser.
Alle 15 par med identisk historisk input gir samme kravbeslutninger, alle fire
støy-/geografiflagg og review-status. Sammen med stresstestene er dette 18/18
stabile par. Lik feil ved repetisjon er fortsatt feil; gjentakelsene måler
stabilitet, ikke korrekthet. De ni spørsmålene og delte kontekstene er korrelerte,
og skal ikke omtales som 145 uavhengige prøver.

### Konkrete uenigheter

- **Case 05, A/B, krav 4:** Begge positive avvik er samme identiske input.
  Dommeren tolker en universell advarsel om at utendørsplasser ikke er trygge
  under torden som støtte for at klippeoverheng ikke er trygt. Referansen krever
  eksplisitt omtale av overheng. Det finnes en logisk kildebegrunnelse, men
  godkjent detaljnivå er uklart. Dette må avgjøres av eieren; det er verken
  dokumentert referansefeil eller sikkert dommerfeil. Begge komplette caser
  forblir negative på grunn av andre manglende krav. Ingen annen positiv
  dekning uten nødvendig kildegrunnlag ble påvist i de ni valideringscasene;
  dette utelukker ikke slike feil. Case 08s tre gamle positive referanser
  mangler derimot konkret veiledningsstøtte, som dokumentert separat ovenfor.
- **Case 09, A/B:** Kommunal omsorgstjeneste/evakuering er ikke relevant for
  varmeforebygging på gruppetur. Dommeren overser dette i to identiske inputs.
  Dette er en konkret irrelevansfeil, selv om forebyggingskravene er dekket.
- **Case 09, B8/C8/C8U8:** Referansene flagger råd om bevegelse for å produsere
  varme etter isredning som misvisende i varmeforebyggingscasen. Den leverte
  teksten beholder nedkjølings-/isredningsbetingelsene. V2 klassifiserer den
  som irrelevant, uten misvisningsflagg. Det følger den nye definisjonen for
  tydelig merket annen situasjon; de tre negative avvikene er ikke tre påviste
  farlige dommerfeil. Eieren må bekrefte hvilken støydefinisjon som skal brukes.

Det finnes ingen positive geografireferanser eller separate konfliktreferanser
i dette historiske utvalget. Positive slike tilfeller er derfor bare undersøkt
syntetisk. Ingen prompt, schema, settings eller valideringskode ble endret
under historisk validering. Originale referanser og gull er uendret.

### Deterministiske kildebevis

De eksisterende kontrollene ble kjørt på de samme lagrede tekstene, uten ny
retrieval eller endring av dommerresultatene. De gir 70 positive beviskandidater
av 145 ordinære krav; dommeren godtar alle 70. De øvrige 75 er **ikke bevist**,
ikke automatisk feil. Ingen proveniensfeil ble funnet. To av de ikke-beviste
kravene er overhengstilfellene som krever avklaring.

For case 14 gir kontrollene ingen positive bevis for de ti delkravene, mens
dommeren og referansene støtter fem: tilpasning av tur til faresignaler.
Det er ikke full støtte for kunnskaps-/erfaringskravet eller hele gapspørsmålet.
Dette viser hvorfor sertifikatmiss ikke kan gjøres til automatisk negativ score.
Ingen beviskontroll overstyrer dommeren i denne kjøringen. Case 08s mangelfulle
bevisrute må avklares før en slik hybrid får autoritet.

## Tokens og kjøremåte

| Målt forbruk | 18 stresskall | 45 historiske kall |
|---|---:|---:|
| Input | 103 305 | 320 833 |
| Cached input, del av input | 6 912 | 45 824 |
| Output, inklusive reasoning | 3 277 | 49 911 |
| Reasoning, del av output | 312 | 5 667 |
| Total tokens | 106 582 | 370 744 |
| Sum kalltid | 179,01 s | 1 570,69 s (26 min 11 s) |
| Median per kall | 9,40 s | 35,33 s |

Totalt **63 planlagte kall, 63 fullførte turns, 477 326 tokens og 29 min 10 s
summert kalltid**. Ingen ukjent usage, ekstra observerte dommerkall eller
overskrevne resultater. Reell gjenopptakelse etter alle 45 lagrede vurderinger
utførte ingen ny inferens. Frosne kode-/inputhash, originale gullkrav, tidligere
pilotresultater og produksjonsartefakter er verifisert uendret.

USD-kostnad er ikke beregnet for abonnementet; API-forbruk er null. CLI
0.162.0-alpha.2 rapporterer ChatGPT-innlogging, katalogen bekrefter
`gpt-6.1-sol` og Medium, og hvert kall setter begge eksplisitt. JSONL oppgir
ikke faktisk servermodell/revisjon; dette kan fortsatt ikke bekreftes.
CLI tilfører runtime-instruksjoner og tokens. Dommeren er uten historikk og
verktøy i en ny katalog, men er ikke isolert i en separat OS-container.
Ingen abonnementsgrense stoppet kjøringen. Dette beviser ikke kapasitet eller
tilgjengelig kvote for full evaluering, og tokenantall kan ikke konverteres til
en verifisert andel abonnementsforbruk. Ved samme gjennomsnitt som de historiske
kallene ville 775 vurderinger uten deduplisering kreve omtrent **6,39 millioner
tokens og 7,5 timer** sekvensielt. Dette er et anslag, ikke en måling av det
nye 25-settet; kontekstlengde, caching, kvoter og kjøreforhold kan endre det.

## Før de 31 retrieval-konfigurasjonene

Sertifikatmiss må forbli «ikke bevist», ikke automatisk feil. Gyldige,
fullstendige bevis kan brukes som positive kontroller, men må dekke ALLE
komponenter og riktig anvendelse; case 08 viser en konkret manglende kontroll.
Semantisk vurdering er fortsatt nødvendig for alternative uttrykk og støy.
Uenighet mellom et sertifikat og dommeren må avklares, ikke skjules med prioritet.

Det gjenstår en liten adapter for fremtidige lagrede kontekster, cache-nøkkel
med eksakt kontekst/krav/prompt/schema/modell/settings/CLI-/validatorversjon,
hybrid avklaringsregler og review-status som blokkerer uavklart vinnervalg.
Eieren må godkjenne håndtering av referansefeil, støydefinisjoner og nødvendige
akseptkriterier før optimisering. Ingen vilkårlig prosentgrense fastsettes
etter resultatene, og denne piloten godkjenner ikke ny gold eller produktsikkerhet.

**Anbefalt minste videre kontroll, ikke allerede godkjente akseptkriterier:**
Avklar overhengstolkningen, case 08s referanser/bevisrute og den nye
misvisningsdefinisjonen. Korriger irrelevanssvakheten i en ny promptversjon
dersom den skal telle i vinnervalget, med en ny avgrenset kontroll før bruk.
Sikkerhetsrelaterte positive uten full støtte og uavklart bevis-/dommeruenighet
må stoppe berørte scorer; `uncertain`/review får ikke avgjøre vinner.
Kontroller finalistenes faktiske kildestøtte manuelt. Dette er en liten,
praktisk kontroll for hobbyprosjektet, ikke et krav om ny omfattende infrastruktur.
Den nye 25-spørsmålsfasiten og autonome scorer/adgangsgrenser trenger fortsatt
separat eiergodkjenning. M2-06 er fortsatt åpen; denne dommervalideringen validerer
ikke Qwens endelige svar eller produktets sikkerhet.

Artefakter: nye v2-prompt/schema/settings/stressdata, `codex_judge_runtime.py`,
`retrieval_judge_validation.py`, tekniske tester og `JUDGE_VALIDATION.md`.
Maskinlesbare aggregater, inputhash, stabilitetspar og frosne kodehash ligger i
`retrieval_judge_validation_results.v2.json`, uten kildeutdrag.
Rålogger, usage, hashes og kildeutdrag er under ignorert
`knowledge/local/diagnostics/retrieval-judge-validation-v2-2026-10-08/`.
V1, originale gullkrav, gamle referanser, kunnskapsbase og produksjon bevares.
Holdout er ikke lest eller brukt. Arbeidet stopper etter valideringsrapporten.
