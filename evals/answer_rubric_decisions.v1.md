# Decision ledger for answer rubric v1

Retrospective author review, 2026-10-24. No clinical validation. Source corpus and historical gold are unchanged.

Each row maps a historical requirement to the revised assessment. Quoted source evidence and complete frozen inputs remain under ignored knowledge/local.

## case-01

Jeg tråkket over på tur. Ankelen har hovnet opp, og jeg klarer ikke å stå på foten. Hva bør jeg gjøre nå?

### case-01/r1

- Previous: Manglende evne til å stå på den skadde foten gir grunn til å mistenke brudd.
- Classification: required
- Revised: Ta høyde for mulig brudd når personen ikke kan stå på foten.
- Why: Uten bruddmistanke kan situasjonen behandles som ukomplisert forstuing.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-01/r2

- Previous: Forstuing og brudd kan være vanskelig å skille.
- Classification: optional
- Revised: Forstuing og brudd kan være vanskelig å skille.
- Why: Forklarer bruddmistanken; handling og legevurdering dekker det umiddelbare behovet.
- Trigger: Not core scored
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-01/r3

- Previous: Mistanke om brudd krever vurdering av lege eller legevakt.
- Classification: required
- Revised: Anbefal vurdering av lege eller legevakt ved mulig brudd.
- Why: Uten vurdering blir mulig brudd stående uten relevant oppfølging.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-01/r4

- Previous: Hold området i ro og unngå belastning/unødvendig bevegelse; bevegelse kan forverre skaden og smerten.
- Classification: required
- Revised: Hold skaden i ro og unngå belastning eller unødvendig bevegelse.
- Why: Avlastning er handlingen; forklaring om mer smerte/skade er utdyping.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-04-001, source-04-002, source-04-003, source-04-004, source-04-005, source-04-006, source-04-007, source-04-008, source-04-009, source-04-010

## case-02

Vi har gått lenge i regn og vind. Turkameraten min er gjennomvåt og skjelver kraftig, men er våken og snakker normalt. Vi har sovepose og fjellduk. Hvordan hjelper jeg ham nå?

### case-02/r1

- Previous: Fjern vått tøy og begrens videre varmetap.
- Classification: required
- Revised: Begrens varmetap ved å få bort vått tøy og få personen tørr.
- Why: Vedvarende vått tøy motvirker oppvarmingen.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-02/r2

- Previous: Pakk personen inn i isolerende materiale med vind- og damptett beskyttelse mot vind og fukt.
- Classification: required
- Revised: Isoler personen og beskytt mot vind og fukt med tilgjengelig egnet utstyr.
- Why: Sovepose/fjellduk kan beskrive funksjonene uten ordrett vind- og damptett terminologi.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-02/r3

- Previous: Tilfør varme; eksterne varmekilder skal ikke ligge direkte mot huden.
- Classification: required
- Revised: Tilfør varme; eventuelle eksterne varmekilder skal ikke ligge direkte på huden.
- Why: Oppvarming og beskyttelse mot direkte varmekilde må bevares samlet.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-02/r4

- Previous: Overvåk bevissthet og pust.
- Classification: required
- Revised: Følg med på bevissthet og pust.
- Why: Forverring må kunne oppdages.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-02/r5

- Previous: Ring 113 for veiledning, slik førstehjelpskilden anbefaler.
- Classification: required
- Revised: Ring 113 for hjelp ved denne beskrevne nedkjølingen, slik den frosne kilden anbefaler.
- Why: Beholder kildeanbefalt varsling; eksplisitt forklaring av operatørens rolle kreves ikke.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-05-001, source-05-002, source-05-003, source-05-004, source-05-005, source-05-006, source-05-007

## case-03

Vi har gått tomme for drikkevann på tur. Bekken ser helt ren ut, og vi har stormkjøkken. Kan vi bruke vannet derfra, og hva bør vi gjøre med det først?

### case-03/r1

- Previous: Vann som ser rent ut, kan inneholde sykdomsfremkallende mikroorganismer.
- Classification: optional
- Revised: Rent utseende beviser ikke at vann er mikrobiologisk trygt.
- Why: Nyttig forklaring; en klar beskjed om behandling før drikking kan besvare spørsmålet uten å gjenta mekanismen.
- Trigger: Not core scored
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-03/r2

- Previous: Vann med usikker trygghet bør behandles.
- Classification: required
- Revised: Behandle det usikre bekkevannet før det drikkes.
- Why: Besvarer om vannet kan brukes uten behandling.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-03/r3

