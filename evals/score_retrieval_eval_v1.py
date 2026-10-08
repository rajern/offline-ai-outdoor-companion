"""Inspectible manual semantic annotations for the single frozen A/B run.

No retrieval, generation or gold edits. Quotes identify evidence in already
retrieved context, not acceptable chunk IDs for future evaluation. Decisions
below were made by reading the actual delivered passages against frozen facts.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07"


def evidence(id, quote):
    return {"id": id, "quote": quote}


def yes(reason, *quotes):
    return {"covered": True, "reason": reason, "evidence": list(quotes)}


def no(reason, *partial_quotes):
    return {"covered": False, "reason": reason, "evidence": list(partial_quotes)}


def finding(id, quote, reason):
    return {"id": id, "quote": quote, "reason": reason}


def case(items, irrelevant=(), misleading=(), optional=(), notes=()):
    return {"items": items, "irrelevant": list(irrelevant), "potentially_misleading": list(misleading),
            "jurisdiction_leakage": [], "optional_observed": list(optional), "notes": list(notes),
            "jurisdiction_review": "Delivered content inspected: NO/general applicable passages only; no wrong-country operational/legal/service advice observed."}


def build_annotations():
    a = {}
    a["case-01"] = case([
        no("No fracture suspicion or inability-to-bear-weight criterion; context concerns ice rescue/preparation."),
        no("No statement distinguishing sprain and fracture."),
        no("No medical assessment for suspected fracture."),
        no("No ankle immobilisation/non-loading or warning that movement worsens injury/pain."),
    ], irrelevant=[finding("source-19-004", "Stå oppreist i vannet og legg armene eller albuene på vannkanten.", "Self-rescue from water/ice is unrelated to the ankle injury.")],
       notes=["Wrong document family, not merely a missing adjacent instruction section. Explicit ice context is retained; not marked as a source contradiction."])
    a["case-02"] = case([
        yes("Remove wet clothing explicitly.", evidence("source-05-004", "Fjern vått tøy raskt og systematisk")),
        yes("Warm insulation with both wind- and vapour-tight protection explicitly.", evidence("source-05-004", "Pakk personen inn i varmt, isolerende tøy eller materiale - slik at det blir vindtett og damptett")),
        yes("Apply external warmth without direct skin contact explicitly.", evidence("source-05-004", "Tilfør varme, som flasker med varmt vann (ikke direkte på huden)")),
        yes("Monitor consciousness and respiration explicitly.", evidence("source-05-004", "Overvåk bevissthet og pust")),
        yes("113 for guidance explicitly.", evidence("source-05-004", "Ring 113 for å få veiledning")),
    ], optional=["Go indoors if possible; fallback wind/vapour barrier when insulation absent; normal-breath monitoring/warm covering in source-07-007."],
       notes=["Primary treatment passage alone covers every item. Short preparation heading and cold/monitoring follow-up are not classified as misleading; no side-position procedure delivered in A."])
    a["case-03"] = case([
        yes("Clear-looking water can contain germs explicitly.", evidence("source-21-005", "Water containing germs that can make you sick—including bacteria, viruses, and parasites—sometimes looks clean.")),
        yes("Treat water when safety uncertain explicitly.", evidence("source-21-002", "If you are not sure whether the water you are using is safe to drink, treat it to remove germs.")),
        no("No boiling procedure, duration or altitude condition retrieved."),
        no("No three-minute high-altitude boiling instruction retrieved."),
        no("No chemical/toxin limitation or alternative water-source instruction retrieved."),
    ], irrelevant=[finding("source-20-003", "Rydd hagen: Flytt verdisaker som møbler, grill og løse gjenstander/materialer.", "Household flood/property preparation is unrelated to treating stream drinking water.")],
       optional=["Filter then disinfect mentioned as the next-best treatment method."],
       notes=["Correct CDC article and risk overview do not supply its separate Boil/Treat your water instruction sections."])
    a["case-04"] = case([
        no("No context returned."), no("No context returned."), no("No context returned."),
        no("No context returned."), no("No context returned."),
    ], notes=["No candidate meets the existing production cosine threshold; no refusal/generation behaviour scored."])
    a["case-05"] = case([
        yes("Audible thunder means lightning close enough to strike.", evidence("source-22-002", "If you hear thunder, lightning is close enough to strike you.")),
        yes("No safe outdoor place explicitly.", evidence("source-22-002", "NO PLACE outside is safe when thunderstorms are in the area!!")),
        no("No explicit instruction to leave ridges/peaks/high terrain."),
        no("No explicit exclusion of cliff overhangs as lightning shelter; general outdoor-unsafety alone is not the specific required fact."),
        yes("Full acceptable building or enclosed metal-roof vehicle with windows up condition retrieved.", evidence("source-22-002", "When you hear thunder, immediately move to safe shelter: a substantial building with electricity or plumbing or an enclosed, metal-topped vehicle with windows up.")),
        no("No outdoor last-resort risk-reduction guidance/qualification; general no-place-outside-is-safe supplies item 2, not the whole conjunction in item 6.", evidence("source-22-002", "NO PLACE outside is safe when thunderstorms are in the area!!")),
    ], irrelevant=[finding("source-09-007", "Stop and assess the situation. Unless you are certain of the way out, stay where you are.", "Lost-person stay-put/navigation scenario was not asked; explicit If you get lost heading retained, so not counted as a source contradiction.")],
       optional=["Remain in safe shelter 30 minutes after last thunder."],
       notes=["Conservative semantic judgement: an owner could regard general outdoor-unsafety as covering overhang exclusion or the final safety qualification. No implied instruction is awarded here; frozen per-item requirements retained."])
    a["case-06"] = case([
        no("No instruction to call 113 for major/uncontrolled bleeding."),
        yes("Direct dressing/clean-cloth pressure with fingers explicitly.", evidence("source-02-007", "Trykk bandasje eller reint tøy direkte mot blødinga og bruk fingrane til å presse mot såret for å redusere blødinga mest mogleg.")),
        yes("New dressing outside old one with increased pressure, not removal.", evidence("source-02-008", "Blør det gjennom bandasjen, legg du ein ny bandasje utanpå, med større press mot blødinga.")),
        no("No warming, monitoring or notification on deterioration."),
    ], irrelevant=[finding("source-02-010", "Dersom såret spriker, klemmer du det saman og set eit plaster eller strips på tvers av såret.", "Minor-cut closure is distracting during described major bleeding.")],
       misleading=[finding("source-02-010", "Du kan stoppe mindre blødingar ved å trykkje eit reint tøystykke hardt mot såret i 5–10 minutt.", "Wrong-severity waiting/minor-bleed procedure is delivered without required major-bleeding escalation. Potential misapplication, not a claim that the source's minor-bleeding instruction is false.")],
       optional=["Lie down/elevate if possible; retain embedded objects; extra pressure using a hard object over dressing."])
    a["case-07"] = case([
        no("No adult burn running-water cooling temperature or duration."),
        no("No prohibition on ice/ice-cold water for burns."),
        no("Blisters described, but no instruction not to puncture."),
        no("Medical contact for deep burns only; hand-specific assessment criterion absent.", evidence("source-03-005", "Ved mistanke om dyp brannskade skal du alltid kontakte lege.")),
    ], irrelevant=[finding("source-21-010", "To kill germs, bring clear water to a rolling boil for 1 minute.", "Drinking-water boiling is not burn first aid.")],
       misleading=[finding("source-02-012", "Vask såret og huda rundt såret i lunka vatn eller sårvatn.", "Abrasion/cut washing advice is wrong-injury actionable context while the burn cooling procedure is absent; potential misapplication, not a false statement about abrasions.")],
       notes=["Burn-source cream/ointment conflict is non-scoring and does not affect success or noise. Neither A nor B retrieves the conflicting burn-treatment passages. Irrelevant abrasion washing is assessed independently, not its ointment advice."])
    a["case-08"] = case([
        yes("Call 113 for unconsciousness explicitly.", evidence("source-07-003", "Ring 113 hvis en person:"), evidence("source-07-003", "er bevisstløs eller vanskelig å vekke, og du må riste og rope for å holde hen våken")),
        no("Full adult airway/see-listen-feel assessment up to 10 seconds absent. Child airway advice is not acceptable substitution; also lacks timing.", evidence("source-01-010", "Sjekk om barnet puster normalt; se, føl, lytt etter pust.")),
        yes("Normal-breath condition, stable side position, free airway and downward mouth explicitly.", evidence("source-07-006", "Har du holdt fri luftvei og sett at den bevisstløse puster normalt, skal du legge den bevisstløse i sideleie:"), evidence("source-07-006", "Bøy hodet bakover og pass på at personens munn er vinklet nedover."), evidence("source-07-006", "Personen skal ligge på siden, og ikke skli over i mageleie."), evidence("source-07-006", "Luftveien er fri ved at tungen sklir fremover slik at luft kan passere og væske renner ut.")),
        no("No continuing breath monitoring plus absent/abnormal-breath CPR branch and 113 clarification."),
    ], irrelevant=[finding("source-01-010", "Legg barnet på hardt underlag.", "Child procedure in an explicitly adult case.")],
       misleading=[finding("source-01-010", "Dra haken fram i et underbitt.", "Actionable paediatric airway assessment competes with a missing adult assessment protocol; age heading remains visible, so this is potential wrong-age application, not falsely labelled adult text.")],
       optional=["Detailed side-position arm/knee placement and insulating clothing under the person."])
    a["case-09"] = case([
        yes("Plenty of water/non-alcoholic fluid explicitly.", evidence("source-06-004", "drikk rikeleg med vatn eller anna alkoholfri drikke")),
        yes("Reduce activity explicitly.", evidence("source-06-004", "reduser fysisk aktivitet")),
        yes("Cool water/wet towels/cool surroundings explicitly.", evidence("source-06-004", "dusj eller bad i kjølig vatn, eventuelt legg våte handklede på huda"), evidence("source-06-004", "opphald deg i kjølige rom")),
    ], irrelevant=[finding("source-06-006", "Helse- og omsorgstenestene kan evakuere utsette personar og sørgje for å dekke dei grunnleggjande behova, som riktig temperatur, mat og drikke.", "Municipal care-service evacuation is extraneous to prevention on a group hike.")],
       optional=["Light/airy/light-coloured clothing; risk groups and strenuous-exertion heat risk."],
       notes=["Preferred prevention passage alone is sufficient; extra source text neither improves coverage nor invalidates complete must-have pass. Noise remains a separate metric."])
    a["case-10"] = case([
        yes("Delivered Tema heading explicitly says Pack warm clothes and extra food; its body explicitly covers bad weather/unexpected night. Both visible together satisfy the first item.", evidence("source-10-004", "Prepare for bad weather and an unexpected night out.")),
        no("No sleeping bag or survival-insulation gear retrieved; post-ice dry clothing/mat and an introduction referring to an unshown gear list do not supply the required equipment."),
        no("No emergency shelter/tent/equivalent shelter equipment information."),
    ], irrelevant=[finding("source-19-005", "Det beste er nok likevel å holde seg i bevegelse for å sette i gang egenproduksjonen av varme.", "Post-ice-rescue treatment is not packing advice for a possible overnight stay; scenario heading is preserved.")],
       optional=["Dry hat and sleeping mat/ground insulation mentioned, but in post-ice-rescue rather than an overnight gear context."],
       notes=["Sleeping mat deliberately optional and not needed for a pass. Header evidence is actually serialized in context.txt as Tema, not merely hidden metadata."])
    a["case-11"] = case([
        no("Burying waste mentioned, but minimum 8 inches depth and 200 feet from natural water absent.", evidence("source-21-008", "Treating your water, burying your poop if toilets are not available, and washing your hands can help you avoid getting and spreading germs.")),
        no("No downstream-of-water-collection condition."),
        yes("Before food/after toilet hygiene and minimum 60% alcohol fallback explicitly.", evidence("source-21-016", "Wash your hands before handling food, eating, and after using the toilet. If soap and water are not available, use a hand sanitizer that contains at least 60% alcohol .")),
    ], irrelevant=[finding("source-20-003", "Rydd kjeller, garasje og første etasje : Flytt gjenstander opp fra gulv, dersom det er en risiko for at vann kan komme inn.", "Household flooding preparation is unrelated to toilet/water hygiene.")])
    a["case-12"] = case([
        no("No brown/discoloured-water unsafe-river sign and resulting do-not-cross instruction."),
        no("Flood/high-flow avoidance is present, but doubts and lack-of-skill/experience stop conditions absent; incomplete composite item.", evidence("source-20-005", "Frarådes det å oppholde seg i nærheten av og kryssing av elver og bekker med stor vannføring eller isgang.")),
        yes("Wait or turn back rather than force an unsafe crossing explicitly.", evidence("source-14-004", "You may encounter a dangerous river and need to turn back or wait until the river is safe to cross.")),
    ], irrelevant=[finding("source-20-003", "Rydd hagen: Flytt verdisaker som møbler, grill og løse gjenstander/materialer.", "Property flood mitigation is not a hiking crossing decision.")],
       optional=["Emergency shelter/food and backup-route preparation."],
       notes=["The second gold item is evaluated strictly across all specified conditions; safe flood guidance alone does not satisfy the missing inexperienced-user/doubt conditions."])
    a["case-13"] = case([
        no("Urgent 113 advice present but no distress-beacon activation/life-threatening trigger/deterioration/earlier-help instruction."),
        no("No instruction to activate beacon if unsure rather than delay."),
    ], irrelevant=[finding("source-01-027", "Tror du at tilstanden er farlig eller lett kan bli det, skal du straks ringe medisinsk nødtelefon 113.", "Three near-duplicate phone-call passages do not address the available beacon when no mobile coverage exists.")],
       misleading=[finding("source-01-027", "skal du straks ringe medisinsk nødtelefon 113", "Phone-only operational guidance assumes an unavailable communication channel in this scenario; the frozen case explicitly identifies it as an inappropriate substitute for beacon activation.")],
       notes=["No wrong-jurisdiction leakage: 113 is Norwegian. This is scenario/channel mismatch, not geography."])
    a["case-14"] = case([
        yes("Only supported subset: danger signs signal avalanche danger and may change planned tour selection.", evidence("source-15-001", "Faretegn (også kalt alarmtegn) er naturens måte å fortelle deg at det er skredfare i området."), evidence("source-15-001", "Det vanskeligste å lære er hvordan du kan bruke faretegnene til å tilpasse turvalget.")),
        no("Knowledge needed to interpret signs partially implied, but avoidance/limiting avalanche terrain without competence not retrieved; incomplete supported subset."),
    ], irrelevant=[finding("source-19-003", "Når du går gjennom isen må du kjempe for å unngå at hodet kommer under vann.", "Ice self-rescue is unrelated to avalanche signs/retreat."), finding("source-17-005", "Under finner du lenker til fortellingen om to skredhendelser", "Accident-story links are not the requested sign interpretation or retreat procedure.")],
       notes=["Insufficient coverage in KB: no explicit whumph/crack interpretation or operational retreat. 1/2 supported-subset items present, never a full-answer pass. No generation/abstention judgement."])
    a["case-15"] = case([], irrelevant=[finding("source-21-010", "To kill germs, bring clear water to a rolling boil for 1 minute.", "Water disinfection is not campfire legal permission."), finding("source-20-003", "Rydd hagen: Flytt verdisaker som møbler, grill og løse gjenstander/materialer.", "Property flood advice does not cover Norwegian fire law.")],
       notes=["No applicable Norwegian legal information; empty gold list yields no numerical coverage or pass. No NZ fire-rule leakage observed. Unrelated context remains, not a retrieval abstention test."])

    b = deepcopy(a)
    b["case-02"]["irrelevant"] = [finding("source-07-006", "Har du holdt fri luftvei og sett at den bevisstløse puster normalt, skal du legge den bevisstløse i sideleie:", "Full unconscious-person side-position procedure added to an awake, normally speaking cold-exposure scenario."), finding("source-05-005", "Det kan være nødvendig at du holder fri luftvei og sjekker pusten i et helt minutt", "Unconscious-hypothermia extended breath assessment is not needed for this awake scenario; explicit condition remains.")]
    b["case-02"]["notes"] = ["Same five facts as A; added irrelevant unconsciousness procedures. Preserved conditions mean no additional source contradiction scored."]
    b["case-06"]["items"][3] = yes("Expansion adds warmth, monitoring and 113 notification on deterioration.", evidence("source-02-009", "Pakk personen som er skadd, inn i varmt tøy eller teppe for å unngå nedkjøling ."), evidence("source-02-009", "Overvak og ring 113 om personen blir sløvare eller noko endrar seg."))
    b["case-06"]["items"][0] = no("113 only on worsening/sluggishness; no major/uncontrolled-bleeding initial call instruction. Different trigger is not full coverage.", evidence("source-02-009", "Overvak og ring 113 om personen blir sløvare eller noko endrar seg."))
    b["case-07"]["notes"].append("Expansion increases drinking-water treatment to six passages rather than reaching burn cooling/hand-assessment sections.")
    b["case-08"]["items"][3] = no("Monitoring added, but absent/abnormal-breath CPR branch and 113 clarification still absent; partial information scores zero.", evidence("source-07-007", "Overvåk og se etter normal pust mens du venter på ambulansen."))
    b["case-08"]["optional_observed"].append("Cover person warmly while waiting for ambulance.")
    b["case-13"]["irrelevant"].extend([
        finding("source-01-026", "Du kan også ringe på telefon: 02415.", "Aftercare phone service for first-aiders is unrelated during this active emergency."),
        finding("source-04-008", "De fleste brudd blir behandlet med gips.", "Wrist fracture/casting does not explain distress-beacon activation."),
        finding("source-03-007", "brannskaden ikke leger innen to uker", "Burn assessment/healing timeline unrelated to beacon decision."),
    ])
    b["case-15"]["notes"].append("Expanded nine chunks still contain no applicable fire-law guidance; extra water-treatment text is not a bonus or a legal answer.")
    return {"A": a, "B": b}


if __name__ == "__main__":
    target = OUTPUT / "scoring.json"
    if target.exists():
        raise RuntimeError("Refusing to overwrite existing manual scoring")
    rows = json.loads((OUTPUT / "retrieved-all.json").read_text(encoding="utf-8"))
    # Check delivered heading evidence explicitly, rather than scoring hidden metadata.
    for mode in ["A", "B"]:
        context = (OUTPUT / mode / "case-10/context.txt").read_text(encoding="utf-8")
        assert "Tema: Five simple steps / 3. Pack warm clothes and extra food" in context
        for row in (r for r in rows if r["configuration"] == mode):
            for excerpt in row["excerpts"]:
                m = excerpt["item"]["metadata"]
                assert m["jurisdiction"] in ["NO", "general"]
    target.write_text(json.dumps(build_annotations(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "scoring-authoring.sha256").write_text(hashlib.sha256(Path(__file__).read_bytes()).hexdigest() + "\n", encoding="utf-8")
    print(f"Manual annotations saved: {target}")
