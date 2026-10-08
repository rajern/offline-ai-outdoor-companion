# Outwise — avgrenset dommerpilot v1

Dato: 2026-10-08. Status: fullført pilot; valg av dommer avventer eierens gjennomgang.

Foreløpig anbefaling er **GPT-6.1 Sol API / Medium til videre kontrollert
kalibrering**. Alle 90 planlagte vurderinger ble lagret og validert. API-forbruket
var estimert til **$0,571171**. Én positiv Luna-vurdering mangler støtte for hele
kravet, og samtlige oppsett har uavklart støyvurdering. Piloten godkjenner ikke
automatisk scoring eller retrieval-optimalisering.

## Oppsett og avgrensning

Tre dommere sammenlignes: GPT-6 Luna API / Medium, GPT-6.1 Sol API / Medium
og GPT-6.1 Sol Codex CLI / Medium gjennom ChatGPT-abonnementet. Det er brukt
lagrede A/B/B8/C8/C8U8-kontekster fra 2026-10-07, uten nye retrieval-kjøringer.
Vi vurderer informasjon levert til Qwen, ikke genererte svar.

Prompt, schema, input, referanser, modellvalg, vurderingsregler og runner ble
frosset før første historiske kall, 2026-10-08 kl. 11:05:55 UTC. De samme 30
inputene ble levert i samme anonymiserte, blandede rekkefølge til alle tre.
Konfigurasjonsnavn, gamle vurderinger, similarity/rank, skjulte kildesitater og
utviklingsagentens samtalehistorikk ble ikke levert. Kun nødvendige, lagrede
utdrag fra kilder med kontrollert godkjennings-/gjenbruksmetadata ble sendt.
Råtekst, referanser, responser og forbrukslogger er lagret lokalt og Git-ignorert.

Det er seks spørsmål, 25 ordinære kontekster med 110 kravvurderinger per dommer
og fem kontekster for ett forhåndsdefinert kunnskapshull. Kravlisten for hullet
er tom og gir aldri full score. Alle fem konfigurasjoner beholdes som bestilt,
men inputhashene viser bare **24 unike input**. Resultatene er derfor korrelerte,
ikke 30 uavhengige testoppgaver. Støy- og geografimål for ordinære kontekster
har nevner 25; de fem gapkontekstene rapporteres separat.

De historiske referansene ble skrevet av tidligere Codex-agenter gjennom
sitatbasert inspeksjon. De er **ikke dokumentert som uavhengig menneskelig
ekspertfasit**. «FP/FN mot referanse» er uenighet med disse etikettene.

## De seks spørsmålene

| Case | Uendret spørsmål | Krav |
|---|---|---:|
| 02 | Vi har gått lenge i regn og vind. Turkameraten min er gjennomvåt og skjelver kraftig, men er våken og snakker normalt. Vi har sovepose og fjellduk. Hvordan hjelper jeg ham nå? | 5 |
| 03 | Vi har gått tomme for drikkevann på tur. Bekken ser helt ren ut, og vi har stormkjøkken. Kan vi bruke vannet derfra, og hva bør vi gjøre med det først? | 5 |
| 06 | Turkameraten min skar seg dypt i leggen på en skarp stein. Det blør mye og trekker gjennom tøyet vi har lagt på. Hva skal vi gjøre først? | 4 |
| 07 | Jeg er voksen og sølte akkurat kokende vann over hånda da vi laget kaffe på tur. Huden er rød og vond, og det begynner å komme blemmer. Hva gjør jeg nå? | 4 |
| 08 | En voksen i turfølget sank plutselig sammen på rasteplassen og svarer ikke når vi snakker til henne. Brystet beveger seg jevnt, men vi er usikre på hva vi skal gjøre. Hvordan hjelper vi henne? | 4 |
| 15 | Vi telter ved et vann i Norge i juli og vil lage et lite bål til matlaging. Er det lov her, og hvilke regler gjelder? | 0, kjent hull |