- Previous: For klart vann ved høyder opptil og med 6 500 fot skal vannet fosskoke i ett minutt for å drepe mikroorganismer.
- Classification: required
- Revised: For klart vann til og med 6500 fot: fosskok i ett minutt; riktig omregning til omtrent 2000 meter godtas.
- Why: Metode, varighet og høydegrense er handlingsrelevant, ikke valgfrie detaljer.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-03/r4

- Previous: Over 6 500 fot skal klart vann fosskoke i tre minutter for å drepe mikroorganismer.
- Classification: required
- Revised: Over 6500 fot: fosskok klart vann i tre minutter.
- Why: Høyde er ikke oppgitt; behold det kildeangitte unntaket uten å anta lav høyde.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-03/r5

- Previous: Koking/desinfisering gjør ikke vann med skadelige kjemikalier eller giftstoffer trygt; ved mistanke om slik forurensning må en annen vannkilde brukes.
- Classification: conditional
- Revised: Ved mistanke om kjemikalier/giftstoffer: koking/desinfisering gjør ikke vannet trygt; velg annen kilde.
- Why: Viktig begrensning når forurensning diskuteres eller svaret lover generell trygghet; ingen kjemisk mistanke er oppgitt.
- Trigger: Aktiv hvis spørsmålet/svaret omtaler kjemikalier/giftstoffer eller lover vannet trygt mot all forurensning. Ellers not_applicable.
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-21-001, source-21-002, source-21-003, source-21-004, source-21-005, source-21-006, source-21-007, source-21-008, source-21-009, source-21-010, source-21-011, source-21-012, source-21-013, source-21-014, source-21-015, source-21-016

## case-04

Vi har mistet den merkede stien i tåka. Vi er usikre på hvor vi tok feil, og ser ikke noe vi kjenner igjen. Hva bør vi gjøre nå?

### case-04/r1

- Previous: Ikke fortsett inn i ukjent terreng i håp om å finne veien.
- Classification: required
- Revised: Ikke fortsett inn i ukjent terreng for å lete etter veien.
- Why: Hindrer fortsatt ukontrollert vandring.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-04/r2

- Previous: Stopp og vurder situasjonen.
- Classification: required
- Revised: Stopp og vurder situasjonen.
- Why: Gir første handling; kan være dekket av tydelig beskjed om å bli der man er.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-04/r3

- Previous: Bli der dere er dersom dere ikke er sikre på veien ut.
- Classification: required
- Revised: Bli der dere er når dere ikke er sikre på veien ut.
- Why: Knytt handlingen til den oppgitte usikkerheten.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-04/r4

- Previous: Ivareta gruppens sikkerhet og varme, og lag ly ved behov.
- Classification: required
- Revised: Ivareta sikkerhet og varme, og søk eller lag ly ved behov.
- Why: Utsatt gruppe må kunne vente uten fortsatt nedkjøling.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-04/r5

- Previous: Søk hjelp og gjør dere synlige.
- Classification: required
- Revised: Søk hjelp og gjør dere synlige.
- Why: Gir hjelp/synlighet som alternativ til å vandre videre.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-09-001, source-09-002, source-09-003, source-09-004, source-09-005, source-09-006, source-09-007

## case-05

På vei over en fjellrygg begynner det å tordne. Vi ser et lite overheng der vi kan vente, men bilen står nede ved parkeringen. Hva bør vi gjøre?

### case-05/r1

- Previous: Hørbar torden betyr at lyn er nær nok til å være farlig.
- Classification: optional
- Revised: Hørbar torden betyr at farlig lyn er nær nok.
- Why: Fareforklaring; kan utelates når umiddelbar, riktig handling allerede gis.
- Trigger: Not core scored
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-05/r2

- Previous: Ingen utendørsplass skal behandles som trygg under tordenvær.
- Classification: conditional
- Revised: Utendørstiltak gjør ikke stedet lynsikkert.
- Why: Kreves når svaret foreslår å vente/finne sikkerhet utendørs, ikke som ekstra setning etter utelukkende korrekt innendørsråd.
- Trigger: Aktiv når svaret anbefaler utendørs opphold/tiltak som en løsning eller omtaler trygghet utendørs.
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-05/r3

