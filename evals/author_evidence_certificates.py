"""Source-authored sufficient evidence certificates for unchanged historical gold.

No manual retrieval annotations are read here. These conservative certificates
are sufficient routes, NOT an exhaustive semantic gold or a chunk-ID whitelist.
Absent certificates mean needs_review, not proof of failed retrieval.
"""
import json
from eval_foundation import CORPUS, BASE_HASH, CORPUS_HASH, source_evidence_locations


def definition():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))["items"]
    by_id = {p["id"]: p for p in corpus}

    def s(locator, *quotes, heading=False):
        p = by_id[locator]
        atoms = []
        for quote in quotes:
            atom = {"source_id": p["document_id"], "section": p["section"], "quote": quote}
            if heading:
                atom["location"] = "section_heading"
            source_evidence_locations(atom, corpus)
            atoms.append(atom)
        return atoms

    def item(*routes):
        return {"alternatives": [{"all_of": route} for route in routes]}

    rules = {}
    rules["case-01"] = [
        item(s("source-04-005", "Hvis den skadde ikke klarer å stå på foten eller vri på armen, bør du mistenke brudd.")),
        item(s("source-04-005", "Det er ikke alltid så lett å avgjøre om det er brudd eller ikke.")),
        item(s("source-04-005", "Ta den skadde til lege eller legevakt hvis du mistenker brudd.")),
        item(s("source-04-006", "Hold det skadede området helt i ro. Bevegelse kan gjøre skaden verre og øke smerten.")),
    ]
    rules["case-02"] = [item(s("source-05-004", q)) for q in [
        "Fjern vått tøy raskt og systematisk",
        "Pakk personen inn i varmt, isolerende tøy eller materiale - slik at det blir vindtett og damptett",
        "Tilfør varme, som flasker med varmt vann (ikke direkte på huden)",
        "Overvåk bevissthet og pust", "Ring 113 for å få veiledning"]]
    rules["case-03"] = [
        item(s("source-21-005", "Water containing germs that can make you sick—including bacteria, viruses, and parasites—sometimes looks clean.")),
        item(s("source-21-002", "If you are not sure whether the water you are using is safe to drink, treat it to remove germs."),
             s("source-21-003", "If you are not sure if water is safe to drink, boil it or use another method to remove germs.")),
        item(s("source-21-010", "To kill germs, bring clear water to a rolling boil for 1 minute.", "At elevations above 6,500 feet, boil for 3 minutes.")),
        item(s("source-21-010", "To kill germs, bring clear water to a rolling boil for 1 minute.", "At elevations above 6,500 feet, boil for 3 minutes.")),
        item(s("source-21-009", "You cannot make water containing harmful chemicals, toxins, or radioactive materials safe by boiling or disinfecting it.", "Use bottled water or a different source of water instead.")),
    ]
    rules["case-04"] = [item(s("source-09-007", q)) for q in [
        "Don’t keep going into unfamiliar terrain hoping to find your way.", "Stop and assess the situation.",
        "Unless you are certain of the way out, stay where you are.",
        "Make yourself and your group safe and comfortable – get warm, eat and drink, make a shelter, use first aid if needed.",
        "Call for help and make yourself visible."]]
    rules["case-05"] = [
        item(s("source-22-002", "If you hear thunder, lightning is close enough to strike you.")),
        item(s("source-22-002", "NO PLACE outside is safe when thunderstorms are in the area!!")),
        item(s("source-22-004", "Immediately get off elevated areas such as hills, mountain ridges or peaks")),
        item(s("source-22-004", "Never use a cliff or rocky overhang for shelter")),
        item(s("source-22-002", "When you hear thunder, immediately move to safe shelter: a substantial building with electricity or plumbing or an enclosed, metal-topped vehicle with windows up.")),
        item(s("source-22-004", "If you are caught outside with no safe shelter anywhere nearby the following actions may reduce your risk:") +
             s("source-22-002", "NO PLACE outside is safe when thunderstorms are in the area!!")),
    ]
    rules["case-06"] = [
        item(s("source-02-006", "Ring 113 ved større blødingar og blødingar du ikkje klarer å stoppe.")),
        item(s("source-02-007", "Trykk bandasje eller reint tøy direkte mot blødinga og bruk fingrane til å presse mot såret for å redusere blødinga mest mogleg.")),
        item(s("source-02-008", "Blør det gjennom bandasjen, legg du ein ny bandasje utanpå, med større press mot blødinga.")),
        item(s("source-02-009", "Pakk personen som er skadd, inn i varmt tøy eller teppe for å unngå nedkjøling .", "Overvak og ring 113 om personen blir sløvare eller noko endrar seg.")),
    ]
    rules["case-07"] = [
        item(s("source-03-006", "Avkjøl det skadede området med rennende vann i inntil 20 minutter.", "Vannet skal være litt kjølig (cirka 20 grader), men ikke iskaldt.")),
        item(s("source-03-006", "Vannet skal være litt kjølig (cirka 20 grader), men ikke iskaldt.", "Ikke bruk is, da dette kan skade huden ytterligere.")),
        item(s("source-03-006", "Ikke stikk hull på blemmer.")),
        item(s("source-03-007", "Kontakt lege hvis:", "ansikt, hender, føtter eller kjønnsorganer er skadet")),
    ]
    adult = s("source-01-004", "Gi fri luftvei ved å dra personens hake fremover i et underbitt.",
              "Bøy personens hode litt bakover og hold grepet (hodet og haken).",
              "Sjekk pusten ved å legge kinnet ditt nært munn og nese, og hør og føl etter varm luftstrøm.",
              "Se mot bryst og mage etter pustebevegelser.",
              "Bruk inntil 10 sekunder for å bestemme om det er normal pust eller ikke.")
    other_adult = s("source-07-004", "Dra personens hake fremover i et underbitt", "Bøy hodet litt bakover og hold grepet (hodet og haken)") + s(
        "source-07-005", "Legg kinnet ditt nært munn og nese, og hør og føl etter varm luftstrøm.",
        "Se mot bryst og mage etter pustebevegelser.", "Bruk inntil 10 sekunder for å bestemme om det er normal pust eller ikke.")
    rules["case-08"] = [
        item(s("source-07-001", "Finner du en bevisstløs person må du ringe 113.", "De vil hjelpe deg med å gi fri luftvei og legge personen i sideleie."),
             s("source-01-001", "Ring 113 dersom du finner en bevisstløs person.", "Medisinsk personell på 113 vil veilede og hjelpe deg helt til ambulansen kommer."),
             s("source-07-003", "Ring 113 hvis en person:", "er bevisstløs eller vanskelig å vekke, og du må riste og rope for å holde hen våken")),
        item(adult, other_adult),
        item(s("source-07-006", "Har du holdt fri luftvei og sett at den bevisstløse puster normalt, skal du legge den bevisstløse i sideleie:",
               "Bøy hodet bakover og pass på at personens munn er vinklet nedover.",
               "Personen skal ligge på siden, og ikke skli over i mageleie.", "Luftveien er fri ved at tungen sklir fremover slik at luft kan passere og væske renner ut.")),
        item(s("source-07-005", "Er det ingen eller unormal pust må du starte hjerte- og lungeredning .",
               "Er du usikker, be 113 høre lydene ved å holde telefonen nær personens munn.",
               "Forsikre deg om at pusten forblir normal, mens du holder fri luftvei og overvåker pusten.")),
    ]
    rules["case-09"] = [item(s("source-06-004", q)) for q in [
        "drikk rikeleg med vatn eller anna alkoholfri drikke", "reduser fysisk aktivitet",
        "dusj eller bad i kjølig vatn, eventuelt legg våte handklede på huda"]]
    rules["case-10"] = [
        item(s("source-10-004", "3. Pack warm clothes and extra food", heading=True) + s("source-10-004", "Prepare for bad weather and an unexpected night out.")),
        item(s("source-12-002", "Sleeping bag – 3–4 season"),
             s("source-12-002", "Survival kit including survival blanket, whistle, paper, pencil, high energy snack food")),
        item(s("source-12-002", "Emergency shelter"), s("source-12-006", "Tent")),
    ]
    rules["case-11"] = [
        item(s("source-21-015", "Aim to bury your poop deep in the soil, at least 8 inches, and at least 200 feet away from lakes, rivers, and other natural waters.")),
        item(s("source-21-015", "Make sure to bury poop downstream from where you or others collect water.")),
        item(s("source-21-016", "Wash your hands before handling food, eating, and after using the toilet.", "If soap and water are not available, use a hand sanitizer that contains at least 60% alcohol .")),
    ]
    rules["case-12"] = [
        item(s("source-14-005", "When you arrive at a river crossing, look for the warning signs of an unsafe river.", "If any are present, do not attempt a crossing.", "Murky: the water is discoloured, often brown.")),
        item(s("source-14-006", "Do not cross if:", "the river is flooded.", "you do not have the skills or experience to cross safely.", "If in doubt? Stay out.")),
        item(s("source-14-004", "You may encounter a dangerous river and need to turn back or wait until the river is safe to cross.")),
    ]
    rules["case-13"] = [
        item(s("source-11-003", "If you or someone else is in a life-threatening situation, set your beacon off .", "Situations can deteriorate rapidly.", "The sooner you activate it, the faster help can be sent to your location.")),
        item(s("source-11-003", "If you are unsure about when to activate the beacon, it is better to activate it and get help.")),
    ]
    rules["case-14"] = [
        item(s("source-15-001", "Faretegn (også kalt alarmtegn) er naturens måte å fortelle deg at det er skredfare i området.") +
             s("source-16-003", "Dersom faretegn og skredfarevurderinger forteller deg at den planlagte turen bør endres så er dette en enklere beslutning å ta dersom du og turfølget ditt allerede har planlagt og snakket sammen om dette.")),
        item(s("source-15-002", "Skredfarevurdering krever erfaring og kunnskap", "Unngå eller begrens ferdsel i skredterreng hvis du ikke har tilstrekkelig med kunnskap og erfaring.")),
    ]
    rules["case-15"] = []
    return {"schema_version": 1, "version": "1.0.0", "status": "pending_owner_review",
            "base_gold_sha256": BASE_HASH, "corpus_sha256": CORPUS_HASH,
            "policy": "Conservative source-authored sufficient certificates. No IDs decide coverage. All atoms required; absence -> needs_review; no semantic fail inferred. Alternatives not exhaustive. Never use holdout.",
            "rules": rules}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(definition(), ensure_ascii=False, indent=2))
