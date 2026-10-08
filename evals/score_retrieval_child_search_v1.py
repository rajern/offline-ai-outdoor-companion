"""Manual semantic scoring of the single frozen C8 run; never retrieves.

Saved B8 annotations remain unchanged. Every C8 case was inspected against the
frozen information-based criteria, including alternate relevant context. Quotes
locate audit evidence, not required gold chunk IDs. Missing partial facts earn zero.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "knowledge/local/diagnostics/retrieval-topk-ablation-v1-2026-10-07"
OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-child-search-v1-2026-10-07"


def ev(id, quote):
    return {"id": id, "quote": quote}


def no(reason, *evidence):
    return {"covered": False, "reason": reason, "evidence": list(evidence)}


def finding(id, quote, reason):
    return {"id": id, "quote": quote, "reason": reason}


def annotations(rows):
    b8 = json.loads((BASE / "scoring.json").read_text(encoding="utf-8"))["B8"]
    c8 = deepcopy(b8)
    for row in (r for r in rows if r["configuration"] == "C8"):
        cid = row["case_id"]
        delivered = {e["item"]["id"] for e in row["excerpts"]}
        for item in c8[cid]["items"]:
            # Only remove stale partial quotations; positive losses are explicitly
            # adjudicated below, not scored by automatic chunk identity matching.
            if not item["covered"]:
                item["evidence"] = [e for e in item["evidence"] if e["id"] in delivered]
        for label in ["irrelevant", "potentially_misleading", "jurisdiction_leakage"]:
            c8[cid][label] = [e for e in c8[cid][label] if e["id"] in delivered]
        c8[cid]["notes"] = []
        c8[cid]["optional_observed"] = []
    c8["case-01"]["items"][3] = no("RICE supplies rest/non-loading but does not explicitly supply movement worsening the injury/pain; incomplete composite item remains zero. No fracture-specific assessment/suspicion context delivered.", ev("source-04-003", "Hold kroppsdelen som er skadet i ro. Unngå å belaste området som er skadet og finn en behagelig stilling."))
    c8["case-01"]["notes"] = ["No full must-have gain. Relevant RICE is partial, not a substitute for fracture assessment. Extra side-position and ice-rescue procedures are unrelated. Gradual reloading remains explicitly conditioned on recovery, not scored as an unconditional unsafe instruction."]
    c8["case-01"]["optional_observed"] = ["RICE rest/non-loading, cooling/compression/elevation; these do not complete fracture gold."]
    c8["case-02"]["notes"] = ["Same delivered passage set as B8, with different seed ranking. Five facts unchanged; no bonus for fully represented child text or extra sources.", "Explicitly conditioned post-ice movement text remains a possible owner-review ambiguity, not scored as a direct contradiction for this awake cold-exposure case."]
    c8["case-03"]["notes"] = ["All five facts remain delivered. Chemical-warning child improves from original parent rank 13 to child rank 5; existing branch expansion also brings boiling. Handled full altitude rule unchanged. Property-flood noise persists."]
    c8["case-04"]["items"] = [no("No required lost-person action in delivered avalanche/unconscious-person passages.") for _ in range(5)]
    c8["case-04"]["irrelevant"] = [finding("source-15-001", "Vurdering av snødekket", "Avalanche danger assessment is unrelated to being lost in fog; it is not the required stop/stay-put action."), finding("source-07-003", "Vurder bevissthet ved å snakke til personen.", "Medical consciousness assessment is not a lost-group procedure.")]
    c8["case-04"]["notes"] = ["Unlike empty B8 context, C8 returns unrelated material. The correct unchanged lost-person passage remains below threshold; no new must-have coverage or abstention judgement."]
    c8["case-05"]["notes"] = ["All six facts remain covered, no implicit-coverage relaxation. Last-resort parent improves rank 8 to best child rank 5. More household flood text enters; context remains noisy."]
    c8["case-06"]["notes"] = ["Three facts remain covered. Added fracture/neck/back/hip 113 advice and internal-bleeding 113 mention are different triggers, not the required major external-bleeding initial escalation."]
    c8["case-07"]["notes"] = ["Same delivered passage set and one covered hand-assessment item as B8. Treatment child is selected at rank 7 but its original treatment parent branch would make the prompt 2,246 tokens and is rejected. Cooling/no-ice/no-puncture remain missing from actual context.", "The previously truncated no-puncture statement is now fully represented in another child at rank 10. Cream/ointment conflict remains excluded from both pass/fail and noise; no new safety policy is inferred."]
    c8["case-08"]["notes"] = ["Two facts remain covered. Normal-breath monitoring is present, but missing adult assessment and abnormal/absent-breath HLR/113 conjunction still scores zero. Hypothermia-specific one-minute procedure disappeared; child/baby procedure risk remains.", "Three duplicate-parent child hits consume slots. The adult assessment alternative is child rank 11 but projected unique-parent rank 8; this projection is diagnostic only, not an evaluated third configuration."]
    c8["case-09"]["notes"] = ["All three prevention facts retained. Cold/ice movement advice remains potentially misleading in the heat scenario; rejected hypothermia packet is not counted as delivered context."]
    c8["case-10"]["notes"] = ["All three facts retained. Best equipment child improves rank 6 to 4; the shelter-tail child itself is rank 26, but full original parent context includes it. Parent hit is not claimed to prove that the shelter statement matched semantically.", "Sleeping mat remains optional. Avalanche/ice/lightning/navigation material remains unrelated."]
    c8["case-11"]["notes"] = ["All three facts retained. Burial passage remains rank 4 and unchanged. Unrelated burn branch disappears, but flood and hypothermia text remains. No noise flag based on cream/ointment conflict."]
    c8["case-12"]["items"][0] = no("No brown/murky-water danger sign and corresponding do-not-cross condition in delivered context. Flood/high-water avoidance does not replace this explicitly required fact.")
    c8["case-12"]["notes"] = ["Regression 3/3 to 2/3: unchanged brown-water warning score is 0.414866, above threshold, but child rank 11 / unique-parent projection 10. It is never selected, not budget-rejected. Full stop conditions and wait/turn-back remain covered.", "New lightning and ice-rescue text is unrelated; preserved scenario headings are not automatically treated as direct contradictions."]
    c8["case-13"]["notes"] = ["No full activation criterion retrieved. Product/device comparison and activate-in-emergencies mention do not supply life-threatening trigger plus deterioration/earlier help, or the activate-if-unsure rule. Phone-only operational mismatch remains.", "A correct document hit (new beacon device comparison) is not a sufficient activation passage. Actual activation passage is unchanged, child rank 23 / unique-parent projection 22."]
    c8["case-13"]["irrelevant"].append(finding("source-11-005", "Knowing the difference between a PLB and SEND", "Device-type comparison is not the requested activation decision during a life-threatening situation."))
    c8["case-14"]["notes"] = ["Separate insufficient-coverage case remains 1/2 on the supported subset. New planning says avoid the most exposed avalanche terrain, but does not explicitly establish the full competence-dependent avoidance requirement. No full-answer pass, missing whumph/crack interpretation and retreat unchanged."]
    c8["case-14"]["irrelevant"].append(finding("source-17-003", "Dersom du er alene om å kunne søke etter den eller de som er tatt av skred, skal du lete før du bruker tid på å varsle om skredet.", "Companion rescue/search timing is not the asked sign interpretation/retreat when nobody is stated to be buried. Explicit rescue condition preserved."))
    c8["case-15"]["notes"] = ["Separate insufficient-coverage case: no Norwegian campfire law, no numeric coverage/pass assigned, no NZ fire-law leakage. Added Norwegian flood-administration text is unrelated, not applicable fire law. No generation/abstention scored."]
    return {"B8": b8, "C8": c8}


def main():
    target = OUTPUT / "scoring.json"
    if target.exists():
        raise RuntimeError("Refusing to overwrite existing manual scoring")
    rows = json.loads((OUTPUT / "retrieved-all.json").read_text(encoding="utf-8"))
    scores = annotations(rows)
    offsets = deepcopy(scores)
    budget = []
    for row in rows:
        mode, cid = row["configuration"], row["case_id"]
        text = {e["item"]["id"]: e["item"]["text"] for e in row["excerpts"]}
        for e in row["excerpts"]:
            assert e["item"]["metadata"]["jurisdiction"] in ["NO", "general"]
        score = offsets[mode][cid]
        for group in [*[i["evidence"] for i in score["items"]], score["irrelevant"], score["potentially_misleading"], score["jurisdiction_leakage"]]:
            for e in group:
                assert e["quote"] in text[e["id"]], (mode, cid, e)
                start = text[e["id"]].index(e["quote"])
                e["start_char"], e["end_char"] = start, start + len(e["quote"])
        for t in row["trace"]:
            if t["status"] == "over_budget":
                budget.append({"configuration": mode, "case_id": cid, **t,
                               "necessary_information_excluded": ["Adult cooling conditions", "No ice/ice-cold water", "Do not puncture blisters"] if cid == "case-07" and t["seed_id"] == "source-03-006" else [],
                               "note": "Rejected candidate is not delivered context and receives no coverage credit."})
    target.write_text(json.dumps(scores, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "scoring-with-offsets.json").write_text(json.dumps(offsets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "budget-analysis.json").write_text(json.dumps(budget, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "scoring-authoring.sha256").write_text(hashlib.sha256(Path(__file__).read_bytes()).hexdigest() + "\n", encoding="utf-8")
    print("Validated and saved B8/C8 manual scoring; no retrieval rerun.")


if __name__ == "__main__":
    main()
