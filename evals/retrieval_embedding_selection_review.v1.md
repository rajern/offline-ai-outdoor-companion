# MiniLM anbefales til fase B, med kjente sikkerhetsmangler

Gjennomgang 9. oktober 2026, basert på fase A ved commit `0e09750`.
**Anbefaling: velg MiniLM som forsøksmodell til fase B.** Den har best samlet
dekning og lavest målt ressursbruk, og Gemma har egne store sikkerhetstap.
MiniLMs baseline er likevel utilstrekkelig: særlig pustovervåking i case 08 og
anafylaksi i case 17 har mangler som de frosne B/C-reglene ikke kan løse fullt.
Dette må inngå i eierens modellbeslutning; anbefalingen godkjenner ikke et
produksjonsoppsett eller en endelig vinner.

## 1. Case 13: Gemma har samme risiko som MiniLM

Alle tre leverer **0/2 nødpeilerkrav**. MiniLM og Gemma har seks identiske
passasjer. Fire av dem gir en generell instruks om straks å ringe 113 når
tilstanden er eller kan bli farlig:

| Passasje | MiniLM-blokk | Gemma-blokk |
|---|---:|---:|
| `source-01-027` | 1 | 2 |
| `source-04-009` | 2 | 4 |
| `source-03-008` | 3 | 3 |
| `source-08-010` | 5 | 6 |

De øvrige felles passasjene er `source-07-002` (egen sikkerhet, telefonhjelp)
og `source-05-007` (generell tidskritikalitet). MiniLM tilfører sideleie/
pustovervåking og planlegging av elvekryssing; Gemma tilfører isredning og HLR.
Ingen av forskjellene gir en nødpeilerinstruks eller kvalifiserer de fire
generelle telefonanvisningene med hva man gjør uten dekning.

**Min kildebaserte vurdering er potensielt misvisende hos begge.** Brukeren
beskriver livsfare og manglende dekning. De generelle, handlingsrettede
telefonanvisningene kan prioritere forsøk på en kontaktvei som situasjonen
utelukker, og dermed forsinke nødpeileren. Dette er en konkret mulig feil
handling, ikke bare fravær av nødpeilerinformasjon. Artikkeltitlene handler om
ulike medisinske tilstander, men selve anvisningen er generell og gjelder
den beskrevne farlige tilstanden. Gjentakelsen alene begrunner ikke flagget.

Dette er **ingen direkte konflikt**: teksten sier verken at nødpeileren skal
unngås eller at varsling skal utsettes. Råd om å vente når fysisk hjelpeinnsats
er farlig gjelder egen sikkerhet, ikke utsatt varsling. Tydelig avgrensede råd
om elvekryssing, isredning, HLR og sideleie er primært irrelevant informasjon.
Qwens snøskredråd om søk før varsling er også eksplisitt avgrenset til en annen
hendelse og gir ikke i seg selv et misvisende-flagg i denne fallulykken.

Forskjellig rekkefølge er dokumentert, men dens effekt er **ukjent**. Én lagret
vurdering per kontekst kan ikke skille plasseringseffekt fra dommervariasjon.
Gemmas fravær av flagg gir ikke dokumentert sikkerhetsfordel her. Faktisk feil
handling i et generert svar er ikke målt.

Jeg foreslår separat adjudikasjon av **A-gemma2/case-13: potensielt misvisende =
ja**, med de samme fire passasjene. MiniLMs flagg og alle modellene sine
0/2-vurderinger beholdes. Forslaget er **ikke anvendt**; råresultatene er urørt.

## 2. Alle 11 tap mot Gemma, og de fire mot Qwen

Kravnummer refererer til den uendrede utviklingsfasiten. Rangene gjelder
MiniLMs eksisterende vektorer etter samme geografifilter. Ingen av de seks
casene nedenfor forkastet en topp-8-pakke av hensyn til tokenbudsjettet.
Tap av en passasje skyldes dermed utvalget/rangeringen, mens case 20 også
viser en tolkningsforskjell.