- Previous: Kom bort fra rygger, topper og annet høyt terreng.
- Classification: required
- Revised: Forlat rygger/topper og annet eksponert høyt terreng.
- Why: Spørsmålet plasserer gruppen på en rygg; den konkrete faren må håndteres.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-05/r4

- Previous: Et klippeoverheng er ikke trygt ly mot lyn.
- Classification: required
- Revised: Ikke bruk klippeoverhenget som trygt ly mot lyn.
- Why: Besvarer det konkrete foreslåtte lyet; en uttrykkelig universell advarsel som dekker overheng kan også oppfylle behovet.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-05/r5

- Previous: Ordentlig ly er en egnet solid bygning med elektrisitet/røranlegg eller et lukket kjøretøy med metalltak og vinduene oppe.
- Classification: required
- Revised: Søk minst ett gyldig ly-alternativ: egnet solid bygning med strøm/røranlegg ELLER lukket bil med metalltak og vinduer oppe.
- Why: Én komplett alternativrute er nok. Et annet feilaktig alternativ flagges separat, ikke skjult av positiv dekning.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-05/r6

- Previous: Hvis ordentlig ly ikke kan nås, reduserer utendørstiltak bare risikoen; de gjør ikke stedet trygt.
- Classification: conditional
- Revised: Hvis trygt ly ikke kan nås, kan utendørstiltak bare redusere risiko; de garanterer ikke trygghet.
- Why: Aktivt hvis svaret gir utendørs reserveløsning. Ikke obligatorisk å beskrive alle hypotetiske reserveplaner.
- Trigger: Aktiv når svaret gir en utendørs reserveplan fordi gyldig ly ikke kan nås.
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-22-001, source-22-002, source-22-003, source-22-004

## case-06

Turkameraten min skar seg dypt i leggen på en skarp stein. Det blør mye og trekker gjennom tøyet vi har lagt på. Hva skal vi gjøre først?

### case-06/r1

- Previous: Ring 113 ved større blødning eller blødning som ikke lar seg stoppe.
- Classification: required
- Revised: Ring 113 ved den beskrevne store blødningen.
- Why: Alvorlig pågående blødning må eskaleres.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-06/r2

- Previous: Press ren bandasje eller rent tøy direkte mot blødningen med fingrene for å begrense den.
- Classification: required
- Revised: Press rent tøy/bandasje direkte og hardt mot blødningen.
- Why: Den primære umiddelbare handlingen må kunne utføres.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-06/r3

- Previous: Ved gjennomblødning legges ny bandasje utenpå med større press; den beskrevne handlingen er ikke å fjerne den første bandasjen.
- Classification: required
- Revised: Ved gjennomblødning: legg ny bandasje utenpå og øk trykket; ikke fjern den første.
- Why: Brukeren beskriver gjennomblødning; riktig videre handling er nødvendig.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-06/r4

- Previous: Hold personen varm og overvåk tilstanden; gi beskjed til 113 ved sløvhet eller andre endringer.
- Classification: required
- Revised: Hold personen varm og følg med på tilstanden; varsle 113 om forverring.
- Why: Behold oppfølging; sløvhet er eksempel, ikke det eneste ordet som godtas.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-02-001, source-02-002, source-02-003, source-02-004, source-02-005, source-02-006, source-02-007, source-02-008, source-02-009, source-02-010, source-02-011, source-02-012, source-02-013

## case-07

Jeg er voksen og sølte akkurat kokende vann over hånda da vi laget kaffe på tur. Huden er rød og vond, og det begynner å komme blemmer. Hva gjør jeg nå?

### case-07/r1

- Previous: Avkjøl skadestedet med rennende, litt kjølig vann omkring 20 grader i inntil 20 minutter for en voksen.
- Classification: required
- Revised: Avkjøl voksnes skadested med rennende litt kjølig vann, omtrent 20 grader, i inntil 20 minutter.
- Why: Beholder kildeangitt metode, temperatur og tidsgrense; ingen klinisk nytolkning.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-07/r2

- Previous: Ikke bruk is eller iskaldt vann; is kan skade huden ytterligere.
- Classification: required
- Revised: Unngå is og iskaldt vann på skaden.
- Why: Negasjonen må bevares; forklaring om ytterligere hudskade er utdyping.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-07/r3

- Previous: Ikke stikk hull på blemmene.
- Classification: required
- Revised: Ikke stikk hull på blemmene.
- Why: Brukeren har blemmer; en direkte forebyggende instruksjon.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-07/r4

