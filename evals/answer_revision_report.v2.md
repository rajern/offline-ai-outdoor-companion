# Rubrikk og vurderingsmodell: fullført sammenligning

24. oktober 2026. **De samme 50 lagrede svarene er vurdert med gammel og ny
rubrikk, først Sol Medium og deretter Sol High.** Ingen nye Qwen-/Gemma-svar er
generert. Historiske vurderinger er bevart. Produksjon og M3 er uendret.

Hovedfunnet er todelt: Rubrikken påvirker hva som får poeng, og enkelte
dommervurderinger er for bokstavelige. Samtidig finnes konkrete feil og utelatelser
som ingen rimelig justering av målet fjerner. Dette er bedre dokumentasjon av
utviklingsstatus, ikke godkjenning av en nødrådgiver.

## Hva dataene faktisk består av

| Del | Lagrede svar | Hva de kan si noe om |
|---|---:|---|
| Historisk Qwen, hele utviklingssettet | 25 | Hele det eksisterende utviklingssettet |
| Ny Qwen 2B og Gemma, åtte screening-spørsmål hver | 16 | Sammenligning på samme begrensede delutvalg |
| Tre diagnostiske spørsmål, tre modell-/promptoppsett | 9 | Hva som skjer med særskilt valgt, tilstrekkelig kildekontekst |
| **Totalt** | **50** | **25 forskjellige spørsmål, ikke 50 uavhengige spørsmål** |

Utviklingssettet har 22 spørsmål med kildegrunnlag og tre deklarerte
kunnskapshull. Screeningdelen har seks støttede spørsmål og to hull. Det finnes
28 spørsmål/kontekstgrupper fordi tre spørsmål også har en egen diagnostisk
kontekst. Ett allerede definert utstyrskontrollsett med tre syntetiske svar ble
vurdert ved hvert resonneringsnivå, separat fra de 50 produktsvarene.

Dette er nyttig for feilsøking: spørsmål, svar og faktiske kildeutdrag er bevart,
og vi kan følge en feil tilbake til det modellen fikk. Alle 50 svarenes kilder
er kontrollert mot de opprinnelige modellinputtene, uten avvik.

Det er svakere som kvalitetstest for vanlig bruk. Spørsmålene er utviklingsdata
som har vært brukt gjentatte ganger i optimalisering. Screening og diagnostikk
er bevisst utvalgt, flere svar gjelder samme spørsmål, og rubrikkforfatteren kjente
svarene. Det er ingen uavhengig klinisk fasit, representativ brukerprøve eller
ny kontrolltest her. Holdout er ikke åpnet. Kildegrunnlagets medisinske aktualitet
er heller ikke nyvalidert i dette arbeidet.

## Hvordan rubrikken fungerer

Gammel rubrikk har **72 krav** for de 22 støttede spørsmålene. Et krav kan inneholde
flere ledd; alle må være med for «fullt». Hvert krav teller én gang i totalsummen.
Det er ingen klinisk betydningsvekting: ett langt prosedyrekrav og ett kort
faktakrav gir like mye. Dette gjør prosenten til en dekningsindikator, ikke en
andel medisinsk riktig tekst.

Den nye rubrikken fordeler de samme 72 kravene på **63 obligatoriske, fire
betingede og fem valgfrie**. Alle har individuell begrunnelse i
[beslutningsloggen](answer_rubric_decisions.v1.md). To ytterligere krav gjelder
den støttede delen av kunnskapshull 14 og holdes utenfor vanlig dekningsprosent.

Ny rubrikk tillater meningsmessig likeverdige formuleringer, henvisning til kjente
opplysninger i spørsmålet og ett gyldig alternativ der alternativer er tillatt.
Eksempler og forklaringer skal ikke automatisk bli ekstra obligatoriske handlinger.
Nødvendige betingelser, negasjoner, rekkefølge og tider beholdes. Betingede krav
vurderes når den oppgitte utløseren er aktiv; ellers «ikke aktuelt».

«Delvis» rapporteres separat, uten en oppfunnet halvpoengsvekt. Kildestøtte,
udokumenterte tillegg, situasjonsfeil, kritiske utelatelser og avståelse vurderes
også separat. **Full kjernedekning er ikke en helhetlig bestått vurdering.**
Merket «kritisk» bygger på forfatterens deklarerte sikkerhetsbetydning; det er
ikke en uavhengig, klinisk validert alvorlighetsklassifisering.

