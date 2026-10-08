"""Synthetic local tests only: no API, CLI, sources, retrieval or holdout."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import retrieval_judge_pilot as p


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp_root = p.ROOT / "knowledge/local/judge-test-temp"
        self.temp_root.mkdir(parents=True, exist_ok=True)
        self.inp = {"case_id": "synthetic", "expected_result": "supported_context",
                    "requirements": [{"item": 1, "requirement": "Close the blue box before noon."}],
                    "blocks": [{"block": 1, "text": "Close the blue box before noon."},
                               {"block": 2, "text": "The red box stays open."}]}
        self.answer = {"case_id": "synthetic", "items": [{"item": 1, "decision": "covered",
                       "evidence": [{"block": 1, "quote": "Close the blue box before noon."}],
                       "missing_components": [], "reason": "Complete instruction supplied."}],
                       "irrelevant": [], "potentially_misleading": [], "jurisdiction_leakage": [],
                       "optional_observed": [], "requires_review": False}

    def test_valid_complete_synthetic_result(self):
        self.assertEqual(p.validate_result(self.answer, self.inp), [])
        self.assertTrue(p.coverage(self.answer, self.inp)["complete_pass"])

    def test_quote_must_occur_in_specified_block(self):
        self.answer["items"][0]["evidence"][0]["block"] = 2
        self.assertIn("quote absent from stated block", p.validate_result(self.answer, self.inp))

    def test_noncontiguous_or_changed_quote_is_invalid(self):
        self.answer["items"][0]["evidence"][0]["quote"] = "Close the blue box ... noon."
        self.assertTrue(p.validate_result(self.answer, self.inp))

    def test_missing_duplicate_and_extra_items_rejected(self):
        for items in [[], self.answer["items"] * 2, [dict(self.answer["items"][0], item=2)]]:
            value = dict(self.answer, items=items)
            self.assertTrue(p.validate_result(value, self.inp))

    def test_schema_and_case_identity(self):
        self.answer["items"][0]["decision"] = "maybe"
        self.assertTrue(p.validate_result(self.answer, self.inp))
        self.answer["items"][0]["decision"] = "covered"
        self.answer["case_id"] = "other"
        self.assertTrue(p.validate_result(self.answer, self.inp))

    def test_partial_is_binary_and_requires_missing_components(self):
        item = self.answer["items"][0]
        item.update(decision="not_covered", missing_components=["before noon"])
        self.assertFalse(p.validate_result(self.answer, self.inp))
        self.assertEqual(p.coverage(self.answer, self.inp)["coverage"], 0)
        item["missing_components"] = []
        self.assertTrue(p.validate_result(self.answer, self.inp))

    def test_positive_cannot_have_missing_parts_or_no_evidence(self):
        self.answer["items"][0]["missing_components"] = ["time"]
        self.assertTrue(p.validate_result(self.answer, self.inp))
        self.answer["items"][0].update(missing_components=[], evidence=[])
        self.assertTrue(p.validate_result(self.answer, self.inp))

    def test_uncertainty_is_never_silently_zero(self):
        self.answer["items"][0]["decision"] = "uncertain"
        self.assertTrue(p.validate_result(self.answer, self.inp))
        self.answer["requires_review"] = True
        self.assertFalse(p.validate_result(self.answer, self.inp))
        self.assertIsNone(p.coverage(self.answer, self.inp)["coverage"])
        self.assertIsNone(p.coverage(self.answer, self.inp)["complete_pass"])

    def test_empty_gold_and_supported_subset_gaps_never_pass(self):
        self.inp["expected_result"] = "insufficient_coverage"
        self.assertFalse(p.coverage(self.answer, self.inp)["complete_pass"])
        self.inp["requirements"], self.answer["items"] = [], []
        self.assertFalse(p.validate_result(self.answer, self.inp))
        self.assertFalse(p.coverage(self.answer, self.inp)["complete_pass"])
        self.assertIsNone(p.coverage(self.answer, self.inp)["coverage"])

    def test_noise_requires_quote_and_nonempty_reason(self):
        self.answer["irrelevant"] = [{"evidence": [], "reason": "Red box off topic."}]
        self.assertTrue(p.validate_result(self.answer, self.inp))
        self.answer["irrelevant"][0]["evidence"] = [{"block": 2, "quote": "The red box stays open."}]
        self.assertFalse(p.validate_result(self.answer, self.inp))
        self.answer["irrelevant"][0]["reason"] = " "
        self.assertTrue(p.validate_result(self.answer, self.inp))

    def test_budget_reservations_include_unknown_calls_and_exact_cap(self):
        ledger = [{"charged_or_reserved_usd": 4.9, "state": "in_flight"}]
        self.assertEqual(p.ensure_budget(ledger, 0.1, 5), 4.9)
        with self.assertRaises(ValueError):
            p.ensure_budget(ledger, 0.11, 5)

    def test_actual_usage_cache_and_reasoning_not_double_billed(self):
        usage = {"input_tokens": 1000, "output_tokens": 500,
                 "input_tokens_details": {"cached_tokens": 200},
                 "output_tokens_details": {"reasoning_tokens": 300}}
        price = {"input": 2, "cached_input": 0.1, "output": 10}
        self.assertAlmostEqual(p.api_cost(usage, price), 0.00662)

    def test_cli_has_no_api_credentials_and_no_repo_cwd(self):
        with patch.dict(p.os.environ, {"OPENAI_API_KEY": "synthetic-secret", "CODEX_API_KEY": "test"}):
            env = p.codex_environment()
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertNotIn("CODEX_API_KEY", env)
        with tempfile.TemporaryDirectory(dir=self.temp_root) as folder:
            cmd = p.codex_command("codex", Path(folder), {"codex_model": "gpt-6.1-sol"})
            self.assertIn("--ignore-user-config", cmd)
            self.assertIn('forced_login_method="chatgpt"', cmd)
            self.assertIn('model_reasoning_effort="medium"', cmd)
            self.assertIn("features.shell_tool=false", cmd)
            self.assertIn("features.apps=false", cmd)
            self.assertEqual(cmd[cmd.index("--cd") + 1], folder)

    def test_sensitive_exception_values_not_logged(self):
        self.assertNotIn("secret", json.dumps(p.safe_error(ValueError("secret"))))

    def test_frozen_result_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as folder:
            path = Path(folder) / "result.json"
            p.write_json(path, self.answer)
            with self.assertRaises(ValueError):
                p.write_json(path, self.answer)

    def test_resume_never_pays_for_existing_completed_record(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as folder:
            base = Path(folder)
            config = p.read_json(p.CONFIG)
            p.write_json(base / "config.json", config)
            p.write_json(base / "schema.json", p.read_json(p.SCHEMA))
            (base / "prompt.md").write_text("synthetic prompt", encoding="utf-8")
            p.write_json(base / "preflight.json", {"api": {"gpt-6-luna": {"available": True}}})
            p.write_json(base / "index.json", [{"context_id": "context-01", "case_id": "synthetic"}])
            p.write_json(base / "results/luna-api/context-01/record.json", {"success": True})
            with patch.object(p, "verify_freeze"), patch.object(p, "api_client") as client:
                p.run(base, ["luna-api"])
                client.assert_not_called()

    def test_unknown_inflight_request_is_not_retried_or_freed(self):
        with tempfile.TemporaryDirectory(dir=self.temp_root) as folder:
            base = Path(folder)
            p.write_json(base / "config.json", p.read_json(p.CONFIG))
            p.write_json(base / "schema.json", p.read_json(p.SCHEMA))
            (base / "prompt.md").write_text("synthetic prompt", encoding="utf-8")
            p.write_json(base / "preflight.json", {"api": {"gpt-6-luna": {"available": True}}})
            p.write_json(base / "index.json", [{"context_id": "context-01", "case_id": "synthetic", "input_sha256": "synthetic"}])
            p.write_json(base / "inputs/context-01.json", self.inp)
            ledger = [{"alternative": "luna-api", "context_id": "context-01",
                       "charged_or_reserved_usd": 1.0, "state": "in_flight"}]
            p.write_json(base / "api-ledger.json", ledger)
            with patch.object(p, "verify_freeze"), patch.object(p, "api_client") as client:
                p.run(base, ["luna-api"])
                client.assert_not_called()
            self.assertEqual(p.read_json(base / "api-ledger.json"), ledger)
            self.assertFalse(p.read_json(base / "results/luna-api/context-01/record.json")["success"])


if __name__ == "__main__":
    unittest.main()