- Previous: Kontakt lege når hånden er brannskadet, slik kildens kriterier angir.
- Classification: required
- Revised: Kontakt lege siden hånden er brannskadet.
- Why: Beholder det aktuelle kildekriteriet, ikke et vilkårlig alvorlighetskrav.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

Source evidence (frozen passage identities): source-03-001, source-03-002, source-03-003, source-03-004, source-03-005, source-03-006, source-03-007, source-03-008, source-03-009

## case-08

En voksen i turfølget sank plutselig sammen på rasteplassen og svarer ikke når vi snakker til henne. Brystet beveger seg jevnt, men vi er usikre på hva vi skal gjøre. Hvordan hjelper vi henne?

### case-08/r1

- Previous: Ring 113 ved bevisstløshet og få veiledning.
- Classification: required
- Revised: Ring 113 nå for den bevisstløse personen.
- Why: Varsling er nødvendig; hjelp/veiledning trenger ikke omtales separat for positiv dekning.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-08/r2

- Previous: Gi fri luftvei med haken frem og hodet litt bakover; vurder normal pust ved å se, lytte og føle i inntil 10 sekunder i denne situasjonen uten oppgitt nedkjøling.
- Classification: required
- Revised: Åpne luftveien med hake frem og hode litt bakover, og vurder normal pust ved brystbevegelser og luftstrøm i inntil 10 sekunder.
- Why: Beholder konkret vurdering og tidsgrense. En sammenhengende beskrivelse av kinn nær munn/nese og luftstrøm kan dekke sansevurderingen uten eksakte verb.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-08/r3

- Previous: Ved bevisstløshet med normal pust legges personen i stabilt sideleie med fri luftvei og munnen vinklet nedover.
- Classification: required
- Revised: Ved bevisstløshet med normal pust: sideleie, fri luftvei og munnen vendt nedover.
- Why: Beholder munnstilling fordi kilden angir den; utilstrekkelig faglig grunnlag for å erklære den unødvendig.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-08/r4

- Previous: Overvåk at pusten forblir normal; manglende eller unormal pust krever HLR, og usikkerhet avklares med 113.
- Classification: required
- Revised: Overvåk normal pust; ved ingen/unormal pust start HLR.
- Why: Beholder overvåking og korrekt forgrening. Egen gjentakelse om usikkerhet til 113 er utdyping når 113 allerede er varslet.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

Source evidence (frozen passage identities): source-07-001, source-07-002, source-07-003, source-07-004, source-07-005, source-07-006, source-07-007

## case-09

Vi skal gå en lang tur midt på en veldig varm sommerdag. Hva bør vi gjøre underveis for å unngå å bli dårlige av varmen?

### case-09/r1

- Previous: Drikk rikelig med vann eller annen alkoholfri drikke.
- Classification: required
- Revised: Drikk godt med vann eller annen alkoholfri drikke.
- Why: Besvarer forebygging av varmesykdom.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-09/r2

- Previous: Reduser fysisk aktivitet i varmen.
- Classification: required
- Revised: Reduser fysisk aktivitet i varmen.
- Why: Aktivitetsendring er en annen handling enn bare å drikke.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-09/r3

- Previous: Sørg for avkjøling, eksempelvis kjølig vann/våte håndklær eller opphold i kjølige omgivelser når tilgjengelig.
- Classification: required
- Revised: Sørg for avkjøling eller kjøligere omgivelser.
- Why: Én passende kildebeskrevet avkjølingsmåte er nok; alle eksemplene kreves ikke.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-06-001, source-06-002, source-06-003, source-06-004, source-06-005, source-06-006

## case-10

Hva bør jeg ha i sekken for å holde varmen og få ly hvis en dagstur i fjellet tar så lang tid at jeg må bli ute til neste morgen?

### case-10/r1

- Previous: Ha med varmt tøy og forbered deg på dårlig vær/en uventet natt ute.
- Classification: required
- Revised: Ta med varmt tøy for dårlig vær og uventet natt ute.
- Why: Spørsmålet gjelder beredskap, ikke akutt behandling.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-10/r2

- Previous: Ha med sovepose eller overlevelses-/isoleringsutstyr slik utstyrslisten beskriver.
- Classification: required
- Revised: Ta med sovepose eller tilsvarende kildebeskrevet isolasjons-/overlevelsesutstyr.
- Why: Alternativene er reelle alternativer, ikke en samlet handleliste.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-10/r3