Utvalget omfatter full/delvis dekning, norsk/engelsk kildegrunnlag, alvorlig
blødning, normal/unormal pust, tidsgrenser, høyde-/vannbetingelser og negasjoner.
Det finnes ingen positive geografifeil i dette utvalget. Enighet om fravær av
slike feil tester ikke dommernes evne til å oppdage dem.

## Resultater og forbruk

| Mål | Luna API | Sol API | Sol Codex CLI |
|---|---:|---:|---:|
| Planlagte/gyldige resultater | 30/30 | 30/30 | 30/30 |
| Item-enighet med historisk referanse | 108/110 (98,2 %) | 107/110 (97,3 %) | 107/110 (97,3 %) |
| Positive avvik (FP) mot referanse | 0 | 0 | 0 |
| Negative avvik (FN) mot referanse | 2 | 3 | 3 |
| Avgjorte krav / `uncertain` | 110/110 / 0 | 110/110 / 0 | 110/110 / 0 |
| Kontekster med `requires_review` | 0 | 0 | 0 |
| Case-enighet om komplett pass | 25/25 | 25/25 | 25/25 |
| Komplette passer / falske komplette passer mot referanse | 8/25 / 0 | 8/25 / 0 | 8/25 / 0 |
| Irrelevans: uenighet, FP/FN mot referanse | 4/25, 1/3 | 2/25, 1/1 | 2/25, 1/1 |
| Potensielt misvisende: uenighet, FP/FN mot referanse | 14/25, 4/10 | 12/25, 3/9 | 9/25, 3/6 |
| Geografi: uenighet / positive referanser | 0/25 / 0 | 0/25 / 0 | 0/25 / 0 |
| Schema-, itemantall- eller sitatvalideringsfeil | 0 | 0 | 0 |

De fem gapkontekstene har tom itemliste, `coverage=null` og ingen komplett
pass for alle tre. Alle merkes irrelevante; ingen merkes misvisende eller
geografisk feil. Dermed er gapbehandlingen riktig i disse fem tilfellene.
Sol API og Sol CLI er enige på alle 110 kravbeslutninger. De er likevel uenige
om misvisende-flagg i **7 av 25** ordinære kontekster og irrelevans i 2 av 25.
API-modelldifferansen Luna/Sol er ett krav og seks misvisende-flagg.

| Faktisk rapportert forbruk, 30 resultater | Luna API | Sol API | Sol Codex CLI |
|---|---:|---:|---:|
| Input-tokens | 82 919 | 82 919 | 208 579 |
| Cached input, del av input | 19 110 | 19 110 | 24 192 |
| Cache-write input, del av input | 63 719 | 63 719 | 0 rapportert |
| Output-tokens, inklusive reasoning | 48 395 | 37 742 | 36 112 |
| Reasoning-tokens, del av output | 28 354 | 4 303 | 4 843 |
| Total tokens | 131 314 | 120 661 | 244 691 |
| Sum målt kalltid | 489,74 s (8,16 min) | 676,15 s (11,27 min) | 1 038,32 s (17,31 min) |
| Median per kall | 15,46 s | 22,14 s | 34,54 s |
| Estimert API-kostnad | $0,032362475 | $0,538808500 | Ikke målt i USD; abonnement |

Input/output/reasoning kommer fra Responses-usage eller CLI `turn.completed`.
Total tokens for CLI er summen av rapportert input og output. Reasoning og
cache-tokens er delmengder, ikke tillegg. Kalltid inkluderer nettverks-/CLI-
overhead og måler ikke bare modellberegning. Sum kalltid er ikke samlet veggklokke-
tid, siden CLI og API kjørte samtidig.

