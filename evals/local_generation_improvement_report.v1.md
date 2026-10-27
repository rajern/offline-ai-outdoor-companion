# Lokal forbedringsrunde — resultat 25. oktober 2026

**Runden ga ingen klar samlet forbedring.** Qwen ble vesentlig svakere med begge
endringene. Gemma fikk noen bedre detaljer, men mistet andre viktige detaljer.
Den nye Gemma-prompten svekket dessuten håndteringen av kunnskapshull. Ingen av
de nye variantene bør erstatte baseline på dette grunnlaget.

## Hva vi faktisk testet

32 nye svar: to eksisterende lokale modeller, åtte identiske spørsmål og to
varianter. De nyeste 16 baseline-svarene og vurderingene ble gjenbrukt.

- **Baseline:** eksisterende prompt og eksisterende genereringsinnstillinger.
- **A — bare innstillinger:** eksisterende prompt; modelltilpasset sampling.
- **B — bare prompt:** eksisterende sampling; den låste prompten fra
  [forskningsforslaget](local_generation_prompt_proposal.v1.md). Den prioriterer
  nær kildegjengivelse og bevaring av vilkår og detaljer.

Spørsmål, faktiske kildeblokker og rekkefølge, modellfiler, kvantisering, runtime,
native chat-template, seed42, kontekst4096 og maksimalt512 svartokens var faste.
Thinking var av. Ingen spørsmål, fasit eller rubriceringsregler ble endret.

A brukte Qwen T1/p1/k20/min_p0/presence2 og Gemma T1/p.95/k64/min_p0/presence0.
B beholdt T.2/p.8/k20/min_p.05/presence0. Andre innstillinger ble eksplisitt låst
og kontrollert mot serverens faktiske verdier. Dette er to konkrete profiler,
ikke en undersøkelse av alle mulige innstillinger.

Vurdering: uendret svarrubrikk v1 og gpt-6.1-sol Medium, åtte sekvensielle kall
med fire anonymiserte svar hver. Tidligere identisk bestått kontroll ble
gjenbrukt. Alle32 svar, leverte kilder,60 nødvendige og8 betingede nye
kriterievurderinger, funnlister og8 kunnskapshullsvurderinger er gjennomgått.
Rådommene er bevart uten korreksjoner.

## Tallene

De åtte spørsmålene omfatter **seks kildestøttede situasjoner og to
kunnskapshull**. De seks situasjonene har15 nødvendige informasjonskrav.
De leverte kildene dekker13 av dem fullt. Begge betingede kravene finnes i
kildene, men anvendelighet vurderes separat for hvert svar.

| Modell/oppsett | Fullstendige krav | Bevarte av13 fullt leverte krav | Fullstendige kjernesvar av6 | Riktig avståelse av2 |
|---|---:|---:|---:|---:|
| Qwen baseline | 8/15 | 8/13 | 2/6 | 0/2 |
| Qwen A: innstillinger | 2/15 | 2/13 | 0/6 | 0/2 |
| Qwen B: prompt | 3/15 | 3/13 | 0/6 | 1/2 |
| Gemma baseline | 6/15 | 6/13 | 1/6 | 2/2 |
| Gemma A: innstillinger | 6/15 | 6/13 | 0/6 | 2/2 |
| Gemma B: prompt | 6/15 | 6/13 | 0/6 | 0/2 |

Dette er informasjonsdekning, ikke prosent korrekte eller trygge svar. Et krav
kan være dekket samtidig som svaret gir andre feilaktige råd. Heller ikke et
kjernesvar med alle krav dekket er dermed godkjent. Eksempelvis har Qwen
baseline8 fullstendige krav, hvorav7 også er vurdert fullt kildeforankret.

Tallene gjelder dette utvalget. Den tidligere retrieval-vurderingen **55/63
(87,3%)** gjelder hele utviklingssettet med25 spørsmål og er uendret. Denne
runden kjørte ikke søket på nytt og må ikke omtales som en ny full25-test.

| Modell/oppsett | Full/delvis/fraværende/usikkert av15 | Svar med kritisk utelatelse | Svar med direkte konflikt | Svar med udokumenterte tillegg |
|---|---|---:|---:|---:|
| Qwen baseline | 8/3/4/0 | 3 | 2 | 7 |
| Qwen A | 2/4/8/1 | 6 | 5 | 7 |
| Qwen B | 3/3/9/0 | 6 | 3 | 6 |
| Gemma baseline | 6/4/5/0 | 5 | 1 | 1 |
| Gemma A | 6/6/3/0 | 5 | 0 | 2 |
| Gemma B | 6/6/3/0 | 6 | 2 | 1 |

