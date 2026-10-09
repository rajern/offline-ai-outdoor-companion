"""Exact owner adjudication scope and conservative continuation checks; no inference."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path
import continue_retrieval_optimization_v1 as c


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.layer = {'status': 'owner_approved', 'records': [{
            'id': 'fixture', 'case_id': 'case-20', 'context_sha256': 'context',
            'cache_key': 'full-input-key', 'item': 1, 'original': 'not_covered', 'approved': 'covered'}]}
        self.row = {'case_id': 'case-20', 'configuration': 'A-minilm', 'context_sha256': 'context',
            'cache_key': 'full-input-key', 'requires_review': False, 'certificate_judge_disagreement': [],
            'decisions': ['not_covered', 'covered'], 'flags': {'contradictory': False},
            'coverage': {'gap': False, 'total': 2, 'covered': 1, 'coverage': .5, 'complete_pass': False}}

    def test_adjustment_preserves_raw_and_only_changes_approved_fields(self):
        original = deepcopy(self.row)
        result, ids = c.adjusted(self.row, self.layer)
        self.assertEqual(self.row, original)
        self.assertEqual(ids, ['fixture'])
        self.assertEqual([k for k in original if original[k] != result[k]], ['decisions', 'coverage'])
        self.assertEqual(result['coverage']['coverage'], 1)
        self.assertTrue(result['coverage']['complete_pass'])

    def test_identical_input_reuse_across_configuration_labels(self):
        self.row['configuration'] = 'B-k8-none'
        self.assertEqual(c.adjusted(self.row, self.layer)[1], ['fixture'])

    def test_other_context_question_or_judge_identity_never_inherits_adjustment(self):
        for key in ['case_id', 'context_sha256', 'cache_key']:
            row = deepcopy(self.row); row[key] = 'different'
            self.assertEqual(c.adjusted(row, self.layer), (row, []))

    def test_adjudication_cannot_hide_review_or_certificate_disagreement(self):
        for key, value in [('requires_review', True), ('certificate_judge_disagreement', [1])]:
            row = deepcopy(self.row); row[key] = value
            with self.assertRaisesRegex(ValueError, 'hide a new review'):
                c.adjusted(row, self.layer)

    def test_no_knowledge_gap_full_pass_or_changed_original(self):
        for edit in ['gap', 'changed']:
            row = deepcopy(self.row)
            if edit == 'gap': row['coverage']['gap'] = True
            else: row['decisions'][0] = 'covered'
            with self.assertRaises(ValueError): c.adjusted(row, self.layer)

    def test_risk_adjustment_never_invents_direct_conflict(self):
        record = self.layer['records'][0]
        record.pop('item'); record.update(field='potentially_misleading', original=False, approved=True)
        self.row['flags']['potentially_misleading'] = False
        result, _ = c.adjusted(self.row, self.layer)
        self.assertTrue(result['flags']['potentially_misleading'])
        self.assertFalse(result['flags']['contradictory'])
        self.assertEqual(result['coverage'], self.row['coverage'])

    def test_unapproved_layer_is_refused(self):
        self.layer['status'] = 'proposed_pending_owner_decision'
        with self.assertRaises(ValueError): c.adjusted(self.row, self.layer)

    def test_stage_cannot_hide_tradeoffs(self):
        summaries = []
        for cid, decisions in [('B-one', ['covered', 'not_covered']), ('B-two', ['not_covered', 'covered'])]:
            summaries.append({'configuration': {'id': cid}, 'full25': {'eligible_for_selection': True},
                'scores': [{'case_id': 'case-01', 'decisions': decisions, 'flags': {
                    'potentially_misleading': False, 'contradictory': False, 'jurisdiction_leakage': False}}]})
        with patch.object(c, 'sidecar', side_effect=summaries), patch.object(c, 'write_once'):
            with self.assertRaisesRegex(RuntimeError, 'tradeoffs'): c.stage_choice('B', ['B-one', 'B-two'])

    def test_driver_skips_a_and_completed_b_and_has_exactly_28_scopes(self):
        plan = {'phase_b': [{'id': f'B-{i}'} for i in range(25)], 'phase_c': [{'id': f'C-{i}'} for i in range(3)]}
        with tempfile.TemporaryDirectory(dir=c.s.runtime.LOCAL) as folder:
            run = Path(folder)
            target = run / 'configurations/B-0'; target.mkdir(parents=True)
            (target / 'summary.json').write_text('{}', encoding='utf-8')
            with patch.object(c.d, 'RUN', run), patch.object(c, 'prepare', return_value=plan), \
                 patch.object(c, 'export'), patch.object(c, 'check_frozen'), patch.object(c, 'sidecar'), \
                 patch.object(c, 'stage_choice') as choose, patch.object(c.d, 'verify_rows') as verify, \
                 patch.object(c, 'guarded_worker') as worker:
                c.run()
            self.assertEqual(worker.call_count, 54)
            self.assertFalse(any(call.args[1].startswith('A-') for call in worker.call_args_list))
            verify.assert_called_once_with('B-0')
            self.assertEqual(choose.call_count, 2)


if __name__ == '__main__':
    c.s.holdout_guard()
    unittest.main()
