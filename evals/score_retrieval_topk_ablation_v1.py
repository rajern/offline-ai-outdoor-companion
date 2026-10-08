"""Manual information-based scoring of the frozen, completed B3/B8 run.

No retrieval or generation. B3 annotations are copied unchanged from the prior
evaluation; B8 decisions refer only to passages in the delivered B8 context.
Evidence IDs locate quotes for audit, not gold-required chunk identities.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07"
OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-topk-ablation-v1-2026-10-07"


def evidence(id, quote):
    return {"id": id, "quote": quote}


def yes(reason, *quotes):
    return {"covered": True, "reason": reason, "evidence": list(quotes)}


def finding(id, quote, reason):
    return {"id": id, "quote": quote, "reason": reason}


def annotations():
    b3 = json.loads((BASE / "scoring.json").read_text(encoding="utf-8"))["B"]
    b8 = deepcopy(b3)
    b8["case-02"]["irrelevant"].append(finding("source-21-007", "Common symptoms caused by drinking unsafe water when hiking, camping, or traveling include:", "Waterborne illness is unrelated to this cold-exposure scenario."))
    b8["case-02"]["optional_observed"].append("Hypothermia symptom/severity descriptions and survival insulation equipment.")
    b8["case-02"]["notes"].append("Post-ice-rescue movement advice retains its specific heading; not scored as a direct contradiction of this awake cold-person case. Potential-misleading labels are manual risk judgements, not generation errors.")

    boil = evidence("source-21-010", "To kill germs, bring clear water to a rolling boil for 1 minute. At elevations above 6,500 feet, boil for 3 minutes.")
    b8["case-03"]["items"][2] = yes("Complete rule implies the one-minute rule at elevations up to 6,500 feet; the explicit above-6,500-foot exception is also delivered. No unknown-altitude assumption.", boil)
    b8["case-03"]["items"][3] = yes("Three-minute high-altitude exception explicitly present.", boil)
    b8["case-03"]["items"][4] = yes("All chemical/toxin/radiation limitations and alternative-water instruction present.", evidence("source-21-009", "You cannot make water containing harmful chemicals, toxins, or radioactive materials safe by boiling or disinfecting it. Use bottled water or a different source of water instead."))
    b8["case-03"]["notes"] = ["The rank-5 Disinfect seed expands the unchanged Treat your water branch, supplying the rank-11 Boil and rank-13 chemical-limit passages. The final context, not their direct seed ranks, determines coverage.", "Full altitude rule retained; original question and gold unchanged. Property-flood noise from B3 remains."]

    b8["case-05"]["items"][2] = yes("Leave elevated terrain explicitly present.", evidence("source-22-004", "Immediately get off elevated areas such as hills, mountain ridges or peaks"))
    b8["case-05"]["items"][3] = yes("Explicit overhang exclusion now present; no change to earlier conservative judgement.", evidence("source-22-004", "Never use a cliff or rocky overhang for shelter"))
    b8["case-05"]["items"][5] = yes("Last-resort actions are explicitly qualified as risk reduction only, jointly with the existing statement that no outdoor place is safe.", evidence("source-22-004", "If you are caught outside with no safe shelter anywhere nearby the following actions may reduce your risk:"), evidence("source-22-002", "NO PLACE outside is safe when thunderstorms are in the area!!"))
    b8["case-05"]["notes"] = ["Rank-8 last-resort passage supplies all three missing items; supporting sources not required. Existing unrelated lost-person instructions and added avalanche/flood material remain noise."]

    b8["case-06"]["notes"].append("Added 113 wording for internal bleeding is a different clinical trigger; it does not meet initial major/uncontrolled external-bleeding escalation. No new must-have coverage.")
    b8["case-07"]["items"][3] = yes("Hand-specific assessment condition explicitly present with contact-doctor instruction.", evidence("source-03-007", "Kontakt lege hvis:"), evidence("source-03-007", "ansikt, hender, føtter eller kjønnsorganer er skadet"))
    b8["case-07"]["notes"] = ["Cream/ointment advice excluded from gold and noise scoring. The burn treatment branch is NOT in delivered context: seed rank 5 would make the prompt 2,162 tokens and is atomically rejected. Cooling/no-ice/no-puncture therefore remain uncovered despite their presence in the rejected candidate.", "Hand-assessment branch at rank 4 fits. Unrelated water-treatment and abrasion-washing context inherited from B3 remains."]
    b8["case-08"]["potentially_misleading"].append(finding("source-05-005", "sjekker pusten i et helt minutt", "Hypothermia-specific one-minute breathing assessment competes with missing adult ten-second assessment. Specific hypothermia condition is visible: potential scenario misapplication, not false source guidance."))
    b8["case-08"]["notes"].append("Added baby airway and unconscious-hypothermia protocols do not satisfy the ordinary adult assessment/HLR requirements; exact necessary conditions remain missing.")
    b8["case-09"]["potentially_misleading"].append(finding("source-19-005", "Det beste er nok likevel å holde seg i bevegelse for å sette i gang egenproduksjonen av varme.", "Cold/post-ice advice to move and produce warmth is explicitly inappropriate for this heat-prevention case and opposes its reduce-activity instruction. The ice-rescue heading remains visible; this flags potential misapplication, not an observed generated error."))
    b8["case-09"]["notes"].append("Must-have pass unchanged, but higher-k adds cold-rescue movement advice and unrelated drinking-water/avalanche context. Optional material cannot compensate for this noise.")

    b8["case-10"]["items"][1] = yes("Actual sleeping bag and survival insulation equipment retrieved.", evidence("source-12-002", "Sleeping bag – 3–4 season"), evidence("source-12-002", "Survival kit including survival blanket, whistle, paper, pencil, high energy snack food"))
    b8["case-10"]["items"][2] = yes("Emergency shelter equipment explicitly listed.", evidence("source-12-002", "Emergency shelter"))
    b8["case-10"]["notes"] = ["Rank-6 actual equipment list provides both missing facts. Sleeping mat remains optional, never a pass requirement. Existing ice-treatment and added avalanche/lightning/navigation material remain noise."]

    b8["case-11"]["items"][0] = yes("Both minimum depth and distance from natural waters explicitly present.", evidence("source-21-015", "Aim to bury your poop deep in the soil, at least 8 inches, and at least 200 feet away from lakes, rivers, and other natural waters."))
    b8["case-11"]["items"][1] = yes("Downstream from water collection explicitly present.", evidence("source-21-015", "Make sure to bury poop downstream from where you or others collect water."))
    b8["case-11"]["irrelevant"].append(finding("source-03-006", "Ikke bruk is, da dette kan skade huden ytterligere.", "Burn first aid is unrelated to toilet hygiene. Cream/ointment conflict is not used in this noise judgement."))
    b8["case-11"]["notes"].append("Rank-4 burial passage supplies both missing items. No primary/supporting source-count requirement. Hypothermia and burn treatment branches add substantial unrelated text.")

    b8["case-12"]["items"][0] = yes("Explicit brown/murky-water danger sign plus do-not-cross condition both present.", evidence("source-14-005", "If any are present, do not attempt a crossing."), evidence("source-14-005", "Murky: the water is discoloured, often brown."))
    b8["case-12"]["items"][1] = yes("Flood, inadequate skills/experience and doubt stop conditions all explicitly present.", evidence("source-14-006", "the river is flooded."), evidence("source-14-006", "you do not have the skills or experience to cross safely."), evidence("source-14-006", "If in doubt? Stay out."))
    b8["case-12"]["notes"] = ["Rank-4 stop-conditions and rank-7 brown-water warning complete coverage; general DOC river-safety passages are applicable, not NZ legal/operational leakage. Flood-property and ice-rescue noise remains."]
    b8["case-13"]["notes"].append("An incidental carry-a-distress-beacon packing mention is not the required activation policy; neither must-have covered. Added phone-only/side-position/allergy advice does not substitute for activation without mobile coverage.")
    b8["case-14"]["notes"] = ["Insufficient-coverage case remains separate: 1/2 supported-subset items present, no full-answer pass. Extra ice guidance does not supply avalanche competence/retreat instructions. No generation/abstention scored."]
    b8["case-15"]["notes"] = ["Insufficient coverage: no applicable Norwegian fire-law passage, zero numeric coverage/pass assigned. No NZ fire-law leakage; more water treatment text remains unrelated. No generation/abstention scored."]
    return {"B3": b3, "B8": b8}


def main():
    target = OUTPUT / "scoring.json"
    if target.exists():
        raise RuntimeError("Refusing to overwrite existing scoring")
    scores = annotations()
    rows = json.loads((OUTPUT / "retrieved-all.json").read_text(encoding="utf-8"))
    offsets = deepcopy(scores)
    budget = []
    for row in rows:
        mode, cid = row["configuration"], row["case_id"]
        text = {e["item"]["id"]: e["item"]["text"] for e in row["excerpts"]}
        for e in row["excerpts"]:
            assert e["item"]["metadata"]["jurisdiction"] in ["NO", "general"]
        annotation = offsets[mode][cid]
        for group in [*[item["evidence"] for item in annotation["items"]], annotation["irrelevant"], annotation["potentially_misleading"], annotation["jurisdiction_leakage"]]:
            for ev in group:
                assert ev["quote"] in text[ev["id"]], (mode, cid, ev)
                start = text[ev["id"]].index(ev["quote"])
                ev["start_char"], ev["end_char"] = start, start + len(ev["quote"])
        for trace in row["trace"]:
            if trace["status"] == "over_budget":
                budget.append({"configuration": mode, "case_id": cid, **trace,
                               "necessary_information_lost": ["Adult burn cooling", "No ice/ice-cold water", "Do not puncture blisters"] if mode == "B8" and cid == "case-07" and trace["seed_id"] == "source-03-006" else [],
                               "note": "Rejected candidate, NOT delivered context; never counted toward coverage."})
    target.write_text(json.dumps(scores, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "scoring-with-offsets.json").write_text(json.dumps(offsets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "budget-analysis.json").write_text(json.dumps(budget, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "scoring-authoring.sha256").write_text(hashlib.sha256(Path(__file__).read_bytes()).hexdigest() + "\n", encoding="utf-8")
    print("Saved manual scoring, validated quote offsets and rejected-packet audit. No retrieval rerun.")


if __name__ == "__main__":
    main()
