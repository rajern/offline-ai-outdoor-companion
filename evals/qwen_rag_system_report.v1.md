# M2-06: lokal Qwen/RAG-systemtest, 2026-10-11

**Konklusjon:** Den lokale kjeden fungerer teknisk, men svarene er ikke klare for
M2-06-kvalitetsgodkjenning. Retrieval-kandidaten leverer 60/72 krav; Qwen utelater
mange leverte opplysninger, blander situasjoner og endrer kritiske betingelser.
Tre diagnostiske tester med tilstrekkelige kilder viser at mer relevant kontekst
alene ikke løser pust/HLR- og anafylaksifeilene. Prioriter generering og
kildeetterlevelse før mer retrieval-optimalisering. M2-06 er fortsatt åpen; M3
og produksjonskonfigurasjonen er uendret.

## Gjennomføring og sporbarhet

Én baseline på de samme 25 utviklingsspørsmålene er fullført gjennom faktisk
FastAPI `/api/chat`, Orchestrator, ModelService og lokal llama.cpp. MiniLM var
lastet samtidig med Qwen. Ferske søkeembedding/rangering/P3-kontekster ble
kontrollert mot lagrede T-ranking-input: alle 25 ga nøyaktig samme prompt.
Ingen retrieval-varianter ble lagt til; T-combined er fortsatt ikke vurdert.

Frosset kandidat: MiniLM full-body window T-ranking, k16, ingen threshold,
opprinnelig P3, høyst 2 000 tokens for komplett grounded prompt. Uendret Qwen3.5-2B
Q4_K_M: 4 096 runtime-kontekst, 256 outputtokens, temperatur 0,2, top-p 0,8,
top-k 20, reasoning off, 120 sekunders timeout. Runtime: build 11193,
commit `4e7481175`. Modellfil: 1 396 198 496 bytes, SHA-256
`57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8`.

Vurderingsmetoden ble frosset før første Qwen-svar i
`qwen_rag_system_protocol.v1.md`. Hvert krav vurderes full/partial/absent/uncertain
i selve svaret; alle delhandlinger og betingelser må være med for full dekning.
Kildeetterlevelse, relevans, konkret feilhandlingsrisiko og språk vurderes separat.
Dette er én agents kildebaserte gjennomgang, ikke en ny uavhengig dommervalidering
eller medisinsk/juridisk faglig godkjenning. Ingen ny akseptgrense er innført.
Innholdsdekning er ikke en sikkerhetsscore; et dekket krav kan stå ved siden av
farlige tillegg. Historiske retrieval-scorer er uendret.

Rådata og forseglede stdout/stderr/kommandoer/svar ligger lokalt under
`knowledge/local/diagnostics/qwen-rag-system-v1-2026-10-11/revision-02/`.
`qwen_rag_system_results.v1.json` binder hver vurdering til eksakt svarhash,
prompt/context/cacheidentitet, leverte passasje-IDer og lokale råfiler.
`qwen_rag_answer_review.v1.json` forklarer vurderingene per case;
`qwen_rag_system_audit.v1.json` dokumenterer kontrollene. Kildetekst, modell og
råkontekster er ikke lagt i Git.

## Baseline-resultater

| Grunnlag | Leverte krav, retrieval | Fullstendige krav i svar | Macro svardekning | Komplette svar |
|---|---:|---:|---:|---:|
| Hele 25-settet, 22 støttede caser | 60/72 (83,33 %) | 15/72 (20,83 %) | 23,33 % | 0/22 |
| Opprinnelige 15, 13 støttede caser | 42/51 (82,35 %) | 7/51 (13,73 %) | 13,85 % | 0/13 |

Svarresultatene bruker den separate agentgjennomgangen og skal ikke fremstilles
som om den historiske retrieval-dommeren også vurderte svarene. Små semantiske
grensedragninger påvirker antallet fullstendige krav; hovedfunnet er de konkrete
feilene nedenfor. Delvis dekning gir ingen fulle poeng. De tre kunnskapshullene
inngår ikke i komplett-pass eller dekningsaggregatene.

