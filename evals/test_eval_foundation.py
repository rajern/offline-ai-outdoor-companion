"""No retrieval/generation. Guard, conjunction and saved-text regression checks."""
import json
import unittest

import eval_foundation as f
from automatic_retrieval_scoring import certified_item, score_saved, rendered_context, CERTIFICATES, bounds


class FoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = f.load_development()
        cls.rules = json.loads(CERTIFICATES.read_text(encoding="utf-8"))
        cls.corpus = json.loads(f.CORPUS.read_text(encoding="utf-8"))["items"]

    def test_legacy_fifteen_exactly_preserved(self):
        self.assertEqual(f.sha(f.BASE), f.BASE_HASH)
        self.assertEqual(self.dev["cases"][:15], f.read_yaml(f.BASE)["cases"])
        self.assertEqual(len(self.dev["cases"]), 25)

    def test_control_ids_rejected_without_reading_control(self):
        with self.assertRaises(ValueError):
            f.require_development_cases(["control-01"])

    def test_correct_document_without_procedure_does_not_pass(self):
        decision = certified_item("Førstehjelp ved brannskader", self.rules["rules"]["case-07"][0])
        self.assertEqual(decision["decision"], "needs_review")

    def test_partial_conjunction_zero_certification(self):
        rule = self.rules["rules"]["case-03"][4]
        only_limit = rule["alternatives"][0]["all_of"][0]["quote"]
        self.assertEqual(certified_item(only_limit, rule)["decision"], "needs_review")
        both = "\n\n".join(a["quote"] for a in rule["alternatives"][0]["all_of"])
        self.assertEqual(certified_item(both, rule)["decision"], "covered")

    def test_altitude_qualification_required(self):
        rule = self.rules["rules"]["case-03"][2]
        short = "To kill germs, bring clear water to a rolling boil for 1 minute."
        self.assertEqual(certified_item(short, rule)["decision"], "needs_review")

    def test_negation_and_quantity_not_fuzzy_matched(self):
        rule = self.rules["rules"]["case-07"][1]
        text = " ".join(a["quote"] for a in rule["alternatives"][0]["all_of"])
        self.assertEqual(certified_item(text.replace("Ikke bruk is", "Bruk is"), rule)["decision"], "needs_review")
        boiling = self.rules["rules"]["case-03"][3]
        text = " ".join(a["quote"] for a in boiling["alternatives"][0]["all_of"])
        self.assertEqual(certified_item(text.replace("3 minutes", "2 minutes"), boiling)["decision"], "needs_review")

    def test_whitespace_and_order_do_not_change_fact_presence(self):
        rule = self.rules["rules"]["case-06"][3]
        atoms = rule["alternatives"][0]["all_of"]
        text = "\n\n".join(a["quote"].replace(" ", "\n") for a in reversed(atoms))
        self.assertEqual(certified_item(text, rule)["decision"], "covered")

    def test_unregistered_equivalent_units_remain_unknown_not_fail(self):
        rule = self.rules["rules"]["case-11"][0]
        text = "Bury human waste about 20 cm deep and about 60 m from natural water."
        self.assertEqual(certified_item(text, rule)["decision"], "needs_review")

    def test_no_chunk_id_whitelist_and_wrong_geography_cannot_certify(self):
        case = next(c for c in self.dev["cases"] if c["id"] == "case-22")
        p = next(p for p in self.corpus if p["id"] == "source-09-005").copy()
        p["id"] = "completely-new-child-identity"
        row = {"case_id": case["id"], "question": case["question"], "excerpts": [{"item": p}],
               "context_tokens": 300, "prompt_tokens": 500, "context_budget": 2000,
               "chunk_count": 1, "section_count": 1}
        text = rendered_context(row["excerpts"])
        result = score_saved(case, row, text, self.corpus, self.rules)
        self.assertEqual(result["certified_found"], 3)
        wrong = dict(case, jurisdiction="NO")
        result = score_saved(wrong, row, text, self.corpus, self.rules)
        self.assertEqual(result["certified_found"], 0)
        self.assertTrue(result["jurisdiction_metadata_candidates"])

    def test_supported_subset_and_empty_gap_never_complete_pass(self):
        case = next(c for c in self.dev["cases"] if c["id"] == "case-25")
        row = {"case_id": case["id"], "question": case["question"], "excerpts": [],
               "context_tokens": 0, "prompt_tokens": 180, "context_budget": 2000,
               "chunk_count": 0, "section_count": 0}
        result = score_saved(case, row, "", self.corpus, self.rules)
        self.assertFalse(result["complete_pass_lower_bound"])
        totals = bounds([result])
        self.assertEqual(totals["covered_cases"], 0)
        self.assertIsNone(totals["must_have_coverage_lower_bound"])
        self.assertEqual(len(totals["insufficient_coverage"]), 1)

    def test_unseen_noise_is_not_automatically_zero(self):
        case = next(c for c in self.dev["cases"] if c["id"] == "case-16")
        p = next(p for p in self.corpus if p["id"] == "source-02-012")
        row = {"case_id": case["id"], "question": case["question"], "excerpts": [{"item": p}],
               "context_tokens": 150, "prompt_tokens": 400, "context_budget": 2000,
               "chunk_count": 1, "section_count": 1}
        result = score_saved(case, row, rendered_context(row["excerpts"]), self.corpus, self.rules)
        self.assertEqual(result["certified_found"], 2)
        self.assertEqual(result["irrelevant_context"], "needs_review")
        self.assertTrue(result["requires_semantic_review"])


if __name__ == "__main__":
    unittest.main()