Prisene ble kontrollert 2026-10-08 og frosset i konfigurasjonen. USD per million
input / cached input / cache-write / output:
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna):
0,10 / 0,01 / 0,125 / 0,50;
[Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol):
2,00 / 0,10 / 2,50 / 10,00. Vanlig ikke-cachet input beregnes som input minus
cache-read og cache-write. Alle 60 API-kall har faktisk usage; ingen retries
eller ukjente API-belastninger. Totalen er $0,571170975 mot konservativ
forhåndsreservasjon $3,130882125 og grense $5. Dette er et usage-basert estimat,
ikke bekreftet faktura.

**Forbruk utenfor de 90 inkluderte resultatene:** En syntetisk CLI-smoketest
før historiske kall brukte 5 428 input + 93 output = 5 521 tokens, 0 reasoning,
6,04 sekunder, via abonnementet. En feil i kjørekoordineringen førte også til
ett ekstra historisk CLI-kall da hovedprosessen nådde CLI-alternativet mens
den separate CLI-prosessen avsluttet. Skrivevernet avviste overskriving;
de 30 opprinnelige CLI-resultatene er bevart og ekstrakallet er ikke analysert.
Ekstrakallets usage/kjøretid ble ikke lagret og er **ukjent**, ikke null.
Registrert abonnementsforbruk er derfor minst **250 212 tokens pluss det
ukjente ekstrakallet**. Ingen ekstra API-kall oppstod. Feilen er dokumentert
og gjenopptaksoppskriften krever én aktiv worker per alternativ.

## Viktige funn ved gjennomgang

**Mulig feil i historisk referanse:** Case 08, A, B og C8, krav 1 krever både å
ringe 113 og å få veiledning. De leverte blokkene beskriver oppringning, men
ingen veiledning. Den gamle positive begrunnelsen dokumenterer bare oppringning.
Et negativt dommerresultat følger derfor den frosne regelen om alle nødvendige
betingelser. Dette er ikke automatisk en falsk negativ dommerfeil. Referansen
beholdes uendret; retting krever separat gjennomgang.

**Konkret positiv dommerfeil som referansetabellen skjuler:** I case 08 C8
(`context-23`) godkjenner Luna krav 1 med sitat/begrunnelse som bare støtter
oppringning. Ingen levert blokk beskriver veiledning. Sol API og Sol Codex
avviser kravet og registrerer den manglende komponenten. Lunas positive er
en feil etter den frosne konjunksjonsregelen, selv om historisk referanse
også er positiv. Dette er minst én dokumentert delkravsgodkjenning uten
full støtte; det gjør ikke hele casen til en falsk komplett pass. Alle tre
godkjenner derimot C8U8, hvor levert kontekst faktisk beskriver hjelp fra 113.

**Sikkerhetskritisk mangel oppdages:** I case 06 mangler de leverte kontekstene
varsling ved stor/ustoppelig ytre blødning. Varsling ved indre blødning eller
senere tilstandsendring dekker ikke dette kravet. I case 08 erstatter ikke
barneprosedyrer, ett minutts pustesjekk ved nedkjøling eller manglende
HLR-/usikkerhetsbetingelser de ordinære voksenkravene. Dette handler om
tekstdekning; piloten gir ingen klinisk validering.

**Støyreglene er ikke tilstrekkelig kalibrert:** Handlingsråd for mindre
blødninger i case 06 og andre sårtyper i case 07 merkes ofte bare irrelevante,
mens referansen også merker mulig feilbruk. Enkelte dommere merker på sin side
isrednings-/sideleieråd i case 02 som potensielt misvisende når referansen ikke
gjør det. Synlige betingelser gjør teksten situasjonsavgrenset; det avgjør
ikke alene om feilbruk skal telle som misvisende. Her trengs en eksplisitt
grense mellom irrelevans, risiko for feil anvendelse og faktisk konflikt.
Et negativt misvisende-flagg er ikke dokumentasjon på at konteksten er trygg.

