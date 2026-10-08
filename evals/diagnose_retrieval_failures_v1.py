"""Read-only candidate-landscape diagnosis of the frozen A/B failures.

Uses the existing index and saved ORIGINAL query vectors. No embedding model
inference, no new retrieval configuration, no prompt, no Qwen/tokenizer calls.
The embedding tokenizer is inspected only to locate already-existing truncation.
Authored evidence maps identify information in the corpus, not gold chunk IDs.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import sys

import numpy as np
from tokenizers import Tokenizer
import yaml
from fastembed.common.preprocessor_utils import load_tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from outwise.knowledge.loader import load_knowledge_items
from outwise.services.semantic_retrieval import allowed_in_jurisdiction

BASELINE = ROOT / "knowledge/local/diagnostics/retrieval-eval-v1-2026-10-07"
OUTPUT = ROOT / "knowledge/local/diagnostics/retrieval-failure-landscape-v1-2026-10-07"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def passage(id, *quotes):
    return {"id": id, "quotes": list(quotes)}


def point(index, *sufficient_sets):
    return {"gold_item_index": index, "sufficient_sets": list(sufficient_sets)}


def mapping():
    # Inspectible source-content judgements; not derived from ranking scores.
    return {
        "case-01": [
            point(1, [passage("source-04-005", "Hvis den skadde ikke klarer å stå på foten eller vri på armen, bør du mistenke brudd.")]),
            point(2, [passage("source-04-005", "Det er ikke alltid så lett å avgjøre om det er brudd eller ikke.")]),
            point(3, [passage("source-04-005", "Ta den skadde til lege eller legevakt hvis du mistenker brudd.")]),
            point(4, [passage("source-04-006", "Hold det skadede området helt i ro. Bevegelse kan gjøre skaden verre og øke smerten.")]),
        ],
        "case-03": [
            point(3, [passage("source-21-010", "To kill germs, bring clear water to a rolling boil for 1 minute. At elevations above 6,500 feet, boil for 3 minutes.")]),
            point(4, [passage("source-21-010", "At elevations above 6,500 feet, boil for 3 minutes.")]),
            point(5, [passage("source-21-009", "You cannot make water containing harmful chemicals, toxins, or radioactive materials safe by boiling or disinfecting it. Use bottled water or a different source of water instead.")]),
        ],
        "case-04": [
            point(1, [passage("source-09-007", "Don’t keep going into unfamiliar terrain hoping to find your way.")]),
            point(2, [passage("source-09-007", "Stop and assess the situation.")]),
            point(3, [passage("source-09-007", "Unless you are certain of the way out, stay where you are.")]),
            point(4, [passage("source-09-007", "Make yourself and your group safe and comfortable – get warm, eat and drink, make a shelter, use first aid if needed.")]),
            point(5, [passage("source-09-007", "Call for help and make yourself visible.")]),
        ],
        "case-05": [
            point(3, [passage("source-22-004", "Immediately get off elevated areas such as hills, mountain ridges or peaks")]),
            point(4, [passage("source-22-004", "Never use a cliff or rocky overhang for shelter")]),
            point(6, [passage("source-22-004", "If you are caught outside with no safe shelter anywhere nearby the following actions may reduce your risk:"),
                      passage("source-22-002", "NO PLACE outside is safe when thunderstorms are in the area!!")]),
        ],
        "case-06": [
            point(1, [passage("source-02-006", "Ring 113 ved større blødingar og blødingar du ikkje klarer å stoppe.")]),
            point(4, [passage("source-02-009", "Pakk personen som er skadd, inn i varmt tøy eller teppe for å unngå nedkjøling .", "Overvak og ring 113 om personen blir sløvare eller noko endrar seg.")]),
        ],
        "case-07": [
            point(1, [passage("source-03-006", "Avkjøl det skadede området med rennende vann i inntil 20 minutter. Vannet skal være litt kjølig (cirka 20 grader), men ikke iskaldt.")]),
            point(2, [passage("source-03-006", "Vannet skal være litt kjølig (cirka 20 grader), men ikke iskaldt.", "Ikke bruk is, da dette kan skade huden ytterligere.")]),
            point(3, [passage("source-03-006", "Ikke stikk hull på blemmer.")]),
            point(4, [passage("source-03-007", "Kontakt lege hvis:", "ansikt, hender, føtter eller kjønnsorganer er skadet")]),
        ],
        "case-08": [
            point(2,
                  [passage("source-01-004", "Gi fri luftvei ved å dra personens hake fremover i et underbitt.", "Bøy personens hode litt bakover og hold grepet (hodet og haken).", "Sjekk pusten ved å legge kinnet ditt nært munn og nese, og hør og føl etter varm luftstrøm.", "Se mot bryst og mage etter pustebevegelser.", "Bruk inntil 10 sekunder for å bestemme om det er normal pust eller ikke.")],
                  [passage("source-07-004", "Dra personens hake fremover i et underbitt", "Bøy hodet litt bakover og hold grepet (hodet og haken)"),
                   passage("source-07-005", "Legg kinnet ditt nært munn og nese, og hør og føl etter varm luftstrøm.", "Se mot bryst og mage etter pustebevegelser.", "Bruk inntil 10 sekunder for å bestemme om det er normal pust eller ikke.")]),
            point(4,
                  [passage("source-07-005", "Er det ingen eller unormal pust må du starte hjerte- og lungeredning . Er du usikker, be 113 høre lydene ved å holde telefonen nær personens munn.", "Forsikre deg om at pusten forblir normal, mens du holder fri luftvei og overvåker pusten.")],
                  [passage("source-07-007", "Overvåk og se etter normal pust mens du venter på ambulansen."),
                   passage("source-01-001", "Hvis en bevisstløs person ikke puster, eller har unormal pust, må du starte hjerte- og lungeredning (HLR). Ring 113 for hjelp,", "Medisinsk personell på 113 vil veilede og hjelpe deg helt til ambulansen kommer.")]),
        ],
        "case-10": [
            point(2, [passage("source-12-002", "Sleeping bag – 3–4 season", "Survival kit including survival blanket")]),
            point(3, [passage("source-12-002", "Emergency shelter")],
                  [passage("source-12-006", "Tent")],
                  [passage("source-14-004", "Packing an emergency shelter and extra food.")]),
        ],
        "case-11": [
            point(1, [passage("source-21-015", "If you are in a remote area without toilets, bury your poop to keep it from getting into water.", "Aim to bury your poop deep in the soil, at least 8 inches, and at least 200 feet away from lakes, rivers, and other natural waters.")]),
            point(2, [passage("source-21-015", "Make sure to bury poop downstream from where you or others collect water.")]),
        ],
        "case-12": [
            point(1, [passage("source-14-005", "If any are present, do not attempt a crossing.", "Murky: the water is discoloured, often brown.")]),
            point(2, [passage("source-14-006", "Do not cross if:", "the river is flooded.", "you do not have the skills or experience to cross safely.", "If in doubt? Stay out.")]),
        ],
        "case-13": [
            point(1, [passage("source-11-003", "If you or someone else is in a life-threatening situation, set your beacon off . Situations can deteriorate rapidly. The sooner you activate it, the faster help can be sent to your location.")]),
            point(2, [passage("source-11-003", "If you are unsure about when to activate the beacon, it is better to activate it and get help.")]),
        ],
    }


CATEGORIES = {
    "case-01": ("ranking / embedding", ["top_k / threshold", "multi-section requirement"],
                "Fracture suspicion/assessment passage ranks 20 and immobilisation 6, both below threshold; unrelated ice rescue outranks them. Lower threshold alone leaves fracture assessment far below top 3."),
    "case-03": ("ranking / embedding", ["multi-section requirement"],
                "Concrete Boil and chemical-limitation passages rank 11/13 behind flood/property and overview material; threshold is not excluding either. Full facts span several sections."),
    "case-04": ("top_k / threshold", [],
                "The independently verified complete lost-person instructions rank FIRST, but score 0.3353 is below 0.35. Threshold is the direct exclusion; no chunk truncation."),
    "case-05": ("top_k / threshold", ["multi-section requirement"],
                "Missing ridge/overhang/last-resort instructions are in one passage at rank 8, above threshold, outside top 3; retained general-lightning passage at rank 2 supplies its qualification. Near-cutoff classification is judgement, not model-quality proof."),
    "case-06": ("ranking / embedding", ["multi-section requirement"],
                "Initial major-bleeding 113 criterion is a short complete passage at rank 44/0.2331; monitoring ranks 22/0.2926. B recovered monitoring by expansion but not the independent escalation section."),
    "case-07": ("top_k / threshold", ["chunk / representation", "multi-section requirement"],
                "Both missing treatment/hand-assessment passages are immediately outside top 3 (ranks 5/4), above threshold. Blister-puncture prohibition exists in stored treatment text but is truncated out of BOTH indexed text views."),
    "case-08": ("ranking / embedding", ["chunk / representation", "top_k / threshold", "multi-section requirement"],
                "Adult full airway/breath alternative ranks 9 while child/baby instructions rank 3/5. Normal-pust decision/monitoring passage ranks 25 below threshold; its CPR/monitoring tail is excluded from both embedding views. Alternative short HLR passage also ranks 27 below threshold; representation alone is not proven to explain the ranking."),
    "case-10": ("top_k / threshold", ["multi-section requirement"],
                "Actual sleeping/survival-insulation and shelter list is at rank 6/0.4833, outside top 3; full necessary content exists in one stored passage. Gear-list introduction and links outrank equipment. Shelter tail is cut in title-context view but retained in body view, not total loss."),
    "case-11": ("top_k / threshold", ["multi-section requirement"],
                "Full burial depth/distance/downstream instructions are at rank 4/0.5839, fully token-visible and applicable; displaced by household flood text at rank 3."),
    "case-12": ("top_k / threshold", ["multi-section requirement"],
                "Doubt/inexperience and brown-water instructions at ranks 4/7, both above threshold and fully visible to embedder, outside top 3; existing wait/turn-back section alone is insufficient."),
    "case-13": ("ranking / embedding", [],
                "One short complete applicable beacon-activation passage ranks 16/0.3964, behind duplicated 113 phone-call passages. Neither multi-section collection nor truncation is needed to explain this failure."),
}


def main():
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite diagnostic artifacts: {OUTPUT}")
    frozen = json.loads((BASELINE / "frozen-run.json").read_text(encoding="utf-8"))
    protected = {name: sha(ROOT / name) for name in frozen["protected_before"]}
    assert protected == frozen["protected_before"], "Current protected inputs differ from frozen evaluation"
    gold = yaml.safe_load((ROOT / "evals/retrieval_cases.v1.yaml").read_text(encoding="utf-8"))
    assert sha(ROOT / "evals/retrieval_cases.v1.yaml") == frozen["gold_hash"]
    assert sha(ROOT / "knowledge/local/knowledge.json") == frozen["corpus_hash"]
    items = load_knowledge_items(ROOT / "knowledge/local/knowledge.json")
    by_id = {i.id: i for i in items}
    index = json.loads((ROOT / "knowledge/local/index.json").read_text(encoding="utf-8"))
    assert index["item_ids"] == [i.id for i in items]
    vectors = np.asarray(np.load(ROOT / "knowledge/local/embeddings.npy", allow_pickle=False), dtype=np.float32)
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)  # EXACT production operation
    manual = json.loads((BASELINE / "scoring.json").read_text(encoding="utf-8"))
    retrieved = json.loads((BASELINE / "retrieved-all.json").read_text(encoding="utf-8"))
    tokenizer, _ = load_tokenizer(ROOT / "knowledge/local/embedding-model")
    untruncated = Tokenizer.from_str(tokenizer.to_str())
    untruncated.no_truncation()
    untruncated.no_padding()

    OUTPUT.mkdir()
    config = {"created_at": datetime.now(timezone.utc).isoformat(), "purpose": "Candidate-landscape diagnosis only",
              "gold_version": gold["set_version"], "gold_sha256": sha(ROOT / "evals/retrieval_cases.v1.yaml"),
              "corpus_sha256": sha(ROOT / "knowledge/local/knowledge.json"),
              "index_sha256": sha(ROOT / "knowledge/local/index.json"),
              "vectors_sha256": sha(ROOT / "knowledge/local/embeddings.npy"),
              "query_vector_source": str(BASELINE), "protected_before": protected,
              "effective_jurisdiction": "NO", "production_top_k": 3, "production_threshold": 0.35,
              "rank_definition": "All 161 jurisdiction-eligible passages sorted by production cosine descending, ID ascending, BEFORE score threshold; global rank also saved",
              "classification_rule": "Nearby cutoff = single-digit ranks 4-8 with sufficient missing information above threshold, or rank 1 excluded by threshold. Higher rank essential information => ranking/embedding primary. This is explanatory judgement, not a new retrieval setting or gold threshold.",
              "primary_scope": "Reason why both A and B still fail. A-only missing monitoring in case 06 is additionally mapped.",
              "secondary_multi_section": "Nine cases require more than one section for the complete case; not nine additional independent primary failures.",
              "secondary_representation": "Counted conservatively only where a necessary fact is absent from BOTH embedding views (cases 07/08); partial one-view truncation documented separately.",
              "tokenizer_truncation": tokenizer.truncation,
              "embedding_calls": 0, "retrieval_calls": 0, "generation_calls": 0,
              "versions": {name: version(name) for name in ["numpy", "tokenizers", "fastembed", "PyYAML"]},
              "runner_sha256": sha(Path(__file__)),
              "baseline_config_metadata_note": "Protocol YAML used unquoted NO, serialized as false by YAML 1.1. Actual baseline code hardcoded/defaulted to NO. Exact top-3 replay and passage filter confirm NO; no production impact. Prior files untouched."}
    save(OUTPUT / "diagnostic-config.json", config)
    shutil.copyfile(Path(__file__), OUTPUT / Path(__file__).name)
    facts = mapping()
    results = []
    for case in gold["cases"]:
        cid = case["id"]
        if cid not in facts:
            continue
        assert case["expected_result"] == "supported_context"
        missing_a = [n for n, p in enumerate(manual["A"][cid]["items"], 1) if not p["covered"]]
        missing_b = [n for n, p in enumerate(manual["B"][cid]["items"], 1) if not p["covered"]]
        assert [p["gold_item_index"] for p in facts[cid]] == missing_a
        q_path = BASELINE / f"{cid}-query-vector.npy"
        q = np.load(q_path, allow_pickle=False)[0]
        scores = vectors @ q
        order = sorted(range(len(items)), key=lambda n: (-float(scores[n]), items[n].id))
        eligible = [n for n in order if allowed_in_jurisdiction(items[n], case["jurisdiction"])]
        geo_rank = {items[n].id: r for r, n in enumerate(eligible, 1)}
        global_rank = {items[n].id: r for r, n in enumerate(order, 1)}
        landscape = [{"id": items[n].id, "document_id": items[n].document_id,
                      "source_url": items[n].source_url, "title": items[n].title,
                      "section": items[n].section, "language": items[n].language,
                      "metadata": items[n].metadata, "text": items[n].text,
                      "cosine": float(scores[n]), "global_rank": global_rank[items[n].id],
                      "jurisdiction_rank": geo_rank.get(items[n].id),
                      "geographically_eligible": n in eligible, "above_production_threshold": bool(scores[n] >= .35)}
                     for n in order]
        rows = {r["id"]: r for r in landscape}
        production = [rows[items[n].id] for n in eligible if scores[n] >= .35][:3]
        saved = next(r for r in retrieved if r["configuration"] == "A" and r["case_id"] == cid)
        assert [r["id"] for r in production] == [r["item"]["id"] for r in saved["seeds"]]
        for r, old in zip(production, saved["seeds"], strict=True):
            assert abs(r["cosine"] - old["score"]) < 1e-7
        annotations = []
        for gold_point in facts[cid]:
            pi = gold_point["gold_item_index"]
            p = {"gold_item_index": pi, "must_have_information": case["must_have_information"][pi-1],
                 "missing_in_A": pi in missing_a, "missing_in_B": pi in missing_b,
                 "exists_in_corpus": True, "sufficient_sets": []}
            for sufficient_set in gold_point["sufficient_sets"]:
                parts = []
                for part in sufficient_set:
                    item = by_id[part["id"]]
                    row = rows[item.id]
                    assert row["geographically_eligible"]
                    views = {}
                    for view, text in [("text", item.text), ("title_section_text", f"{item.title}. {item.section or ''}. {item.text}")]:
                        encoded = tokenizer.encode(text)
                        retained_end = max(end for start, end in encoded.offsets)
                        views[view] = {"untruncated_tokens_including_specials": len(untruncated.encode(text).ids),
                                       "retained_tokens_including_specials": len(encoded.ids),
                                       "retained_character_end": retained_end, "retained_text": text[:retained_end],
                                       "dropped_text": text[retained_end:]}
                    quotes = []
                    for quote in part["quotes"]:
                        assert quote in item.text
                        locations = {}
                        for view, text in [("text", item.text), ("title_section_text", f"{item.title}. {item.section or ''}. {item.text}")]:
                            start = text.index(quote)
                            end = start + len(quote)
                            retained_end = views[view]["retained_character_end"]
                            locations[view] = {"start": start, "end": end,
                                               "fully_seen": end <= retained_end,
                                               "partially_seen": start < retained_end < end,
                                               "not_seen": start >= retained_end}
                        quotes.append({"quote": quote, "locations": locations})
                    parts.append({"id": item.id, "title": item.title, "section": item.section,
                                  "source_url": item.source_url, "score": row["cosine"],
                                  "rank": row["jurisdiction_rank"], "global_rank": row["global_rank"],
                                  "above_threshold": row["above_production_threshold"],
                                  "in_production_top3": item.id in {r["id"] for r in production},
                                  "views": views, "evidence": quotes})
                p["sufficient_sets"].append({"parts": parts, "completion_rank": max(r["rank"] for r in parts),
                                              "all_above_threshold": all(r["above_threshold"] for r in parts)})
            p["best_completion_rank"] = min(s["completion_rank"] for s in p["sufficient_sets"])
            annotations.append(p)
        primary, secondary, rationale = CATEGORIES[cid]
        query_encoded = tokenizer.encode(case["question"])
        query_end = max(end for start, end in query_encoded.offsets)
        assert query_end == len(case["question"]), "Original query unexpectedly truncated"
        result = {"case_id": cid, "question": case["question"], "title": case["title"],
                  "primary_category": primary, "secondary_categories": secondary, "rationale": rationale,
                  "eligible_candidates": len(eligible), "above_threshold_candidates": sum(scores[n] >= .35 for n in eligible).item(),
                  "missing_A_count": len(missing_a), "missing_B_count": len(missing_b),
                  "query_sha256": hashlib.sha256(case["question"].encode()).hexdigest(),
                  "query_vector_sha256": sha(q_path), "query_truncated": False,
                  "original_query_tokens": len(untruncated.encode(case["question"]).ids),
                  "missing_points": annotations,
                  "best_rank_for_any_still_missing_information": min(r["best_completion_rank"] for r in annotations if r["missing_in_B"]),
                  "production_replay_matches": True, "production_top3": production}
        target = OUTPUT / cid
        target.mkdir()
        save(target / "all-candidates.json", landscape)
        save(target / "missing-information.json", result)
        shutil.copyfile(q_path, target / "original-query-vector.npy")
        results.append(result)
        print(f"{cid}: {primary}; missing A/B={len(missing_a)}/{len(missing_b)}", flush=True)
    assert len(results) == 11
    assert sum(r["missing_A_count"] for r in results) == 31
    assert sum(r["missing_B_count"] for r in results) == 30
    categories = ["top_k / threshold", "ranking / embedding", "chunk / representation", "multi-section requirement", "knowledge-base gap", "other"]
    pc = Counter(r["primary_category"] for r in results)
    sc = Counter(c for r in results for c in r["secondary_categories"])
    summary = {"configuration": config, "primary_counts": {c: pc[c] for c in categories},
               "secondary_counts": {c: sc[c] for c in categories}, "cases": results,
               "missing_information_A": 31, "missing_information_B": 30,
               "missing_information_found_in_corpus_A": 31,
               "case_gaps": 0, "query_truncation_cases": 0,
               "new_retrieval_variant_count": 0, "proposed_experiment_run": False}
    save(OUTPUT / "diagnosis.json", summary)
    after = {name: sha(ROOT / name) for name in protected}
    save(OUTPUT / "integrity-after.json", {"protected_unchanged": protected == after, "protected_after": after})
    assert protected == after
    print(json.dumps({"primary": summary["primary_counts"], "secondary": summary["secondary_counts"]}, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
