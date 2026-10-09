"""Exact risk scope and owner-limited three-config resume; no inference."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import continue_retrieval_phase_c_v1 as c


class PhaseCContinuationTests(unittest.TestCase):
    def setUp(self):
        self.row = {'case_id': 'case-13', 'context_sha256': 'context', 'cache_key': 'input',
                    'requires_review': False, 'certificate_judge_disagreement': [], 'decisions': ['not_covered'],
                    'flags': {'potentially_misleading': False, 'contradictory': False},
                    'coverage': {'coverage': 0, 'complete_pass': False}, 'eligible_for_selection': True}
        self.layer = {'status': 'registered_under_explicit_owner_review_authority', 'records': [
            {'id': 'review', 'case_id': 'case-13', 'context_sha256': 'context', 'cache_key': 'input',
             'field': 'potentially_misleading', 'original': False, 'registered': True, 'requires_review': False}]}
        self.original = patch.object(c.s.runtime, 'read', return_value={'status': 'owner_approved', 'records': []})
        self.original.start()
        self.addCleanup(self.original.stop)

    def test_risk_adjustment_preserves_raw_coverage_and_direct_conflict(self):
        original = deepcopy(self.row)
        result, ids = c.adjusted(self.row, self.layer)
        self.assertEqual(self.row, original)
        self.assertEqual(result['coverage'], original['coverage'])
        self.assertEqual(result['decisions'], original['decisions'])
        self.assertTrue(result['flags']['potentially_misleading'])
        self.assertFalse(result['flags']['contradictory'])
        self.assertEqual(ids, ['review'])

    def test_other_whole_inputs_do_not_inherit_review(self):
        for key in ['case_id', 'context_sha256', 'cache_key']:
            row = deepcopy(self.row)
            row[key] = 'changed'
            self.assertEqual(c.adjusted(row, self.layer), (row, []))

    def test_existing_review_and_certificate_disagreement_cannot_be_hidden(self):
        for key, value in [('requires_review', True), ('certificate_judge_disagreement', [1])]:
            row = deepcopy(self.row)
            row[key] = value
            with self.assertRaisesRegex(ValueError, 'cannot hide'):
                c.adjusted(row, self.layer)

    def test_unresolved_risk_blocks_eligibility_instead_of_becoming_zero(self):
        self.layer['records'][0]['requires_review'] = True
        result, _ = c.adjusted(self.row, self.layer)
        self.assertTrue(result['requires_review'])
        self.assertFalse(result['eligible_for_selection'])
        self.assertIsNone(result['coverage']['coverage'])
        self.assertIsNone(result['coverage']['complete_pass'])

    def test_out_of_scope_field_and_changed_original_are_rejected(self):
        for field, original in [('contradictory', False), ('potentially_misleading', True)]:
            layer = deepcopy(self.layer)
            layer['records'][0].update(field=field, original=original)
            with self.assertRaises(ValueError):
                c.adjusted(self.row, layer)

    def test_driver_runs_only_three_C_configs_and_skips_completed_C(self):
        self.original.stop()
        plan = {'phase_c': [{'id': 'C-P1'}, {'id': 'C-P2'}, {'id': 'C-P3'}]}
        with tempfile.TemporaryDirectory(dir=c.s.runtime.LOCAL) as folder:
            target = Path(folder) / 'configurations/C-P2'
            target.mkdir(parents=True)
            (target / 'summary.json').write_text('{}', encoding='utf-8')
            with patch.object(c.d, 'RUN', Path(folder)), patch.object(c, 'prepare', return_value=plan), \
                 patch.object(c, 'check_frozen'), patch.object(c, 'export'), \
                 patch.object(c.d, 'verify_rows') as verify, patch.object(c.previous, 'guarded_worker') as worker:
                c.run()
            self.assertEqual([call.args for call in worker.call_args_list],
                             [('retrieve', 'C-P1'), ('score', 'C-P1'), ('retrieve', 'C-P3'), ('score', 'C-P3')])
            verify.assert_called_once_with('C-P2')


if __name__ == '__main__':
    c.s.holdout_guard()
    unittest.main()