**Stabilitet:** Duplikater vurderes som selvstendige, allerede avtalte kall.
Luna gir forskjellig misvisende-flagg på de identiske C8/C8U8-inputene for
case 06. Sol Codex varierer samme flagg mellom identiske B8/C8/C8U8-input
for case 07. Alle sju parvise duplikatsammenligninger har samme kravbeslutninger
for hver dommer. Misvisende-flagg varierer i 1/7 par for Luna, 0/7 for Sol API
og 2/7 for Sol CLI; CLI-avvikene kommer fra én gruppe med tre identiske input.
Dette er dommer-/prosessvariasjon, ikke en forskjell i retrieval.
Det ble ikke bestilt flere repetisjoner eller endret prompt etter dette funnet.

**Separat irrelevans:** Luna og Codex merker et generelt forberedelsesråd i
case 02 A som irrelevant, mens historisk referanse utelater det. Dette kan
være en referanseutelatelse; det er ikke en klar dommerfeil. I case 08 kan
barneråd få misvisende-flagg uten et eget irrelevansflagg. Kategoriene er ikke
gjensidig utelukkende og må kalibreres som separate utfall.

Case 07s krem-/salveuenighet inngår verken i kravdekning eller støyvurdering.
Ingen gapkontekst gis en komplett pass. Null rapportert `uncertain` er ikke
bevis på sikker eller velkalibrert usikkerhet.

## Modell- og kjøremåteverifikasjon

API-tilgang ble kontrollert for `gpt-6-luna` og `gpt-6.1-sol` før historiske
kall. Begge kjøres med Responses API, `reasoning.effort="medium"`, strict
JSON-schema, ingen verktøy, `store=false`, standard service tier, 6 000
maksimale output-tokens og ingen SDK-retries. Responser kontrolleres mot
forventet modell-ID. Modellnavnene er aliaser; ingen datert backendversjon
er oppgitt eller utledet.

Codex CLI 0.162.0-alpha.2 rapporterer «Logged in using ChatGPT». Den lokale
modellkatalogen bekrefter ID `gpt-6.1-sol` og støtte for Medium. Hvert kall
setter begge eksplisitt og tvinger ChatGPT-innlogging. API-nøkkelvariabler
fjernes fra barnets miljø. Hver dommer starter uten historikk i en ny katalog
utenfor repoet, med prosjektinstruksjoner, ferdigheter, shell, apper, plugins,
nettlesing, hukommelse og agentdelegering deaktivert. Verktøyhendelser ville
ugyldiggjort resultatet og stoppet CLI-alternativet.

**CLI-begrensning:** JSON-hendelsene oppgir ikke serverens faktiske modell-ID
eller backendversjon. Katalog og eksplisitt forespørsel er verifisert; serverens
identitet er ukjent. Det ble ikke byttet modell eller resonneringsnivå.
Codex tilfører egne system-/runtime-instruksjoner og høyere inputforbruk.
Det er derfor en sammenligning av kjøremåter med samme brukerdefinerte
judge-materiale, ikke identiske komplette provider-requests eller beviselig
identiske modellvekter. Ingen verktøybruk ble observert. Oppsettet gir
prosess-/verktøyisolasjon, ikke en separat OS-container.

## Foreløpig anbefaling og gjenstående arbeid

**Foreløpig anbefaling: GPT-6.1 Sol gjennom Responses API, Medium, med
menneskelig gjennomgang av støy og sikkerhetskritiske positive.** Den fanger
den konkrete manglende kravkomponenten som Luna overser i C8, og gir en enklere
kontrollerbar klient med rapportert modell-ID og faktisk API-usage enn CLI.
CLI er et brukbart abonnementsalternativ i denne piloten, men serveridentiteten
kan ikke bekreftes, runtime påvirker input og støyflagget varierer på identiske
input. API-kostnaden vurderes sammen med disse kvalitets- og driftsfunnene,
ikke som eneste utvalgskriterium.