| Case/krav | Hva Gemma leverer som MiniLM mangler | Sikkerhetsbetydning og dokumentert årsak | Mulighet innen avtalt B/C |
|---|---|---|---|
| 01/1 | Manglende belastningsevne gir bruddmistanke: `source-04-005`, Gemma-blokk 3. | Risiko for å behandle mulig brudd som forstuing. Passasjen har MiniLM-rang **20**, uten embedding-avkorting. | k≤16/P2 henter den ikke. **P1** kan inkludere den via `source-04-006` på rang 6; budsjett må fortsatt bestås. **P3 gjør ikke denne utvidelsen.** |
| 01/2 | Vanskelig å skille brudd fra forstuing: samme passasje. | Understøtter nødvendig usikkerhet. Samme rangeringstap; omtale av begge skadetyper alene er utilstrekkelig. | Samme P1-mulighet som 01/1. |
| 01/3 | Lege/legevakt ved bruddmistanke: samme passasje. | Viktig eskalering. MiniLMs 113-råd gjelder nakke/rygg/hofte og erstatter ikke ankelkravet. | Samme P1-mulighet som 01/1. |
| 03/3 | Fosskoking av klart vann i ett minutt ved høyde ≤6 500 fot: `source-21-010`, Gemma-blokk 8. | Nødvendig behandlingsprosedyre. MiniLM-rang **11**, ingen avkorting. Generelt kokeråd mangler tid/høyde. | k12/16 kan tilby passasjen; ingen leveringsgaranti. P1 kan hente den via desinfiseringsgrenen på rang 5, men pakken er seks passasjer. |
| 03/4 | Fosskoking i tre minutter over 6 500 fot: samme passasje. | Kritisk høydeforbehold når høyden er ukjent. Samme årsak. | Samme mulighet og budsjettforbehold som 03/3. |
| 03/5 | Koking/desinfisering løser ikke skadelige kjemikalier/giftstoffer; velg annen vannkilde: `source-21-009`, Gemma-blokk 6. | Hindrer feil trygghetsantakelse. MiniLM-rang **13**; én embedding-visning er litt avkortet, den rene tekstvisningen er komplett. | k16 kan tilby den. P1 har samme seks-passasjers gren; P3 utvider ikke grenen. |
| 08/2 | Voksen luftveisteknikk + se/lytte/føle i ≤10 sekunder: `source-01-006` og `source-07-005`, Gemma-blokk 6/3, Qwen-blokk 8/4. | Akutt førstehjelp. MiniLM leverer barne-/baby- og hypotermiprosedyrer, men ikke alle anvendelige komponenter. Alternativ full voksenpustesjekk `source-01-004` ligger på rang **9**. | k12/16 kan tilby den komplette voksenpustesjekken. `source-01-004` avkortes bare i tittel-/seksjonsvisningen, ikke i ren tekst. |
| 08/4 | Vedvarende pustovervåking, HLR ved ingen/unormal pust og 113 ved usikkerhet: `source-07-005`, Gemma-blokk 3, Qwen-blokk 4. | **Akutt og vesentlig tap.** MiniLM-rang **25**; begge embedding-visninger avkorter HLR-/overvåkingsdelen. | k≤16 henter ikke denne passasjen. P1/P3 kan tilføre overvåking fra sideleiegrenen, men **ikke hele kravet**: den manglende pust/HLR/113-beslutningspassasjen nås ikke gjennom de frosne grenreglene. |
| 17/1 | Rask anafylaksi med hud-/slimhinnehevelse, trang hals/pustebesvær og insektutløser: `source-08-004`, Gemma-blokk 2. | **Akutt og vesentlig tap.** MiniLM-rang **34**. Begge embedding-visninger mister selve hevelses-/halssymptomene ved avkorting. | Ingen passende topp-16-gren gir symptompassasjen i P1/P3. De planlagte justeringene løser ikke dette dokumenterte tapet. Gemma mangler fortsatt **17/2: akutt behandling og umiddelbar 113**. |
| 20/1 | Gemma har eksplisitt rute-/ferdighetskontroll i `source-10-002`, blokk 8; MiniLM-rang **10**. Qwen siterer i stedet `source-16-002`, blokk 1, identisk med MiniLM-blokk 3. | Forebyggende sikkerhet. Gemmas tydeligere primærbevis er et rangeringstap; **Qwens gevinst er ikke et tap av den siterte teksten**. Dommerens semantiske vurdering varierer. | k12/16 kan tilby det eksplisitte primærbeviset, uten avkorting. Se separat adjudikasjonsforslag nedenfor. |
| 21/2 | Følg produktets bruksanvisning: `source-21-009`, Gemma/Qwen-blokk 4; MiniLM-rang **13**. | Viktig produktforbehold. **MiniLM leverer allerede filtrer først, desinfiser etterpå.** Det er ikke omvendt eller manglende rekkefølge. Produktinstruksen er bevart i begge embedding-visninger. | k16 kan tilby passasjen. P1 kan hente den i seks-passasjers gren fra filtertreffet på rang 1; P3 gjør ikke denne grenutvidelsen. |