Funnkolonnene teller svar med minst ett rått dommerflagg, av åtte svar. De er
ikke en uttømmende opptelling av feil eller en klinisk alvorlighetsrangering.
Usikkerheter ved enkelte klassifiseringer er dokumentert i gjennomgangen.

## Hva endringene ga og kostet

**Qwen A:** ingen nye fullstendige krav; seks tidligere fullstendige krav tapt.
Språket ble ofte svært uklart, og svar blandet situasjoner og fant på innhold.
At profilen var begrunnet med modellråd, gjorde den ikke egnet til denne
norske RAG-oppgaven. Dette avviser den testede profilen, ikke alle mulige
innstillinger for Qwen.

**Qwen B:** vant ventetidskravet i23, men mistet seks andre fullstendige krav.
Fem av åtte svar traff tokengrensen, mot to i baseline. Modellen kopierte blant
annet innhold fra feil situasjon og kunne gjenta dette lenge. Ett korrekt
erkjent kunnskapshull gjorde ikke resten av dette svaret relevant eller godt.

**Gemma A:** mest interessant som begrenset positivt signal. Filterbegrensningen
i21 gikk fra fraværende til fullstendig. Pustovervåking i08 og eskalering i17
gikk fra fraværende til delvis. Begge kunnskapshull ble fortsatt håndtert riktig,
og antall direkte konfliktflagg falt fra ett til null. Samtidig forsvant den
fullstendige advarselen mot elektrisk kontakt i23, og udokumenterte tillegg
økte. Total dekning sto på6/15; ingen av de seks kjernesvarene ble fullstendige.
Dette er en reell avveining, ikke en tydelig vinner.

**Gemma B:** pustevurderingen i08 ble mer fullstendig. Samtidig ble HLR-trinn
gjengitt uten nødvendig situasjonsbetingelse. Ventetidsformuleringen i23 ble
uklar, og begge riktige avståelser gikk tapt: ett svar besvarte et annet tema,
og ett gjentok oppgaven uten å erkjenne kildehullet. Nær kildegjengivelse
bevarte dermed enkelte detaljer uten å sikre riktig valg og sammenkobling.

**Hovedfunnet:** Vansken er fortsatt å velge relevante kildeinstrukser, bevare
vilkår og bruke dem på den aktuelle situasjonen. Mer tekst og flere kopierte
detaljer løser ikke dette alene. Samtidig er konteksten full av uvedkommende
treff, og to krav er bare delvis levert; dette forsøket isolerer ikke årsaken
til svak kildeutvelgelse eller modellens maksimale kapasitet.

## Lengde, ressurser og kontroll

| Modell/oppsett | Genererte tokens totalt / median per svar | Stopp ved512 tokens |
|---|---:|---:|
| Qwen baseline | 2828 / 347,5 | 2/8 |
| Qwen A | 3250 / 375,5 | 2/8 |
| Qwen B | 3146 / 512 | 5/8 |
| Gemma baseline | 684 / 71 | 0/8 |
| Gemma A | 1227 / 128,5 | 0/8 |
| Gemma B | 973 / 77,5 | 0/8 |

Samlet ble8596 nye svartokens generert. Gemma brukte mer av det eksisterende
budsjettet uten å nå grensen. Resultatet gir ingen konkret støtte til å øke
budsjettet nå; en egen lengdetest er ikke gjennomført.

MiniLM var lastet samtidig uten nye søk. Under generering var maksimal målt
prosesstre-RSS2,61GiB for Qwen og3,21GiB for Gemma. Minste tilgjengelige
vertsminne var henholdsvis1797,7MiB og677,0MiB. De uendrede grensene på4GiB RSS
og256MiB reserve besto i både førkontroll og generering. Målingene er samplet
hvert0,1sekund, ikke en garanti mot alle kortvarige topper.

Genereringsgruppene tok516,7 og423,8sekunder inkludert oppstart og kontroll.
Rekkefølgen og ulik svarlengde hindrer en ren hastighetssammenligning mellom
profilene. Åtte vurderingskall tok442,8sekunder og rapporterte100458 tokens,
hvorav74410 input og26048 output;3968 inputtokens var bufret. Rapportert
reasoning-output er2586 tokens og legges ikke oppå totalen en gang til.