Rubrikken er dermed tydeligere, men ikke ferdig validert som endelig mål.
Blant annet krever bredden i håndhygienekravet, implisitte handlingsråd og
vektingen av små utelatelser fortsatt vurdering. Dette er dokumentert som
usikkerhet, uten å endre kravene etter resultatene.

## Resultater med uendrede modellsvar

Hele det historiske 25-settet; kun de 22 støttede spørsmålene inngår i brøkene:

| Dommer | Gammel rubrikk: fullt/delvis/fraværende | Ny obligatorisk kjerne: fullt/delvis/fraværende | Alle nye kjernekrav dekket |
|---|---|---|---|
| Medium | 12 / 30 / 30 av 72 | 13 / 26 / 24 av 63 | 0 av 22 spørsmål |
| High | 11 / 30 / 31 av 72 | 12 / 26 / 25 av 63 | 0 av 22 spørsmål |

Med Medium blir dette 16,7 % mot 20,6 %, og med High 15,3 % mot 19,0 %.
**Dette er endret vurdering og nevner, ikke forbedrede svar.** Ser vi bare på
de 63 beholdte kravene, øker antallet fulle krav fra 11 til 13 med Medium og
fra 10 til 12 med High. Begge flytter tre fra delvis til fullt og ett fra fullt
til delvis. Rubrikkendringen redder altså ikke den gamle helhetlige løsningen.

Den tidligere rapporterte 15/72-vurderingen tilhører den opprinnelige
arbeidsagenten, som er en annen assessor. Den erstattes ikke med disse tallene
og er ikke en kontrollert Medium-baseline.

På de samme åtte screening-spørsmålene gir **begge dommere samme dekningssummer**:

| Lagret oppsett | Gammel rubrikk | Ny kjerne | Full ny kjerne per støttet spørsmål | Trygg avståelse i hull |
|---|---:|---:|---:|---:|
| Historisk Qwen 2B | 3/19 | 4/15 | 0/6 | 0/2 |
| Ny Qwen 2B | 3/19 | 8/15 | 2/6 | 0/2 |
| Gemma | 5/19 | 6/15 | 1/6 | 2/2 |

Den opprinnelige agentvurderingens 2/19, 4/19 og 6/19 er bevart som egen
vurdering. Forskjellen til tabellen viser også dommeravhengighet.

Qwen får høyere ny kjernedekning enn Gemma, men dette gjør den ikke til en bedre
assistent. Qwen anbefaler eksempelvis umiddelbar 113-kontakt etter vepsestikk,
og fyller dermed det nye kjernekravet, samtidig som den dikter en
nedkjølingsforklaring og varmebehandling. På åtte svar flagger Medium
udokumenterte tillegg i sju Qwen-svar mot ett Gemma-svar; High i åtte mot to.
Flaggene er dommerfunn, ikke en validert feilrate. Med aktive betingede krav
inkludert har begge nye modeller bare ett komplett screening-svar av seks.

Den avgrensede diagnostikken er mer lovende; begge dommere er også enige her:

| Lagret oppsett, tre diagnostiske spørsmål | Gammel rubrikk | Ny kjerne |
|---|---:|---:|
| Historisk Qwen 2B | 1/11 | 2/8 |
| Ny Qwen 2B | 4/11 | 7/8 |
| Gemma | 5/11 | 7/8 |

Begge nye modeller dekker alle nye kjernekrav i to av disse tre svarene.
Pust-/HLR-svarene er vesentlig bedre enn med primærkonteksten, men mangler
munnens nedoverstilling i sideleie etter den frosne rubrikken. Gemmas
diagnostiske svar har ingen registrerte udokumenterte tillegg eller direkte
konflikter. Qwen har blant annet et snudd vilkår om elektrisk kokeutstyr.

Dette er et tegn på at **hvilken kontekst vi leverer betyr mye**. Det er ikke
87,5 % kvalitet for hele appen, eller bevis på at bare støy er årsaken: både
innholdsdekning og kontekstutvalg er endret i en liten, bevisst valgt diagnostikk.
Resultatene gir ikke grunnlag for å fastslå at modellstørrelsen alene er flaskehalsen.

## Medium mot High og gjennomgangen av uenigheter

Dommerne er enige om 139/145 historiske og 122/130 reviderte kriteriebeslutninger:
261/275, altså 94,9 %. Dette er **enighet, ikke målt korrekthet**. Støttelabelen
er lik for 119/130 reviderte kriterier; blant de 80 hvor begge gir positiv
dekning, er den lik i 76.