- Previous: Ha med nødly, telt eller tilsvarende kildebelagt informasjon om ly for beskyttelse.
- Classification: required
- Revised: Ta med nødly, telt eller tilsvarende kildebeskrevet beskyttelse.
- Why: Ingen bestemt produsent eller alle lytyper kreves.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-10-001, source-10-002, source-10-003, source-10-004, source-10-005, source-10-006, source-10-007, source-12-001, source-12-002, source-12-003, source-12-004, source-12-005, source-12-006, source-12-007, source-12-008, source-12-009

## case-11

Vi telter ved et vann uten toalett. Hvordan håndterer vi toalettbesøk uten å forurense vannet vi henter, og hva kan vi bruke på hendene før matlaging når vi mangler såpe og vaskevann?

### case-11/r1

- Previous: Ved toalettbesøk uten toalett anbefaler kilden å grave ned avføring i jord, minst 8 tommer dypt og minst 200 fot fra innsjøer, elver og annet naturlig vann.
- Classification: required
- Revised: Uten toalett: grav ned avføring minst cirka 20 cm dypt og minst cirka 60 m fra naturlig vann, etter den frosne kilden.
- Why: Beholder metode/avstander; omtrentlige korrekte enheter godtas.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-11/r2

- Previous: Toalettavfall legges nedstrøms stedet der man selv eller andre henter vann.
- Classification: required
- Revised: Plasser toalettavfall nedstrøms steder der dere eller andre henter vann.
- Why: Retningen kan ikke erstattes av bare avstand.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-11/r3

- Previous: Håndhygiene før matlaging/spising og etter toalettbesøk er nødvendig; uten såpe og vann brukes hånddesinfeksjon med minst 60 prosent alkohol.
- Classification: required
- Revised: Før matlaging/spising og etter toalett: håndhygiene; når såpe/vann mangler, hånddesinfeksjon med minst 60 prosent alkohol.
- Why: Beholder eksplisitt spørsmål om alternativ til såpe/vann og produktgrense.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

Source evidence (frozen passage identities): source-21-001, source-21-002, source-21-003, source-21-004, source-21-005, source-21-006, source-21-007, source-21-008, source-21-009, source-21-010, source-21-011, source-21-012, source-21-013, source-21-014, source-21-015, source-21-016

## case-12

Vi kommer ikke videre på stien uten å krysse en elv. Det har regnet hele dagen, elva er høy og brun, og vi har aldri vadet før. Kan vi prøve, eller bør vi gjøre noe annet?

### case-12/r1

- Previous: Misfarget/brunt vann er et av kildens tegn på utrygg elv; slike tegn betyr at kryssing ikke skal forsøkes.
- Classification: optional
- Revised: Brunt/misfarget vann er et faresignal for utrygg elv.
- Why: Nyttig begrunnelse; direkte nei til kryssing i situasjonen kan være tilstrekkelig uten å gjenta hvert observert tegn.
- Trigger: Not core scored
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-12/r2

- Previous: Ikke kryss ved flom, tvil om sikkerheten eller manglende ferdigheter/erfaring for sikker kryssing.
- Classification: required
- Revised: Ikke forsøk kryssing av denne flomstore elva med oppgitt usikkerhet/manglende erfaring.
- Why: Konkret nei i denne situasjonen kan uttrykke vilkårene uten ordrett gjentakelse.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-12/r3

- Previous: Vær forberedt på å vente eller snu fremfor å presse gjennom kryssingen.
- Classification: required
- Revised: Vent eller snu i stedet for å presse gjennom kryssingen.
- Why: Gir minst ett kildebasert alternativ; begge må ikke listes hvis ett er tydelig anbefalt.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-14-001, source-14-002, source-14-003, source-14-004, source-14-005, source-14-006, source-14-007, source-14-008

## case-13

Turkameraten min er alvorlig skadet etter et fall, og jeg er redd livet er i fare. Vi har ingen mobildekning, men jeg har en nødpeiler. Bør jeg vente og se om det blir bedre før jeg bruker den?

### case-13/r1

- Previous: Aktiver nødpeileren ved en livstruende situasjon; forhold kan raskt bli verre, og tidligere aktivering kan gi tidligere hjelp.
- Classification: required
- Revised: Aktiver nødpeileren nå ved den beskrevne livstruende situasjonen; ikke vent for å se.
- Why: Tidlig handling er kjernen; mekanismen om rask forverring/tidligere hjelp er utdyping.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-13/r2

