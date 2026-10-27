# Låst vurdering og oppdatert retrieval-score

25. oktober 2026. **Punkt 1 og 2 er fullført.** Den eksisterende nye rubrikken og
Sol Medium er låst for videre utvikling. De 25 lagrede primærkontekstene er vurdert
på nytt, etter tre beståtte kontroller av vurderingslogikken. Ingen nye søk eller
produktsvar er kjørt. Gamle vurderinger er bevart; produksjon og M3 er uendret.

## Hovedresultatet

| Måling | Resultat |
|---|---:|
| Fullt levert av retrieval, ny obligatorisk kjerne | **55/63 = 87,3 %** |
| Delvis levert | 4/63 |
| Fraværende | 4/63 |
| Usikre kriterielabeler fra dommeren | 0/63 |
| Støttede spørsmål med alle kjernekrav levert | 16/22 |
| Gjennomsnittlig bekreftet dekning per støttet spørsmål | 84,8 % |
| Betinget greninformasjon, utenfor hovednevner | 3 fullt tilgjengelige, 1 fraværende |

Dette gjelder de samme faktiske utdragene som den gamle 83,3 %-målingen bygget på:
forsøksoppsettet MiniLM T-ranking, k16, uten threshold, P3. Det er ikke en ny
måling av nåværende produksjons-/UI-oppsett eller en forbedring av selve søket.
Tre deklarerte kunnskapshull holdes utenfor 63-nevneren. Case 14 har 1/2 av sitt
støttede delsett levert; tomme kravlister i case 15/25 gir ingen automatisk suksess.

## Hva modellen bevarer av informasjonen den faktisk fikk

Retrieval og de allerede lagrede Medium-vurderingene er koblet sammen per
kriterie-ID. Bevaring betyr:

> Antall krav som er fullt dekket både i de leverte kildene og i svaret,
> delt på antall krav som er fullt dekket i de leverte kildene.

For den **historiske 25-kjøringen** fant søket 55 krav. Svaret gjenga 13 av dem
fullstendig: **13/55 = 23,6 % bevaring**. Samlet svardekning er fortsatt 13/63
(20,6 %) i den låste rå Medium-vurderingen. Alle 13 ligger i den fullt leverte
kjerneinformasjonen; ingen ekstra fullstendig dekket svarpåstand må her tilskrives
informasjon utenfor de fullt dekkede kildekravene.

For de samme åtte screening-spørsmålene, hvor seks har definerte kjernekrav:

| Lagret oppsett | Tilgjengelig fra søket | Fullt dekket i svaret | Bevaring av tilgjengelige krav |
|---|---:|---:|---:|
| Historisk Qwen 2B, samme delutvalg | 13/15 | 4/15 | 4/13 = 30,8 % |
| Nyere Qwen 2B-oppsett | 13/15 | 8/15 | 8/13 = 61,5 % |
| Gemma | 13/15 | 6/15 | 6/13 = 46,2 % |

De to kunnskapshullene vurderes separat, uten bevaringsprosent. Nyere Qwen/Gemma
har ikke nye svar på hele 25-settet. Tabellen kan ikke erstatte en slik vurdering.
De tre tidligere diagnostiske kontekstene er heller ikke vurdert på nytt her.

**Bevaring er ikke samlet kvalitet eller sikkerhet.** Nyere Qwen får mer
kjernedekning, men har fortsatt mange udokumenterte tillegg. Et korrekt varslingsråd
kan få full dekning sammen med feil situasjonsforklaring og ubegrunnet behandling.
De tidligere funnene om blant annet manglende pustevurdering står ved lag.

## Hvorfor 87,3 % er forskjellig fra 83,3 %

Ingen kilder, spørsmål, rangering eller kontekstpakking er endret.

| Trinn i definisjonsendringen | Full dekning |
|---|---:|
| Historisk retrieval-vurdering, 72 krav | 60/72 |
| Bare de 63 beholdte obligatoriske kravene, gamle vurderinger | 54/63 |
| Ny vurdering mot de reviderte formuleringene | 55/63 |

Ni tidligere krav er nå betingede eller valgfrie; seks av disse ni hadde tidligere
full retrieval-dekning. Det eneste beholdte kravet som skifter fra manglende til
full dekning, er akutt varsling i case 17. Den nye formuleringen kan støttes av
levert generell 113-veiledning ved pustevansker/tidskritisk tilstand. Dette betyr
ikke at en stikkspesifikk anafylaksiprosedyre er hentet; den finnes ikke i pakken.