Alle **18 kriterie-/støtteuenigheter**, **35 avtalte, samstemte vurderinger i
høykonsekvenstilfellene** og **50 par av funn-/avståelsesvurderinger** er gjennomgått.
X/Y-vurderingene ble skrevet og hashforseglet før innsatsnivåenes nøkkel ble åpnet.
Tidligere Medium-funn og svar var kjent, så dette er bare delvis blinding.

Min kildebundne gjennomgang foretrekker High i sju uenighetspunkter og Medium i
fem; fem er fortsatt uavklart, og i ett er begge for bokstavelige. Flere punkter
er samme formulering vurdert under to rubrikker. Dette er derfor ikke et
statistisk grunnlag for å erklære High bedre. Gjennomgangen er heller ikke
uavhengig klinisk fasit. Råscorene er uendret; ingen delvis korrigert toppliste lages.

Konkrete eksempler:

- High er bedre på å avvise skredvurdering som delvis svar på bortkomst og på å
  holde feil 113-betingelser sammen med handlingen.
- Medium er bedre på ikke å gi delvis poeng for å la toalettavfall renne.
- Begge gir for lite historisk ly-dekning når et komplett bygningsalternativ
  allerede er oppgitt, fordi et annet kjøretøyalternativ mangler metalltak.
  Det siste skal vurderes separat.
- Ved bekken i spørsmål 24 omfatter det brede avstandsrådet også den beskrevne
  skråningen, etter den nye kontekstregelen. Begges krav om eksplisitt gjentakelse
  blir for bokstavelig. Dette beholdes som et eget vurderingslag.
- Støtte for en avgrenset riktig del versus hele en setning med flere alternativer
  er fortsatt et tolkningsproblem. Høyere resonnering løser ikke automatisk dette.

Funnstypene varierer mellom dommerne i 20/50 svar. Ett kunnskapshull har ulik
avståelsesklassifisering; teksten er tvetydig og regnes ikke som bekreftet trygg
avståelse. Gemmas to screening-avståelser er bekreftet av begge.

## Hva som fortsatt er påvist, og hva som er usikkert

I primærtilfellet med bevisstløshet mangler alle tre svar faktisk pustevurdering,
selv om den er levert. Gemma gir luftveisåpning, men går videre til HLR uten
avklart pust. Dette er en konkret svakhet også med enklere mål.

Anafylaksitilfellets primærretrieval inneholder derimot ingen stikkspesifikk
prosedyre. Gemmas beskrivelse av den mangelen er riktig, men den utelater
generelt, kildebelagt råd om akutt varsling. Det er ikke et vellykket corpus-gap-
svar. I vannfiltertilfellet er virusbegrensningen og rekkefølgen levert, mens
produktinstruksjonen mangler. Den siste utelatelsen er ikke bare genereringens feil.

Selve brannskadekilden har også motstridende kremråd. Dommerenighet avgjør ikke
slike kildespørsmål. Verken antall kritiske flagg eller kjernedekning alene er
et tilstrekkelig godkjenningsmål.

## Forskningsgrunnlag og praktisk betydning

