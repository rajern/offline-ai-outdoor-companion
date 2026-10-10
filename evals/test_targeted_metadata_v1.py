"""Verify diagnostic completion cannot change the existing source scorer."""
import copy
import unittest
import targeted_scoring_metadata_v1 as m


class MetadataCompatibility(unittest.TestCase):
    def test_scope_count_without_mutation(self):
        row = {'chunk_count': 3, 'excerpts': [
            {'item': {'document_id': 'a', 'section': 'x'}},
            {'item': {'document_id': 'a', 'section': 'x'}},
            {'item': {'document_id': 'b', 'section': 'x'}}]}
        before = copy.deepcopy(row)
        self.assertEqual(m.complete_metadata(row)['section_count'], 2)
        self.assertEqual(row, before)
        self.assertEqual(m.complete_metadata(m.complete_metadata(row)), m.complete_metadata(row))

    def test_old_scorer_equivalence_and_cached_answer(self):
        s = m.s; s.holdout_guard()
        corpus = s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']
        cases = {c['id']: c for c in s.load_development()['cases']}
        old = s.runtime.read(m.t.d.RUN / 'configurations/C-P3/case-01/retrieved.json')
        context = m.t.d.context_for([m.t.d.RetrievedKnowledgeItem(m.t.d.KnowledgeItem(**e['item']), e['score']) for e in old['excerpts']])
        original = m.ORIGINAL(cases['case-01'], old, context, corpus, s.rules())
        without = {k: v for k, v in old.items() if k != 'section_count'}
        self.assertEqual(original, m.score_saved(cases['case-01'], without, context, corpus, s.rules()))
        row = s.runtime.read(m.t.RUN / 'configurations/T-ranking/case-01/retrieved.json')
        payload = s.judge_input(cases['case-01'], row)
        self.assertEqual(payload, s.judge_input(cases['case-01'], m.complete_metadata(row)))
        identity = s.runtime.read(m.t.RUN / 'freeze.json')['judge_identity']
        cache = s.CACHE / s.cache_key(payload, identity)
        answer = s.runtime.read(cache / 'results/context-01/answer.json')
        m.install()
        merged = s.merge(cases['case-01'], row, '\n\n'.join(b['text'] for b in payload['blocks']), corpus, answer, s.rules())
        self.assertFalse(merged['requires_review'])
        self.assertEqual(merged['decisions'], [i['decision'] for i in answer['items']])


if __name__ == '__main__':
    unittest.main()