Økningen i prosent kommer dermed fra vurderingsdefinisjonen, ikke en teknisk
retrieval-forbedring. Gammel 60/72 og alle historiske råfunn er uendret.

## De åtte kjernekravene som ikke er fullt levert

| Spørsmål | Manglende eller delvis kildeinformasjon |
|---|---|
|01, ankelskade | Koblingen mellom manglende belastningsevne og mulig brudd mangler. Lege-/legevaktvurdering ved mulig brudd er bare delvis levert. |
|03, bekkevann | Begge høydeavhengige koketidskrav mangler. Generell beskjed om behandling finnes. |
|06, stor blødning | Initial varsling for den beskrevne store ytre blødningen mangler. Varsling ved forverring/indre blødning er andre betingelser. |
|08, bevisstløshet | Videre pustovervåking finnes, men koblingen mellom ingen/unormal pust og HLR-oppstart mangler. Selve pustesjekken er fullt levert. |
|13, nødpeiler | Nødpeileren beskrives som aktiverbar i nødsituasjoner, men klar straks-aktivering fremfor venting er bare delvis levert. |
|21, vannfilter/tabletter | Riktig rekkefølge finnes; instruks om produktets bruksanvisning mangler. |

Dette er konkrete hull i disse lagrede pakkene, ikke et utsagn om at informasjonen
aldri finnes i hele kunnskapsbasen. Ingen ny datainnhenting eller feilsøking av
søkeparametere er utført i denne oppgaven.

## Hva som er låst og kontrollert

[Låsedokumentet](evaluation_lock.v1.md) binder uendret `answer_rubric.v1.json`
til `gpt-6.1-sol`, forespurt `medium`. 63 obligatoriske krav brukes på begge sider.
Fire betingede grener inventeres separat uten å avhenge av et fremtidig LLM-svar;
fem valgfrie krav kompenserer ikke for mangler. Ingen ny beståttgrense er innført.
Det gamle 54/60-utviklingsmålet omregnes ikke automatisk til et nytt mål.

Den nye [retrieval-instruksen](retrieval_rubric_judge.v1.md) vurderer faktisk
kildeforekomst, med meningsmessig likeverdighet, bevarte betingelser og kildebevis
for alle nødvendige komponenter. Dommeren ser ikke gamle scorer, modellnavn,
genererte svar eller den gamle kravlisten. Spørsmålet kan avklare referanser,
men gir ikke i seg selv bevis for råd som mangler fra kildene.

Før hovedkjøringen besto tre kontroller med sju kriterier: komplett/flerspanns
dekning, ett gyldig alternativ, delvis dekning, fravær, bred instruks som dekker
oppgitt eksempel, feil scenario og full dekning sammen med motstridende tilleggs-
informasjon. Dette er små forfatterkontroller, ikke en uavhengig fasit eller
statistisk kalibrering av alle spørsmål.

Alle 69 ordinære kriteriebeslutninger (63 kjerne, 4 betingede, 2 gap-delkrav)
og 25 funnlister er gjennomgått. Positive sitater er kontrollert mot kravets mening;
manglende/delvise krav er kontrollert mot leverte kilder. Ingen råscore er endret.

## Støy, risikofunn og usikkerhet

Dommeren finner irrelevant stoff i alle 25 pakker. Det sier ikke hvor stor andel
av teksten som er støy. Alle pakkene kan inneholde både nyttig og irrelevant tekst.

To pakker får rått `potentially_misleading`-flagg: 08 og 13. Gjennomgangen beholder
disse som **uavklart anvendelse**, ikke påviste kliniske feil. I 08 viser sammendraget
til operatørhjelp, og riktig pustevilkår finnes et annet sted i pakken. I 13 kan
telefonrådet avlede fra nødpeiler, men teksten sier ikke at telefon er eneste valg,
og kildene avgjør ikke alle muligheter for nødanrop. Funn og kildebevis er bevart.