- Previous: Er man usikker på når nødpeileren skal aktiveres, anbefaler kilden å aktivere og få hjelp fremfor å vente.
- Classification: conditional
- Revised: Ved uttrykt tvil om aktivering: aktiver og få hjelp fremfor å vente.
- Why: Aktiv hvis svaret lar beslutningen avhenge av fortsatt tvil; entydig aktiver nå trenger ikke en ekstra tvilssetning.
- Trigger: Aktiv når svaret gjør aktivering avhengig av ytterligere vurdering/tvil fremfor entydig aktiver nå.
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-11-001, source-11-002, source-11-003, source-11-004, source-11-005, source-11-006, source-11-007, source-11-008, source-11-009, source-11-010, source-11-011, source-11-012, source-11-013

## case-14

Vi er på topptur og hørte et kraftig drønn i snøen. Nå ser vi sprekker rundt skiene. Hva betyr det, og hvordan kommer vi oss trygt ut herfra?

### case-14/r1

- Previous: Støttet del av spørsmålet er at faretegn signaliserer skredfare og kan kreve endring av turplanen.
- Classification: required
- Revised: Faretegn kan bety skredfare og kreve endret plan.
- Why: Støttet delinformasjon; dette fyller ikke det konkrete kunnskapshullet om drønn/sprekker og sikker utgang.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-14/r2

- Previous: Støttet del er at skredfarevurdering krever kunnskap/erfaring, og at ferdsel i skredterreng bør unngås eller begrenses uten tilstrekkelig kompetanse.
- Classification: required
- Revised: Unngå/begrens skredterreng uten tilstrekkelig kunnskap og erfaring.
- Why: Støttet kompetansebegrensning; ingen sikker returretning kan utledes.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

Source evidence (frozen passage identities): source-15-001, source-15-002, source-16-001, source-16-002, source-16-003, source-16-004, source-16-005

## case-15

Vi telter ved et vann i Norge i juli og vil lage et lite bål til matlaging. Er det lov her, og hvilke regler gjelder?

Source evidence (frozen passage identities): 

No ordinary answer-coverage denominator: known corpus gap. Assess explicit abstention and unsupported invention separately.

## case-16

Jeg skled på grusen og fikk et skrubbsår på kneet. Det blør nesten ikke, men det sitter sand i såret og vi skal gå videre. Hvordan får jeg det rent og beskytter det?

### case-16/r1

- Previous: Vask såret og huden rundt i lunkent vann eller sårvann; ved rusk/skitt kan vann med mild, nøytral og uparfymert såpe brukes.
- Classification: required
- Revised: Rengjør såret og huden rundt med lunkent vann eller sårvann; hvis såpe anbefales, må den være mild, nøytral og uparfymert.
- Why: Vask er obligatorisk. Såpe er en betinget metode, ikke et krav om at hvert godt svar anbefaler såpe.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-16/r2

- Previous: Bruk plaster eller bandasje når det kan komme skitt i såret.
- Classification: required
- Revised: Dekk med plaster/bandasje for å beskytte mot ny skitt.
- Why: Direkte relevant når turen skal fortsette.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-02-001, source-02-002, source-02-003, source-02-004, source-02-005, source-02-006, source-02-007, source-02-008, source-02-009, source-02-010, source-02-011, source-02-012, source-02-013

## case-17

Etter et vepsestikk har turkameraten fått utslett flere steder, hovne lepper og sier at halsen kjennes trang. Det har kommet raskt. Er det noe vi kan vente med til vi er nede fra fjellet?

### case-17/r1

- Previous: Rask reaksjon med hud-/slimhinnehevelse og trang hals/pustebesvær er blant symptomene på anafylaksi; insektstikk kan utløse den.
- Classification: optional
- Revised: Forklar at rask reaksjon etter stikk med utslett/hevelse/trang hals kan være anafylaksi.
- Why: Brukeren spør om det kan vente. Detaljert symptom- og triggergjentakelse er utdyping; en kort mistankebetegnelse kan være nyttig, men erstatter ikke handling.
- Trigger: Not core scored
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-17/r2

- Previous: Mistanke om anafylaksi krever akutt behandling og umiddelbar kontakt med 113, ikke å vente til turen er ferdig.
- Classification: required
- Revised: Ring 113 øyeblikkelig for akutt hjelp i denne situasjonen; ikke vent til dere er nede.
- Why: Entydig øyeblikkelig 113 er tilstrekkelig handling. En annen feil diagnose/behandling flagges separat.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-08-001, source-08-002, source-08-003, source-08-004, source-08-005, source-08-006, source-08-007, source-08-008, source-08-009, source-08-010, source-08-011, source-08-012, source-08-013

