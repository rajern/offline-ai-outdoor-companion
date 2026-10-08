"""Manual information-based scoring of frozen C8 versus C8U8 contexts only.

All added excerpts were inspected. Saved C8 decisions remain unchanged.
No retrieval/generation; evidence IDs locate quotes, not chunk-based gold rules.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "knowledge/local/diagnostics/retrieval-child-search-v1-2026-10-07"
OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-parent-dedup-v1-2026-10-07"


def main():
    target = OUTPUT / "scoring.json"
    if target.exists():
        raise RuntimeError("Refusing to overwrite existing manual scoring")
    baseline = json.loads((BASE / "scoring.json").read_text(encoding="utf-8"))["C8"]
    candidate = deepcopy(baseline)
    quotes = ["Gi fri luftvei ved å dra personens hake fremover i et underbitt.",
              "Bøy personens hode litt bakover og hold grepet (hodet og haken).",
              "Sjekk pusten ved å legge kinnet ditt nært munn og nese, og hør og føl etter varm luftstrøm.",
              "Se mot bryst og mage etter pustebevegelser.",
              "Bruk inntil 10 sekunder for å bestemme om det er normal pust eller ikke."]
    candidate["case-08"]["items"][1] = {"covered": True,
        "reason": "Newly delivered original adult assessment passage explicitly supplies chin-forward/head-back, see/listen/feel and the full ten-second normal-breath assessment. Information matches frozen gold; preferred document identity not required.",
        "evidence": [{"id": "source-01-004", "quote": quote} for quote in quotes]}
    for finding in candidate["case-08"]["potentially_misleading"]:
        finding["reason"] = "Paediatric airway procedure remains wrong-age actionable context for an explicitly adult question, now alongside the correct adult procedure. Age heading remains visible: potential misapplication, not a false source statement or an observed generation error. Addition of adult evidence does not remove the child/baby excerpts."
    candidate["case-08"]["notes"].append("C8U8 adds the adult parent at unique-parent rank 8 (original child rank 11). Full-item coverage improves 2/4 to 3/4. Its ten-second tail is supplied by full parent packing, not the selected prefix child alone. Required absent/abnormal-breath HLR plus 113 clarification remains missing; complete case still fails.")
    candidate["case-08"]["optional_observed"].append("Additional 113/unconscious-person summary and near-duplicate 116117 contact passage; no coverage bonus for duplicated contact advice.")
    candidate["case-09"]["notes"].append("C8U8 adds avalanche-terrain avoidance text only; no must-have gain or new jurisdiction leakage. Existing cold/heat mismatch remains.")
    candidate["case-11"]["optional_observed"].append("Do not wash/use soap in lakes or streams, supplied by the newly added toiletries passage; optional, not core score.")
    candidate["case-11"]["notes"].append("C8U8 adds relevant optional water-hygiene advice, not new must-have information. Flood/hypothermia noise remains.")
    candidate["case-06"]["notes"].append("Newly selected ice-rescue parent is rejected by budget and never delivered; must-have/noise scoring unchanged.")
    candidate["case-07"]["notes"].append("C8U8 still rejects necessary treatment at 2,246 prompt tokens. New sprain/RICE packet is also rejected (2,370), so it creates no delivered-noise finding. Cream conflict stays non-scoring.")
    candidate["case-12"]["notes"].append("C8U8 selects an extra ice-rescue parent (budget-rejected), not the required brown-water warning, which is unique-parent rank 10. Case remains 2/3.")
    for cid in ["case-01", "case-02", "case-03", "case-04", "case-05", "case-10", "case-13", "case-14", "case-15"]:
        candidate[cid]["notes"].append("C8U8 delivered context is identical to C8; information/noise/gap scoring unchanged. Different selection/trace bookkeeping does not earn coverage.")
    scores = {"C8": baseline, "C8U8": candidate}
    with_offsets = deepcopy(scores)
    rows = json.loads((OUTPUT / "retrieved-all.json").read_text(encoding="utf-8"))
    rejected = []
    for row in rows:
        mode, cid = row["configuration"], row["case_id"]
        text = {e["item"]["id"]: e["item"]["text"] for e in row["excerpts"]}
        annotation = with_offsets[mode][cid]
        groups = [*[i["evidence"] for i in annotation["items"]], annotation["irrelevant"],
                  annotation["potentially_misleading"], annotation["jurisdiction_leakage"]]
        for group in groups:
            for evidence in group:
                assert evidence["quote"] in text[evidence["id"]], (mode, cid, evidence)
                start = text[evidence["id"]].index(evidence["quote"])
                evidence["start_char"], evidence["end_char"] = start, start + len(evidence["quote"])
        for e in row["excerpts"]:
            assert e["item"]["metadata"]["jurisdiction"] in ["NO", "general"]
        for trace in row["trace"]:
            if trace["status"] == "over_budget":
                rejected.append({"configuration": mode, "case_id": cid, **trace,
                                 "necessary_information_excluded": ["Adult burn cooling", "No ice", "No blister puncture"] if cid == "case-07" and trace["seed_id"] == "source-03-006" else [],
                                 "note": "Rejected packet is not delivered evidence; never counts toward coverage or delivered-noise metrics."})
    target.write_text(json.dumps(scores, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "scoring-with-offsets.json").write_text(json.dumps(with_offsets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "budget-analysis.json").write_text(json.dumps(rejected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "scoring-authoring.sha256").write_text(hashlib.sha256(Path(__file__).read_bytes()).hexdigest() + "\n", encoding="utf-8")
    print("Validated quotes and saved C8/C8U8 manual scoring; no retrieval rerun.")


if __name__ == "__main__":
    main()