Qwens fire registrerte gevinster er **08/2, 08/4, 20/1 og 21/2**. De tre
førstehjelps-/vannkravene har reelt bedre levert kildegrunnlag. I 20/1
leverer Qwen ingen annen passasje som fullfører den siterte ferdighetsvurderingen.
Den felles teksten ber leseren undersøke terrenget og vurdere turens
gjennomførbarhet mot gruppens evner. Jeg vurderer dette som semantisk dekning
av rute-/ferdighetskontroll, uten krav om identisk ordlyd. **Separat forslag:
A-minilm/case-20/krav 1 → covered**, med disse konkrete tekstspennene.
Forslaget er ikke anvendt; den registrerte 11/4-tapsoversikten beholdes.

**Avkorting er en dokumentert eksponering, ikke en bevist årsak til rangeringen.**
Ingen kontrafaktisk embeddingkjøring er gjort. Kilden leveres alltid hel dersom
den først velges. Brudd-, koke- og planleggingspassasjene uten avkortet
primærbevis viser at avkorting ikke alene forklarer tapene. Threshold kan
filtrere bort treff og eventuelt frigjøre plass, men **kan ikke flytte et treff
fra rang 20/25/34 inn i topp 16**. Større k kan også fylle budsjettet med støy.

## 3. Samlet modellvurdering

| Modell | Uendrede fase A-resultater | Modellvekter / målt maksimal RSS |
|---|---|---|
| MiniLM | 56/72; macro 75,7 %; 14/22 komplette | 235 MB / 0,915 GB |
| Gemma 2 | 51/72; macro 74,1 %; 13/22 komplette | 1 489 MB / 2,017 GB |
| Qwen Q4 | 37/72; macro 54,9 %; 10/22 komplette | 396 MB / 1,778 GB |

Gemmas gevinst på akutt førstehjelp er reell, særlig case 08. Men byttet mister
16 krav MiniLM dekker, inkludert **hele case 04 (bortkommen i tåke, fem krav)**
og **case 05 (tordenvær/klippeoverheng, seks krav)**. Viktige bevis ligger på
Gemma-rang 29 (`source-09-007`) og 108/66 (`source-22-002`/`source-22-004`).
Ingen kilde fra disse dokumentene finnes blant Gemmas topp 16 i de respektive
casene, så P1/P3 kan heller ikke hente dem. Gemma gir dermed ikke en
dokumentert generell sikkerhetsforbedring innen dette forsøksrommet, og er
ikke en løsning på det felles tapet av akutt varsling ved anafylaksi.

MiniLM kombinerer bedre bredde med omtrent halvparten av Gemmas målte RSS og
en sjettedel av modellfilstørrelsen. Baseline har også færre
budsjettforkastelser: 2 mot Gemmas 7 og Qwens 9, over alle 25 spørsmål.
Indekstrinnene tok 5,84/70,11/130,95 sekunder, men **MiniLM gjenbrukte
dokumentvektorene**, mens de andre beregnet dem. Dette er ikke en sammenlignbar
full indeks- eller live-latensbenchmark. Rangering med cachede spørsmålsvektorer
er rask hos alle; mobil og samtidig drift med svarmodellen er ikke målt.