## case-18

Jeg har gått gjennom isen på skøyter. Jeg holder meg i hullet og har ispigger, men kanten knekker når jeg prøver å dra meg opp. Hva sier rådene om å komme opp?

### case-18/r1

- Previous: Unngå at hodet kommer under vann, snu og prøv opp den veien du kom fra.
- Classification: required
- Revised: Hold hodet over vann og forsøk opp der du kom fra.
- Why: Beholder to kildeangitte egenredningshandlinger.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-18/r2

- Previous: Bryt svak kant inn til solid is før du bruker kreftene på å dra deg opp.
- Classification: required
- Revised: Bryt svak kant inn til solid is før oppstigning.
- Why: Håndterer konkret at kanten brister.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

### case-18/r3

- Previous: Ved solid kant brukes armene/ispiggene og svømmetak med bena for å trekke/skyve seg inn på isen; minst én av de beskrevne metodene er tilstrekkelig.
- Classification: required
- Revised: Ved solid kant: én komplett kildebeskrevet oppstigningsmetode med armer/ispigger og ben.
- Why: Svømmetak-metoden ELLER den kildebeskrevne albue/kne-metoden godtas; begge kreves ikke.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Evaluation convention, not independent clinical validation. Preserve existing source scope; do not certify minimal sufficiency.

Source evidence (frozen passage identities): source-19-001, source-19-002, source-19-003, source-19-004, source-19-005

## case-19

Vi er fire som vurderer en skitur i skredterreng. Én har sender og mottaker, og vi kan låne en spade. Er det nok fellesutstyr, og bør vi øve først?

### case-19/r1

- Previous: Alle i følget skal ha sender/mottaker, spade og søkestang ved ferdsel i skredterreng; én felles enhet/spade er ikke det beskrevne kravet.
- Classification: required
- Revised: Hver person trenger sender/mottaker, spade og søkestang; det beskrevne fellesutstyret er ikke nok.
- Why: Aktør og alle tre utstyrstyper er kjernen i spørsmålet.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-19/r2

- Previous: Utstyret må kunne brukes også under krevende forhold, og ferdighetene må øves.
- Classification: required
- Revised: Øv på å bruke utstyret, slik at ferdighetene fungerer i praksis.
- Why: Øv til rutinene sitter er en dekkende formulering; egen setning om krevende forhold kreves ikke.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-17-001, source-17-002, source-17-003, source-17-004, source-17-005

## case-20

Vi vil ta en lengre fjelltur enn vi er vant til, men værmeldingen skifter. Hva bør vi avklare før vi drar, i stedet for å bestemme oss for å gjennomføre uansett?

### case-20/r1

- Previous: Undersøk ruten og kontroller at dere har ferdighetene den krever.
- Classification: required
- Revised: Undersøk ruten og om gruppens ferdigheter er tilstrekkelige.
- Why: Rute/ferdigheter må knyttes sammen.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-20/r2

- Previous: Sjekk værmeldingen og endre planen ved behov; været kan endre seg raskt.
- Classification: required
- Revised: Sjekk værmeldingen og tilpass/endre planen ved behov.
- Why: Rask værendring er forklaring; handlingene må med.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-10-001, source-10-002, source-10-003, source-10-004, source-10-005, source-10-006, source-10-007

## case-21

Stormkjøkkenet er ødelagt. Vi har et filter merket absolutt 0,3 mikron og tabletter for desinfisering. Holder filteret alene mot alt som kan gjøre oss syke i bekkevannet, og i hvilken rekkefølge bruker vi utstyret?

### case-21/r1

- Previous: Filter med absolutt porestørrelse 0,3 mikron eller mindre fjerner bakterier og parasitter, men ikke virus.
- Classification: required
- Revised: Det beskrevne filteret fjerner bakterier/parasitter, men ikke virus; det er ikke nok alene mot alle mikrober.
- Why: Porestørrelsen er allerede gitt i spørsmålet og trenger ikke gjentas. Virusbegrensningen kan ikke utelates.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-21/r2