| Case | Fullstendige krav i svar | Viktigste funn |
|---|---:|---|
| 01 | 0/4 | Råd om ro nyttig; frakturgrunnlag mangler, 20 minutter blir uriktig kontaktgrense |
| 02 | 2/5 | Vått tøy/overvåking med; vind-/damptetthet, trygg varmetilførsel og veiledning mangler |
| 03 | 1/5 | Flomrydding tar plassen til vannbehandling; filter alene fremstilles som nok |
| 04 | 1/5 | Nødpeiler/hjelp nyttig; tåke/navigasjon blir skredredning |
| 05 | 0/6 | Lyn blir snøskred; foreslår feil slags «sikker» plass ute |
| 06 | 0/4 | Press delvis med; feil 113-betingelser og ufullstendig bandasje/overvåking |
| 07 | 0/4 | Kjøling delvis riktig; blemmer og lege ved håndskade utelatt |
| 08 | 0/4 | HLR uten pustebetingelse; normalt-pustende sideleiegren utelatt |
| 09 | 1/3 | Drikke nevnt, men varmt isolerende tøy anbefales i varmeforebygging |
| 10 | 0/3 | Oppfunnet trekasse; sovepose/nødly erstattes av ispasientråd |
| 11 | 1/3 | Dybde/avstand nyttig; avfall skal «renne» nedstrøms, håndhygiene ufullstendig |
| 12 | 1/3 | Avviser brun elv; vent/snu og hele sikkerhetsbetingelsen ufullstendig |
| 13 | 0/2 | Anbefaler 113 fordi mobildekning mangler; nødpeiler ikke besvart |
| 14 | 0/2 støttet del, kunnskapshull | Isredning og skredsøk; ingen erkjennelse av manglende utgangsråd |
| 15 | Kunnskapshull | Nevner manglende dekning, men gir også ubegrunnede regel-/vannpåstander |
| 16 | 1/2 | Rensing/bandasje nyttig; 113 brukes ved usikker sårdybde |
| 17 | 0/2 | Venteråd ved halshevelse; anafylaksi ikke håndtert |
| 18 | 2/3 | Hodet over vann/solid iskanten nyttig; selve opptrekksmetoden ufullstendig |
| 19 | 0/2 | Personlig fullt utstyr og øving uklart; irrelevant isredning |
| 20 | 1/2 | Rute/gruppeferdigheter semantisk med; vær og planendring utelatt |
| 21 | 1/2 | Filterets begrensning riktig; desinfisering/virus og rekkefølge blir feil |
| 22 | 1/3 | Offlinekart nyttig; papirreserve legges i telefonen, batteri utelatt |
| 23 | 1/3 | Elektriske apparater nevnt; 30-minutters ventetid utelatt |
| 24 | 1/2 | Stor vannføring korrekt; skråningsråd erstattes av bil/båt |
| 25 | Kunnskapshull | Oppfunnet lybygging med 24-timers venting; ingen avståelse |

Flere svar har nyttige, kildebelagte deler: case18 om solid iskanten, case21 om
filterets virusbegrensning og case24 om stor vannføring. Ingen baseline-svar
dekker alle krav. Disse delene skal derfor ikke presenteres som gode helhetssvar.

Overlappende svarflagg: 18/25 med udokumenterte eller feil anvendte tillegg,
19/25 med irrelevant råd, 16/25 med konkret potensielt misvisende råd og 9/25
med direkte konflikt. Original15: henholdsvis 12,12,11,6. Ingen sikker
feil-country-instruksjon er registrert; case22 har likevel en viktig geografisk
promptfeil. Tre svar/caser trenger særskilt review (07,16,18). Flaggtallene er
agentvurderinger med dokumentert begrunnelse, ikke validerte sikkerhetsestimater.

## Feilårsak og diagnostikk

Retrieval mangler fortsatt 12 komplette krav: 01/1–3,03/3–4,06/1,08/4,13/1–2,
17/1–2 og21/2. Viktige komponenter kan likevel være levert i et ufullstendig
krav: case21 mangler produktanvisningen, men korrekt filtrer-først-rekkefølge og
desinfisering mot virus står faktisk i source-21-012. Qwens reversering er dermed
en genereringsfeil, ikke bare retrieval-tap. Tilsvarende er sideleie ved normal
pust levert i case08, og generelle tidskritiske 113-kriterier i case17.

Generering mister også tydelig informasjon ved full retrieval: alle lynkrav i05,
vesentlige hypotermi-/brannskadehandlinger i02/07, varmeforebygging09,
utstyr/praksis19 og ventetiden23. Case01 omformer en kjølevarighet til et
legekontaktvilkår. Dette kan ikke forklares med manglende kilder alene.

Tre separate diagnostiske svar brukte manuelt kontrollert tilstrekkelig kontekst
fra samme korpus, samme spørsmål/prompt/settings og samme ressursgrenser:

| Case | Kontrollerte passasjer | Observasjon |
|---|---|---|
| 03 | source-21-005/009/010 | Vannspesifikt svar og ett/tre minutter, men høydegrensen og kjemikalieadvarselen fortsatt mangler |
| 08 | source-07-001/005/006/007,source-01-004 | Sideleie/overvåking mangler fortsatt; 10 sekunder knyttes feilaktig til HLR |
| 17 | source-08-001/003/004 | Alvorlige raske symptomer gjenkjennes, men «113 øyeblikkelig» kombineres med venting til nedstigning |

Ingen diagnostisk svar dekker alle krav. Kortere og renere kontekst endrer både
støy, lengde og plassering; tre enkeltsvar isolerer ikke disse effektene eller
samplingsvariasjon. De er ikke nye retrieval-konfigurasjoner og inngår ikke i
baseline-aggregatene. Ingen ekstra prompt- eller modellvariant ble testet.

De tre kunnskapshullene er bevart: detaljert skredutgang14, norske bålregler15,
greinlybygging25. Bare15 erkjenner eksplisitt manglende dekning, og samtidig gir
den ubegrunnet råd. Dermed ingen ren, trygg avståelse blant de tre. Ingen nye
kilder eller oppdiktede gold-krav er lagt til.

Trepunktinstruksen kan fortrenge viktige handlinger: case03 bruker to punkter på
flom, case24 på bil/båt. Det beviser ikke at større tokenramme alene hjelper.
Synlige svar var 69–227 låste tokens; ingen dokumentert 256-token-avkorting.
Runtime rapporterer ikke faktisk stoppreason/tokenregnskap. Dårlig norsk,
feil situasjon og betingelsesendringer forekommer også i korte svar.

Case16 er kildebasert gjennomgått mot V3 i
`qwen_rag_system_case16_review.v1.json`. Den opprinnelige scope-/pressuenigheten
er fortsatt eksakt kontekstbundet `requires_review`. Den nye Qwen-feilen om
113/sårdybde vurderes separat og endrer ingen retrieval-scorer. Case07 har en
eksisterende uklar kremregel i samme passasje; case18 en uklar kvalifikasjon av
skistaver som redningsutstyr. Disse må håndteres eksplisitt i kvalitetsreview.

## App, avståelse og offline

Normal app bruker fremdeles opprinnelig mean-index, k3, threshold0,35,
jurisdiksjonNO og ingen P3/tokenbudsjett-packing. Kandidaten ble injisert bare i
testappen. API-kilder/metadata samsvarte med faktisk levert tekst i alle25:
utgiver, URL, lisens, eier, lisenslenke, datoer og støttede gjenbruksmerknader.
Frontend-koden viser disse feltene; interaktiv UI-gjennomgang er ikke utført.
Kildelisten viser alle leverte dokumenter, og beviser ikke at Qwens påstander
er støttet eller at modellen brukte hvert dokument.

Fire nåværende-app-prober uten Qwen-inferens bekrefter avvikene:
01 henter isredning/varmt tøy,15 vannbehandling/flom,22 generelle tur-/skredråd
og25 tur/flom. Alle ville utløst generering, også de to kunnskapshullene.
Se `qwen_rag_app_integration.v1.json`. Dette er integrasjonskontroller, ikke nye
optimaliseringsforsøk. Den eksisterende deterministiske avståelsen gjelder bare
tom retrieval; ikke-tomme irrelevante treff avdekker ikke manglende kunnskap.
Kandidatens ingen-threshold gjør dette særlig viktig.

Promptserialiseringen er identisk med evaluert kandidat, men inneholder alltid
«Brukeren er i Norge». Case22 er eksplisitt i NZ; normal app filtrerer ogsåNO.
Dette er en integrasjons-/promptbegrensning som må behandles før kvalitet kan
godkjennes. Ingen endelig sikkerhetslogikk fra M3 er implementert.

Kjeden brukte lokale assets, ASGI i prosessen og eksplisitt lokal GGUF; Python
eksterne socketforbindelser var blokkert. Bare numerisk loopback var tillatt for
Windows' interne asyncio-socketpair. OS-nettet ble ikke koblet fra, og CLI-nett
ble ikke sperret med brannmur. En fysisk offline-test gjennom UI gjenstår som
manuell kontroll; ingen skjult betalt API ble brukt.

## Ressurser og tekniske begrensninger