**MiniLM er derfor beste praktiske forsøkskandidat**, mens Gemma er et reelt
alternativ dersom eieren vil prioritere den eksisterende, komplette
pustebeslutningen høyere enn tordenvær/orientering og ressursbruk. Qwen gir
ingen særskilt dokumentert sikkerhetsgevinst over Gemma i de fire undersøkte
kravene, og svakere samlet dekning gir ikke grunn til å prioritere den.

Jeg forventer ikke at B/C automatisk gjør MiniLM tilstrekkelig. Fasene kan
avklare vannbehandling, voksenpustesjekk, nødpeiler og P1s bruddutvidelse, men
de dokumenterte begrensningene for 08/4 og 17 må følge en eventuell finalist.
Å løse dem med endret embedding, bredere packing eller annen retrieval ville
kreve et separat oppdrag, og inngår ikke som skjult tillegg her.

## 4. Krav som skal følges i B/C

- **01/1–3:** bruddmistanke, usikkerhet og legekontakt; behold 01/4 ro/avlastning.
- **03/1–5 og 21/1–2:** begge høydebetingelser, kjemisk begrensning,
  virusbegrensning, riktig rekkefølge og produktinstruks som separate delkrav.
- **08/1–4:** full voksenpustesjekk, korrekt sideleie, oppringning **og**
  veiledning, samt den fortsatt manglende pust/HLR-beslutningen.
- **17/1–2 og 13/1–2:** anafylaksisymptomer **og** umiddelbar eskalering;
  nødpeiler ved livsfare/tvil. 17/2 og begge nødpeilerkrav mangler hos alle tre.
- **20/1–2:** rute-/ferdighetskontroll og værtilpasning; følg den dokumenterte
  tolkningsforskjellen, uten å kalibrere dommeren underveis.
- **Bevar MiniLMs sikkerhetsgevinster:** alle krav i 04/05, samt 10/1, 19/2
  og 23/2–3. Følg også de felles udekkede 06/1 og 06/4. Alle 25 caser scores
  fortsatt; listen begrenser ikke evalueringen til favorittcaser.

## 5. Beslutninger og sporbarhet

Eieren må velge forsøksmodell og ta stilling til de to
[foreslåtte adjudikasjonene](retrieval_embedding_selection_adjudication.proposed.v1.json).
Ingen av dem er skrevet inn i den aktive adjudikasjonsfilen, scoren, cachen
eller frysemanifestet. Ingen ny scoregrense eller gold-endring er foreslått.
Det opprinnelige 15-settet og historiske resultater forblir uendret.

[Evidensoversikten](retrieval_embedding_selection_review.v1.json) har alle 11
krav, de fire Qwen-gevinstenes bevis, blokknumre, kilde-ID/URL, tekst- og
konteksthashes, lagrede ranglister, tokenizerkontroll og strukturelle grenregler.
Full tekst finnes lokalt i
`knowledge/local/diagnostics/retrieval-optimization-v1-2026-10-08/experiment/configurations/A-{modell}/case-XX/`
og dommercachen angitt med `cache_key`. Analyse og kildebærende avkortingsspenn
er lagret under samme diagnostikkatalogs `source-review/`; offentlig rapport
inneholder ingen kopiert kildetekst. Rang over 16 er beregnet med de eksisterende
vektorene, og topp-16-rekkefølgen er kontrollert mot de lagrede resultatene.
Grenanalyse beskriver mulig kildetilgang **før** budsjett/threshold, ikke nye
leverte kontekster eller nye testresultater.

**Stoppunkt:** kun gjennomgang er utført. 0 nye dommer-/embeddingkall,
0 nye retrieval-konfigurasjoner. Fase A er ikke gjentatt, B/C er ikke startet,
holdout er ikke åpnet, og produksjonskode/-konfigurasjon er uendret.
