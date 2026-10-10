"""Meaningful synthetic checks; no knowledge corpus or gold read."""
import unittest
import numpy as np
from tokenizers import Tokenizer, models, pre_tokenizers, processors

import targeted_retrieval_methods as m
import run_retrieval_optimization_v1 as d


def item(identifier, text, section, document='doc'):
    return d.KnowledgeItem(identifier, text, 'title', 'synthetic', 'https://example.invalid',
                           'synthetic', 'en', 'test', section=section, document_id=document,
                           metadata={'is_location_specific': False, 'jurisdiction': 'general'})


class TargetedTests(unittest.TestCase):
    def tokenizer(self):
        value = Tokenizer(models.WordLevel({'[UNK]': 0, '[CLS]': 1, '[SEP]': 2, 'word': 3}, unk_token='[UNK]'))
        value.pre_tokenizer = pre_tokenizers.Whitespace()
        value.post_processor = processors.TemplateProcessing(single='[CLS] $A [SEP]', special_tokens=[('[CLS]', 1), ('[SEP]', 2)])
        return value

    def test_every_body_character_and_tail_is_searchable(self):
        text = ' word ' * 400 + ' final instruction'
        tokenizer = self.tokenizer()
        windows = m.text_windows(text, tokenizer, 96)
        self.assertEqual(''.join(t for t, _ in windows), text)
        inputs, groups = m.embedding_views([{'id': 'synthetic', 'title': 'word ' * 40, 'text': text}], tokenizer)
        self.assertTrue(any('final instruction' in t for t in inputs))
        self.assertTrue(all(len(tokenizer.encode(t).ids) <= 128 for t in inputs))
        self.assertEqual(len(groups), 2)

    def test_repeating_identical_windows_does_not_get_max_score_bonus(self):
        vectors = np.array([[1, 0], [0, 1], [1, 0], [0, 1]], dtype=np.float32)
        short = [{'indices': [0, 1], 'weights': [1, 1]}] * 2
        long = [{'indices': [0, 1, 2, 3], 'weights': [1, 1, 1, 1]}] * 2
        np.testing.assert_allclose(m.parent_vectors(vectors, short), m.parent_vectors(vectors, long))
        self.assertEqual(m.parent_vectors(vectors, long).shape, (1, 2))

    def test_ancestor_scope_and_whole_same_heading_procedure_retained(self):
        parents = [item('scope', 'Only in this situation.', 'root'),
                   item('step1', 'First: action with condition.', 'root / procedure'),
                   item('step2', 'Then: call emergency service.', 'root / procedure'),
                   item('unrelated', 'Other circumstances.', 'root / other')]
        self.assertEqual([p.id for p in m.instruction_unit(parents[1], parents, 'NO')], ['scope', 'step1', 'step2'])
        self.assertNotEqual(m.scope_key(parents[0]), m.scope_key(item('other', parents[0].text, 'other')))

    def test_atomic_packet_not_trimmed_to_fit_and_document_diversity(self):
        parents = [item('large', 'long', 'root / procedure'),
                   item('continuation', 'condition', 'root / procedure'),
                   item('short', 'brief', 'root', 'other')]
        class Counter:
            def count(self, text):
                return (2100 if 'condition' in text else 100), 'synthetic'
        results, _, trace = m.diverse_pack({'question': 'test', 'jurisdiction': 'NO'},
            [d.RetrievedKnowledgeItem(parents[0], .9), d.RetrievedKnowledgeItem(parents[2], .8)], parents, Counter())
        self.assertEqual([r.item.id for r in results], ['short'])
        self.assertEqual(trace[0]['status'], 'over_budget')
        self.assertEqual(trace[0]['would_add'], ['large', 'continuation'])


if __name__ == '__main__':
    unittest.main()