Fem relevante automatiserte tester besto før definisjonene ble låst. Den
avsluttende revisjonen kontrollerte eksakte forespørsler, native tokens,
effektive innstillinger, råsvar, dommerstrømmer, kilde-/sitatbindinger, bruk og
ressursgrenser.745 beskyttede historiske filer er uendret.

To tekniske oppstartsforsøk hadde **null svarforespørsler**: først feil runtimebane
ved omdirigert LOCALAPPDATA, deretter blokkert lokalforbindelse i sandkassen.
Begge er bevart. Separate frosne adaptere valgte samme verifiserte runtimefil,
rettet Windows-låsopprydding og brukte vertstilgang for lokalforbindelsen.
Ingen modell, parameter, kilde eller ressursgrense ble endret. Alle32 senere
svar og åtte dommerkall lyktes uten ny generering eller dommerforsøk.
Ingen betalt API eller kvotetilbakestilling ble brukt.

## Hva dette betyr videre

Forbedringshypotesene er nå prøvd i én avgrenset runde. De ga ingen grunn til
å erstatte baseline eller automatisk kombinere A+B. Rubrikken og Medium
forblir låst; resultatet gir ingen begrunnelse for å senke vurderingskravene.

Jeg anbefaler å avslutte denne innstillings-/promptjakten nå. Neste avgrensede
steg er den tidligere foreslåtte større-modell-referansen på identiske spørsmål
og kilder, med samme vurdering. Den kan vise hvor mye bedre samme kildepakke
kan brukes, før vi velger videre lokal forbedring eller en enklere svarform.
En eventuell test krever egen oppstart; den er ikke kjørt her.

Gemma A kan beholdes som en dokumentert kandidat til en senere bekreftelse,
men den har en konkret regresjon som må tas på alvor. Direkte kildevisning med
begrenset tolkning er fortsatt et alternativ. Også den krever relevant kildevalg;
dagens rå treffliste er ikke automatisk en egnet prosedyrevisning.

Ingen produksjonsvariant eller sikkerhetspolicy er valgt. M2-06-kvalitet er
fortsatt ikke godkjent, og M3 er ikke startet.

## Begrensninger og dokumentasjon

Dette er ett seed på åtte utvalgte utviklingsspørsmål. Ingen holdout eller
stabilitetstest er brukt. Ny vurdering grupperte fire svar per spørsmål,
mens gjenbrukte baseline-vurderinger grupperte opptil tre. Ingen regradering
av baseline ble brukt til å rette på denne forskjellen. Den nye prompten er
en samlet endring; effekten kan ikke tilskrives én setning. A+B er uprøvd.

Dommer, rubrikk og agentgjennomgang er ikke uavhengig klinisk fasit.
Rå konfliktflagget for Gemma B i23 kan være for sterkt for en tvetydig
oversettelse; delvis dekning og behovet for tydeligere ventebeskjed består.
Qwen B i25 fikk riktig avståelsesetikett selv om resten av svaret var svakt.
Ingen av disse forbeholdene snur hovedkonklusjonen.

- [Forhåndslåst protokoll](local_generation_improvement_protocol.v1.md)
- [Resultater med individuelle kriterier](local_generation_improvement_results.v1.json)
- [Gjennomgang av alle32 svar og forbehold](local_generation_improvement_review.v1.json)
- [Uavhengig teknisk kontroll](local_generation_improvement_audit.v1.json)
- [Runtime-/låsadapter](local_generation_improvement_transport.v1.md) og
  [lokalforbindelse](local_generation_improvement_host_transport.v1.md)

Private eksakte input, svar, rålogger, modell-/CLI-identiteter og frysinger:
`knowledge/local/diagnostics/local-generation-improvement-v1-2026-10-25/revision-03`.
`check` i vertstransport-adapteren og `--check` i
`audit_generation_improvement_v1.py` kontrollerer eksisterende filer uten
inferens. Sistnevnte rekalkulerer revisjonen og kontrollerer sluttmanifestet.
Oppsummerings- og revisjonsskript nekter å overskrive allerede publiserte
resultatfiler. Ikke kjør generering/vurdering på nytt for å rekonstruere
dokumentasjon.