Dette er tilstrekkelig for et **foreløpig valg til videre kontrollert
kalibrering**, ikke til å fastslå generelt best modell eller godkjenne
autonom scoring. Ett konkret skille på seks spørsmål gir begrenset evidens.
Piloten avdekker samtidig at høy referanseenighet kan belønne en feil.

Før automatisk scoring må vi godkjenne og uavhengig kontrollere referansene,
avklare støygrensene, teste gjentakelsesstabilitet, og inkludere negative
kontroller med én manglende betingelse, feil tall/enhet/negasjon/alder/
jurisdiksjon og ufarlig omformulering. Kalibrering og separat validering må
holdes atskilt; akseptgrenser og behandling av usikkerhet må fryses på forhånd.
De ni øvrige historiske spørsmålene er ikke sendt til dommerne. Holdout er
ikke åpnet, søkt i eller brukt. Dette er forslag til senere arbeid, ikke
aktiviteter utført som del av piloten.

Metodisk bygger oppdelingen av kravdekning og støy på prinsipper om detaljert
retrieval-/genereringsevaluering i [RAGChecker](https://arxiv.org/abs/2408.08067)
og separate kvalitetsdimensjoner i [RAGAS](https://arxiv.org/abs/2309.15217).
[ARES](https://aclanthology.org/2024.naacl-long.20/) motiverer behovet for
menneskelig kontroll og separat vurdering av dommerpålitelighet. Ingen av
arbeidene dokumenterer at vår prompt eller én av disse modellene er best.
Klientstrukturen i [masterprosjektet](https://github.com/JoakimRuud1/master-public/blob/main/src/judge_client.py)
ble inspisert som eksempel; den medisinske
1–5-rubrikken ble ikke brukt.

## Leveranse og kontroll

Nye filer i `evals/`:

- `retrieval_judge_prompt.v1.md` og `retrieval_judge_output.schema.v1.json`
- `retrieval_judge_pilot.v1.json` og `retrieval_judge_pilot.py`
- `requirements-judge.txt` og `test_retrieval_judge_pilot.py`
- `JUDGE_PILOT.md` og `retrieval_judge_pilot_report.v1.md`

`evals/README.md` er oppdatert med lenker til arbeidsflyten og rapporten.
Produktkode, produksjonsoppsett, gullkrav, historiske referanser, korpus og
indekser er uendret. Den avsluttende hash-/resultatkontrollen bekrefter dette
og revaliderer alle 90 resultater; alle 60 API-kall har usage i budsjettjournalen.
Gjenopptak etter fullføring avsluttet uten nye modellkall. M2-06 er fortsatt
åpen; dommerpiloten oppfyller ikke produktets øvrige akseptkriterier.

Kjøringen brukte Python 3.12, OpenAI SDK 3.26.1 og de fire versjonslåste
evalueringsavhengighetene i `requirements-judge.txt`, isolert fra produktet.
Frosne runner-/prompt-/schema-/inputhash og kildeidentitet finnes i lokal
`freeze.json`; endring av disse uten ny pilotversjon avvises.

17 lokale syntetiske tester og 11 eksisterende foundation-tester består.
De syntetiske testene dekker schema/sitater, tomme krav, delvis dekning,
usikkerhet, budsjett, nøkkelfjerning, overskriving og gjenopptak uten nye
betalte forsøk. De tester ikke samtidige workers; kjørefeilen over avdekket
at overskrivingsvern alene ikke hindrer et overlappende kall.
Resultatvalideringen sjekker eksakte sitater og strukturell
konsistens; den kan ikke bevise semantisk støtte for alle kravkomponenter.

Reproduksjon og begrensninger: [JUDGE_PILOT.md](JUDGE_PILOT.md).
Lokalt resultatsted: `knowledge/local/diagnostics/retrieval-judge-pilot-v1-2026-10-08/`.
Denne rapporten inneholder ingen lokale kildesitater eller hemmeligheter.
Arbeidet stopper etter piloten for gjennomgang og valg av dommer.