[HealthBench](https://openai.com/index/healthbench/) støtter situasjonsspesifikke
krav med begrunnet viktighet. Den
[publiserte graderregelen](https://raw.githubusercontent.com/openai/simple-evals/main/healthbench_eval.py)
skiller reelle obligatoriske ledd fra illustrerende eksempler. Det støtter
metoden, men validerer ikke våre 63 krav. Outwise mangler tilsvarende faglig panel.

[RAGChecker](https://arxiv.org/abs/2408.08067) støtter skillet mellom retrieval,
dekning og kildestøtte. OpenAIs
[nyere evalueringsdrøfting](https://deploymentsafety.openai.com/gpt-5-6-august-update)
advarer dessuten om at lengre svar kan få høyere rubrikkscore uten tilsvarende
gevinst i brukbarhet eller sikkerhet. Vi har ikke målt faktisk forståelse og
handling hos en bruker på tur. Se også [forskningssjekken](answer_revision_research_check.v1.md).

Forslag videre: Bruk denne gjennomgangen til å ta én avgrenset produktbeslutning.
Kildebevarte prosedyrer i kritiske situasjoner, med begrenset språkmodellrolle,
er fortsatt et begrunnet alternativ. Dersom friere generering skal testes videre,
bør neste begrunnede hypotese handle om riktig og avgrenset kontekst, fremfor å
anta at bare enda en modell eller mer resonnering løser problemet. Dette er et
forslag til eieren; ingen sikkerhetspolicy eller ny test er implementert.

## Teknisk regnskap og etterprøvbarhet

Det dokumenterte [fortsettelsestillegget](answer_revision_continuation.v1.md)
ble lagt før nye kall. Den gamle case08-strømmen hadde ingen ferdig vurdering å
gjenbruke. Ni vellykkede kall, med 12 produktsvar og kontrollen, ble kopiert
byteidentisk uten inferens. Nye kall fikk 1 200 sekunders grense ved begge nivåer.
Det nye case08-forsøket tok 62,5 sekunder. Årsaken til det opprinnelige
420-sekundersavbruddet er ikke fastslått.

Det er 58 vellykkede kall i sammenligningen, 29 per nivå. Fortsettelsen gjorde
49 nye kall. Med det bevarte tidsavbruddet er det totalt 59 utsendte forsøk;
de tidligere transportfeilene var før utsending. Det var ingen parallelle dommere,
nye kvote-/tilgangsstopp eller ressursbrudd.

| Måling, vellykkede kall inkludert kontroll/gjenbruk | Medium | High |
|---|---:|---:|
| Kjente inputtoken | 245 476 | 245 484 |
| Kjente outputtoken, inkludert resonnering | 51 783 | 90 430 |
| Derav resonneringstoken | 9 070 | 43 948 |
| Total kjente token | 297 259 | 335 914 |
| Median tid per gruppe | 31,9 s | 60,3 s |
| Sum vellykkede kall | 1 073,0 s | 2 039,9 s |

Totalt er 633 173 token kjent, hvorav 537 612 gjelder fortsettelsens nye kall.
Tidsavbruddets bruk er **ukjent, ikke null**. Resonneringstoken inngår i output
og legges ikke til igjen. Medium inneholder gjenbruk fra en tidligere bølge;
latens er en beskrivelse av disse kjøringene, ikke et kontrollert serverbenchmark.

Samme CLI-binær, forfatterinstruksjoner, schema og input ble brukt. Alle 29
Medium/High-inputpar har identisk JSON-filhash. Modellforespørselen er
`gpt-6.1-sol`, CLI `0.164.0-alpha.11.1`, abonnementspålogging, isolerte
read-only/no-tools-sesjoner. Faktisk serverrevisjon og effekt av innsatsinnstillingen
kan ikke uavhengig bevises av JSONL. Verktøyadvarselen om utilgjengelig Code Mode
forekommer også i vellykkede kall og er ikke påvist årsak til det gamle avbruddet.

Fire eksisterende atferdstester består. Den avsluttende kontrollen bekrefter
frosne og historiske filer, 58 komplette svarstrømmer, inputbindinger,
kilde-/svarsitatenes forekomst og ressursgrenser. Ett High-kildesitat har 222
tegn mot promptens 220; det frosne skjemaet håndhever ikke tegnbegrensningen.
Sitatet finnes i kilden. Rådata er beholdt, og ingen ny vurdering ble kjørt for dette.
Automatiske sitatkontroller beviser ikke semantisk riktighet.

Private rålogger, input, vurderingspakker og forseglinger ligger i
`knowledge/local/diagnostics/answer-rubric-revision-v1-2026-10-24/continuation-v1/`.
Foreldrekjøringen `transport-v3/` er urørt. Arvede transportmetadata og den
opprinnelige 58-kallsrammen er presisert i `lineage-clarification.json`;
det autoriserte erstatningsforsøket gir 59 forsøk totalt.

Offentlige, kildefrie resultater: [råsummer](answer_revision_results.v3.json),
[uavhengig summering](answer_revision_analysis.v1.json),
[vurderingsgjennomgang](answer_revision_review.v1.json) og
[integritetskontroll](answer_revision_audit.v2.json).
`analyze_answer_revision_continuation_v1.py` beregner summene direkte fra råposter
og kontrollerer dem mot resultatfilen; `audit_answer_revision_continuation_v1.py`
kontrollerer bindingene uten modellkall. Nye kontrollsnapshots versjoneres.

Ingen gratis tilbakestilling, betalt API, lokal produktinferens, holdout,
produksjonsendring, commit/push eller M3-arbeid er utført. Engangsautomasjonen er
slettet. **Vurderingsoppgaven er fullført; M2-06s kvalitetsgodkjenning er fortsatt åpen.**