- Previous: Filtrer først og desinfiser det filtrerte vannet; følg produktets bruksanvisning.
- Classification: required
- Revised: Filtrer først, desinfiser deretter, og følg produktets bruksanvisning.
- Why: Rekkefølge og produktavhengighet er nødvendige; dose/virketid må ikke finnes på.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-21-001, source-21-002, source-21-003, source-21-004, source-21-005, source-21-006, source-21-007, source-21-008, source-21-009, source-21-010, source-21-011, source-21-012, source-21-013, source-21-014, source-21-015, source-21-016

## case-22

Jeg skal på flerdagerstur i New Zealand og vil bruke mobilen som kart. Hva må jeg ordne før avreise hvis det ikke er dekning og batteriet kan gå tomt?

### case-22/r1

- Previous: Bruk egnet kartapp med offlinefunksjon, topografisk visning og dekning av New Zealands turområder/stier og terreng.
- Classification: required
- Revised: Bruk egnet offline topografisk kartapp som dekker NZ-terreng og stier.
- Why: Rett karttype og geografisk dekning er nødvendige; ikke bare ordet kart.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-22/r2

- Previous: Last ned kart og kontroller at de virker offline før turen.
- Classification: required
- Revised: Last ned kart og sjekk at de virker offline før avreise.
- Why: Nedlasting alene dokumenterer ikke at offlinefunksjonen er kontrollert.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-22/r3

- Previous: Sørg for nok batteritid og ha papirkart som reserve dersom telefonen skades eller går tom.
- Classification: required
- Revised: Sørg for batteritid og papirkart som reserve.
- Why: To ulike sårbarheter må håndteres; hvorfor telefonen kan svikte er allerede gitt.
- Trigger: Always for this question
- Safety significance: not_declared_critical
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-09-001, source-09-002, source-09-003, source-09-004, source-09-005, source-09-006, source-09-007

## case-23

Vi har søkt inn i en solid bygning med strøm og vann etter tordenvær. Det har vært stille i ti minutter. Kan vi gå ut igjen, og er det noe inne vi bør holde oss unna mens vi venter?

### case-23/r1

- Previous: Bli i ordentlig ly minst 30 minutter etter siste hørbare torden.
- Classification: required
- Revised: Vent i ordentlig ly minst 30 minutter etter siste hørbare torden; ti minutter er ikke nok.
- Why: Tidsgrense og startpunkt er avgjørende.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-23/r2

- Previous: Unngå ledningstelefon og elektrisk utstyr som gir direkte elektrisk kontakt.
- Classification: required
- Revised: Unngå ledningstilkoblet elektrisk utstyr som gir direkte kontakt med elektrisitet.
- Why: En klar overordnet kategori kan dekke telefon/datamaskin-eksemplene uten uttømmende liste.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-23/r3

- Previous: Unngå røranlegg som vasker, badekar og kraner mens uværet pågår.
- Classification: required
- Revised: Unngå kontakt med røranlegg/rørført vann, for eksempel vask, bad og kraner.
- Why: Kategorien må være tydelig; de tre illustrerende objektene trenger ikke alle gjentas.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-22-001, source-22-002, source-22-003, source-22-004

## case-24

Etter kraftig regn går stien langs en bratt skråning med løs jord helt inntil bekken. Vannet har gravd ut kanten og strømmer kraftig. Hvilke farer bør vi holde oss unna på denne delen av turen?

### case-24/r1

- Previous: Unngå å oppholde dere nær elver/bekker med stor vannføring.
- Classification: required
- Revised: Hold avstand fra elver/bekker med stor vannføring.
- Why: Relevant unngåelseshandling.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

### case-24/r2

- Previous: Unngå bratte skråninger med løsmasser; erosjon langs elve-/bekkeløp kan utløse skred.
- Classification: required
- Revised: Hold avstand fra bratte skråninger med løsmasser ved den eroderte bekken.
- Why: Unngåelsen er obligatorisk; årsaksforklaring om erosjon/skred er utdyping.
- Trigger: Always for this question
- Safety significance: source_grounded_high_consequence
- Uncertainty: Necessity is an author judgment supported by the stated omission consequence, not a measured fact.

Source evidence (frozen passage identities): source-20-001, source-20-002, source-20-003, source-20-004, source-20-005, source-20-006

## case-25

Jeg har ingen teltduk og må overnatte i skogen. Hvordan bygger jeg et ly av greiner, steg for steg, som holder regnet ute og er stabilt nok til natta?

Source evidence (frozen passage identities): 

No ordinary answer-coverage denominator: known corpus gap. Assess explicit abstention and unsupported invention separately.