| Mål | Baseline25 |
|---|---:|
| Samlet målt svartid | 377,40 s |
| Median / gjennomsnitt / min–maks | 14,45 / 15,10 / 11,75–20,62 s |
| Fersk query/rangering/packing, gjennomsnitt | 0,544 s |
| CPU, prosess+barneprosesser | 317,13 CPU-sekunder |
| Samtidig MiniLM/Qwen peak RSS | 2 037,49 MiB |
| Minste tilgjengelige verts-RAM | 294,13 MiB |
| Komplett prompt / kontekst, låste tokens totalt | 48 990 / 44 204 |
| Synlige svar, låste tokens totalt | 3 034 |
| Største komplette prompt / svar | 1 999 / 227 tokens |

Alle25+3 modellkall bestod 256 MiB reserve og4 GiB RSS-grensene. Minste margin
var bare38,13 MiB over reserven; RAM er fortsatt følsomt for øvrige apper.
RSS ble samplet hvert0,1 sekund, og GPU-VRAM er ikke målt. Dette er Windows-PC,
ikke en måling av mobil ytelse/energi. ModelService starter en ny CLI per
forespørsel, så svartiden inkluderer innlasting. Packing-tiden bruker tidligere
cachede tokeniseringer; ytelse for nye spørsmål uten token-cache er ikke målt.

Tre diagnostiske kall: 2 502 prompttokens +278 synlige svartokens. Samlet for
28 Qwen-kall: 51 492 prompttokens +3 312 svartokens =54 804 målte låste tokens.
Dette er teksttokenisering, ikke runtime-/abonnementsfakturering; chat-template/
kontrolltokens er ikke separat rapportert. Reasoning var av. Nye Codex-dommerkall:
0; betalte API-kall:0. Denne chatens kontobruk er ikke et dommerregnskap.
Ingen fullført Qwen-inferens ble gjentatt. Alle28 resultater har verifisert cache-
og filbinding for senere identisk gjenbruk.

Den gamle backend-venven peker på en utilgjengelig Python3.11. Et isolert lokalt
Python3.12-miljø med eksisterende prosjektavhengigheter ble brukt. 68 backendtester
og13 Qwen-relaterte tester består, hvorav8 gjelder det nye testløpet/isolasjonslaget.
Første launcher stoppet uten inferens fordi et for strengt socketvern også
blokkerte Windows-loopback. Separat teknisk adapter/revisjon er frosset; gammel
freeze/stopp er beholdt. Sandboxens første testprosess stanset, samme test bestod
uten sandbox. Ingen av disse er modellkvalitetsfunn.

Et diagnostisk `corpus_gap`-felt i råkjøringen brukte feil YAML-nøkkel og er false.
Det separate analyselaget henter korrekt gapstatus14/15/25 fra uendret
`expected_result` og kontrollerer mot eksisterende scorer. Rådata er ikke skrevet
om; feilen påvirket verken spørsmål, prompt, kontekst, inferens eller scorer.

## Prioritering før godkjenning

1. **Nødvendig først:** et avgrenset M2-06-arbeid for Qwens kildeetterlevelse,
   situasjonsvalg og kritiske betingelser. Reproduser08/17/21 og avståelse ved
   kunnskapshull; riktig retrieval er utilstrekkelig uten riktig generering.
   Begynn med den eksisterende modellen og små prompt-/svarkontraktendringer,
   ikke ny embedding-grid eller et uautorisert M3-sikkerhetslag.
2. **Før manuell kvalitetsgodkjenning:** avklar/håndter review07/16/18, geografisk
   kontekst og avståelse, gjenopprett normal backend-start, og få app/testoppsett
   til å samsvare etter separat godkjenning av kandidatens integrasjon. Ingen
   permanent kandidatbytte er gjort nå.
3. **Manuell eiergjennomgang:** faktiske representative UI-svar, korrekt
   kildestøtte, fysisk offline-kjøring og eksplisitte mangler. M2-06 fullføres
   ikke før denne er godkjent. M3-policy og godkjenningspunkter står uendret.
4. **Kan vente:** mer retrieval-optimalisering, mobil ressurs-/energitesting,
   runtime med vedvarende modell og utvidelse av godkjent korpus. De12 retrieval-
   manglene og tre korpushullene beholdes som kjente begrensninger; nødvendige
   innholdsendringer krever egne beslutninger.

Anbefalt neste praktiske steg er et lite, separat godkjent M2-06-genereringsarbeid
med de konkrete feilene som regresjoner. Resultatene gir ikke grunnlag for å
implementere en endelig retrieval-vinner, kjøre kontrollsettet eller starte M3.
