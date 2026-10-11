"""Relevant input-budget and source-preservation guard checks; no inference."""
import unittest
import preflight_local_generation_v1 as p


class PreflightTests(unittest.TestCase):
    def test_actual_template_tokens_and_output_fit(self):
        p.budget_check(3200, 4096, 262144)
        with self.assertRaisesRegex(RuntimeError, '3200'):
            p.budget_check(3201, 4096, 262144)
        with self.assertRaisesRegex(RuntimeError, 'context'):
            p.budget_check(3200, 3711, 262144)
        with self.assertRaisesRegex(RuntimeError, 'context'):
            p.budget_check(3200, 4096, 3711)

    def test_sources_and_question_stay_verbatim_in_distinct_roles(self):
        context = '[KUNNSKAPSUTDRAG 1]\nInnhold: SYNTHETIC Å\n\n[KUNNSKAPSUTDRAG 2]\nInnhold: SYNTHETIC B'
        question = 'Syntetisk spørsmål?'
        turns = p.messages(question, context)
        self.assertEqual([t['role'] for t in turns], ['system', 'user'])
        self.assertIn('[KILDEUTDRAG]\n' + context + '\n[/KILDEUTDRAG]', turns[1]['content'])
        self.assertIn('[BRUKERSPØRSMÅL]\n' + question + '\n[/BRUKERSPØRSMÅL]', turns[1]['content'])

    def test_full_plan_predefines_sensitive_tests(self):
        self.assertEqual(len(p.STAGE_ONE), 8)
        self.assertEqual(list(p.PARAPHRASES), ['case-03','case-08','case-17','case-21'])
        self.assertEqual(p.REPEATS, ['case-08','case-17','case-21','case-23'])


if __name__ == '__main__':
    unittest.main()
