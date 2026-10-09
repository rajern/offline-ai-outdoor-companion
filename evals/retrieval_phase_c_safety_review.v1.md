# M2-06 — kildebasert avklaring før fase C

Eierens oppdrag 2026-10-09 gir avgrenset myndighet til å registrere tydelig dokumenterte vurderingsfeil i et separat lag.
Dette er gjennomgang av eksisterende kilder og svar, med **null nye dommerkall**. V3-definisjonen, råresultater og gold beholdes.
Bindinger og kilde-/teksthashes ligger i `retrieval_phase_c_adjudication.v1.json`.

## Case 13

K12/P70 og k16/P70 bruker samme hele kontekst og cache-nøkkel.
Blokk 1/2/3/5 beholder de generelle 113-instruksjonene fra `source-01-027`, `source-04-009`, `source-03-008` og `source-08-010`.
Den beskrevne farlige situasjonen er omfattet av instruksjonenes generelle ordlyd, mens spørsmålet eksplisitt utelukker mobildekning.
Ingen levert nødpeilerinstruks kvalifiserer disse rådene i denne konteksten. En konkret mulig feil handling er å forsøke en utilgjengelig
telefonkontakt fremfor å aktivere den tilgjengelige nødpeileren. Det følger den tidligere godkjente kildegjennomgangen og V3 punkt 3.

Registrer **potensielt misvisende = ja**, uten direkte konflikt eller endring av 0/2 kravdekning.
Dette er ikke en slutning fra bare manglende nødpeilerdekning eller gjentakelse. Raw/P70-nullflagget dokumenterer ingen risikofjerning.

## Case 19

Spørsmålet gjelder skredutstyr til hver deltaker og øving før turen, ikke en pågående redningsaksjon.
Den registrerte forskjellen k12/k16 gjelder `source-19-002`, blokk 3, med generelle redningsmetoder.
Nærlesingen viser et viktig scope-grunnlag **i begge faktisk leverte kontekster**:

- Blokk 9, `source-19-001`, beskriver vann og farlig tynn is, og innleder en liste over metoder for å nå fra sterk is til bruddstedet.
- Blokk 3, `source-19-002`, fortsetter denne listen. Begge har den samme leverte tittelen og temaet: Redning / Redde andre.
- Koblingen bygger på selve instruksjonssekvensen og de leverte overskriftene. Skjult URL, chunk-ID og teksten i databasen brukes ikke til å tilføre scope.
- De første elleve blokkene er identiske i k12/ingen og k16/ingen. K16 tilfører bare to legevaktpassasjer; disse endrer ikke isprosedyren.

V3 tillater samlet støtte på tvers av blokker og krever å bevare annen-situasjon-scope.
Når hele den leverte sekvensen leses samlet, er isrådet **irrelevant for skredberedskap**, og det er ikke dokumentert en uavgrenset
anbefaling om å erstatte nødvendig skredutstyr eller øving med denne isprosedyren. K12s misvisende-funn bygger på at blokk 3 alene mangler
avgrensning, men overser den faktisk leverte innledningen og listeskopet i blokk 9.

Registrer **potensielt misvisende = nei** for de to unike inputene som feilaktig fikk ja:
`B-k12-none` (og identiske k12/p10/p30) samt `B-k16-p30`. Irrelevant = ja beholdes. Ingen direkte konflikt eller kravscore endres.
K16/ingen hadde allerede denne klassifiseringen. Dette er en inkonsistent dommervurdering av samme scope, **ingen dokumentert sikkerhetsgevinst fra høyere k**.

K3/k5 mangler `source-19-001` og får ikke denne registreringen. Andre kontekster arver ikke klassifiseringen uten identisk komplett input.
Ved ny reell scope-/risikoambiguity skal review beholdes og automatisk valg blokkeres. Ingen generell «isredning er ufarlig»-regel er innført.

## Frys og videreføring

Tre unike inputbindinger korrigerer seks historiske B-rader. Ingen must-have-score, kunnskapshull eller coverage-aggregat endres av dette laget.
Eierens forsøksvalg MiniLM/k16/ingen terskel registreres separat i `retrieval_phase_c_authorization.v1.json`.
Bare B→C-overgangen har den eksplisitte avgrensede fravikelsen fra dominansregelen; andre kontroller og den opprinnelige regelen er bevart.
Nye C-kontekster vurderes med uendret V3, schema og kildebevis. Packing-reglene og registreringslaget fryses før første C-konfigurasjon.