Kremuklarheten i en brannskadekilde er registrert som egen kildebegrensning i 07
og som irrelevant kildeuklarhet i 15, uten å avgjøre medisinsk riktig krembruk.
Ingen direkte motstrid eller geografisk lekkasje ble merket av dommeren. Det er
ikke bevis på fravær av alle slike problemer.

Null `uncertain`-labeler i kjerneopptellingen er heller ikke null måleusikkerhet.
Samme arbeidsagent som kjenner dataene har gjennomgått funnene; dette er ingen
uavhengig klinisk validering. De gjentatte utviklingsspørsmålene er ikke et nytt,
representativt testsett, og holdout er ikke åpnet.

Tidligere svarvurderingers forbehold følger med bevaringsberegningen. Særlig har
den historiske LLM-vurderingen et kjent konteksttolkningspunkt i case 24 som kan
flytte ett krav ved egen adjudikasjon. Her brukes de forseglede rå Medium-scorene;
ingen delvis korrigert modelltoppliste presenteres. Case24 er ikke i screeningsettet.

## Teknisk gjennomføring og regnskap

28 sekvensielle abonnementskall: tre kontroller, deretter 25 primærkontekster.
Ingen mislykkede modellkall, automatisk gjenkjøring, kvotestopp eller ressursbrudd.
Eksakt stdin, instruks, skjema, kommando, kildehashverdier, rålogger, tidsbruk og
tokenbruk er lagret privat. Samme CLI-binær som i forrige parvise vurdering er
brukt: `0.164.0-alpha.11.1`. Faktisk serverrevisjon/resonneringsnivå kan ikke
bekreftes uavhengig av forespørselsinnstillingen.

Kjent bruk: 223 119 inputtoken og 27 495 outputtoken, totalt 250 614. De 4 569
resonneringstoken inngår i output og legges ikke til igjen. 11 520 av inputtoken
er registrert som bufret. Vurderingskallene tok samlet 597,0 sekunder, med median
20,9 sekunder. Ingen betalt API eller gratis tilbakestilling er brukt.

Den første offline summeringen stoppet fordi en Windows-bakstrek gjorde at den
uttrykkelig tillatte oppdateringen av evals/AGENTS.md ble behandlet som endring av
en uforanderlig fil. Ingen score var skrevet av den summeringen. Et
[separat kontrolltillegg](retrieval_rescore_progress_path_adapter.v1.md) bevarer
original kode/frys og normaliserer bare identiteten til de to allerede tillatte
statusfilene. 485 historiske filer bekreftes uendret på opprinnelig plass; originale
TASKS.md og evals/AGENTS.md er i tillegg bevart byteidentisk som før-snapshots.
Ingen modellkall eller data ble endret eller gjentatt for rettingen.

Seks atferdstester består. Den uavhengige offline kontrollen bekrefter 28 komplette
råsvar, eksakt serialisert stdin, korrekte kriterie-IDer, sitatforekomst, ressurs-
grenser og uendret M3. Summeringen er beregnet separat, og koblingen til 34 støttede
primærsvar er kontrollert direkte mot private forseglede svarposter. Sitatforekomst
alene beviser ikke at dommeren har tolket teksten riktig; derfor følger gjennomgangen.

## Etterprøving og videre arbeid

- [Resultater og kravvis bevaring](retrieval_rubric_rescore_results.v1.json)
- [Gjennomgang og bro mellom gamle/nye krav](retrieval_rubric_rescore_review.v1.json)
- [Offline integritetskontroll](retrieval_rubric_rescore_audit.v1.json)
- [Frosset protokoll](retrieval_rubric_rescore_protocol.v1.md)

Private input/rålogger ligger i
`knowledge/local/diagnostics/retrieval-rubric-locked-v1-2026-10-25/`.
Bruk `retrieval_rescore_progress_path_adapter_v1.py check` for kontroll uten
inferens. Adapterens `summarize`/`audit` lager nye versjonerte snapshots uten
modellkall. Den opprinnelige kjørekommandoen skal ikke brukes til nye forsøk.

Tallene underbygger videre fokus på å bevare levert informasjon i svarene.
Kontekststøy og de åtte ufullstendige kravene er kjente forbehold. Denne oppgaven
starter ikke lokal forbedringsrunde, GPT-svargenerering, produksjonsintegrering,
sikkerhetspolicy eller M3. M2-06s kvalitetsgodkjenning er fortsatt åpen.
