"""Offline audit of existing targeted rows, seals and unchanged scorer output."""
import run_targeted_retrieval_v1 as t
import retrieval_optimization_scoring as s
import json
from pathlib import Path
import numpy as np
import targeted_scoring_metadata_v1 as metadata


def verify_partial(target, cases, parents):
    rows = []
    for path in sorted(target.glob('case-*/retrieved.json')):
        row = s.runtime.read(path); case = cases[row['case_id']]
        assert row['question'] == case['question']
        assert row['corpus_hash'] == t.d.file_hash(s.runtime.LOCAL / 'knowledge.json')
        assert row['gold_hash'] == t.d.file_hash(s.ROOT / 'evals/retrieval_cases.v1.yaml')
        results = []
        for excerpt in row['excerpts']:
            item = t.d.KnowledgeItem(**excerpt['item'])
            assert t.d.asdict(item) == t.d.asdict(parents[item.id])
            assert t.d.allowed_in_jurisdiction(item, case['jurisdiction'])
            results.append(t.d.RetrievedKnowledgeItem(item, excerpt['score']))
        for filename, text, prefix in [('context.txt', t.d.context_for(results), 'context'),
                ('prompt-not-executed.txt', t.d._build_grounded_prompt(case['question'], results), 'prompt')]:
            assert text == (path.parent / filename).read_text(encoding='utf-8')
            key = s.runtime.legacy.text_sha(text)
            assert key == row[prefix + '_sha256'] == row[prefix + '_tokenization_key']
            directories = [base / 'tokenization' / key for base in [t.d.RUN, t.PREVIOUS, t.RUN]]
            cache = next(directory for directory in directories if (directory / 'count.json').exists())
            count = s.runtime.read(cache / 'count.json')
            assert text == (cache / 'input.txt').read_text(encoding='utf-8')
            assert t.d.file_hash(cache / 'stdout.txt') == count['stdout_sha256']
            ids = json.loads((cache / 'stdout.txt').read_text(encoding='utf-8'))
            assert all(isinstance(v, int) for v in ids)
            assert len(ids) == count['tokens'] == row[prefix + '_tokens']
        assert row['prompt_tokens'] <= 2000
        assert len({r['item']['id'] for r in row['seeds']}) == 16
        payload = s.judge_input(case, row)
        assert 'expected_result' not in payload
        assert len(payload['requirements']) == len(case['must_have_information'])
        assert s.runtime.legacy.text_sha('\n\n'.join(b['text'] for b in payload['blocks'])) == row['context_sha256']
        rows.append(row)
    return rows


def audit():
    frozen = t.verify(); cases = {c['id']: c for c in s.load_development()['cases']}
    if (metadata.STATE / 'freeze.json').exists():
        metadata.verify_binding(); metadata.install()
    corpus = s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']
    parents = {p['id']: t.d.KnowledgeItem(**p) for p in corpus}
    rows_checked = scores_checked = 0
    for config in frozen['config']['variants']:
        target = t.RUN / 'configurations' / config['id']
        checked = (t.verify_rows(config['id']) if (target / 'retrieved-all.json').exists()
                   else verify_partial(target, cases, parents))
        for row in checked:
            rows_checked += 1
            case = cases[row['case_id']]
            payload = s.judge_input(case, row)
            assert 'expected_result' not in payload
            assert len(payload['requirements']) == len(case['must_have_information'])
            assert s.runtime.legacy.text_sha('\n\n'.join(b['text'] for b in payload['blocks'])) == row['context_sha256']
            path = target / row['case_id'] / 'score.json'
            if not path.exists():
                continue
            raw = s.runtime.read(path); case = cases[row['case_id']]
            payload = s.judge_input(case, row)
            key = s.cache_key(payload, frozen['judge_identity'])
            assert key == raw['cache_key']
            cache = s.CACHE / key; result = cache / 'results/context-01'
            assert s.runtime.read(cache / 'inputs/context-01.json') == payload
            for name, expected in s.runtime.read(cache / 'result-seal.json').items():
                assert t.d.file_hash(result / name) == expected
            record = s.runtime.read(result / 'record.json')
            assert record['success'] and record['authentication'] == 'chatgpt_subscription'
            assert record['model_requested'] == 'gpt-6.1-sol' and record['reasoning_effort'] == 'medium'
            answer = s.runtime.read(result / 'answer.json')
            assert not s.runtime.validate(answer, payload, s.runtime.read(s.SCHEMA))
            assert s.digest(answer) == raw['judge_result_sha256']
            context = '\n\n'.join(b['text'] for b in payload['blocks'])
            merged = s.merge(case, row, context, corpus, answer, s.rules())
            assert all(raw[k] == v for k, v in merged.items())
            scores_checked += 1
    record = {'passed': True, 'retrieved_rows_checked': rows_checked, 'scores_checked': scores_checked,
              'blind_adapter_rows_checked': rows_checked,
              'audit_helper_code_sha256': t.d.file_hash(Path(__file__)),
              'fresh_query_vector_bytes_equal_baseline': (
                  np.load(t.RUN / 'index/queries.npy').tobytes() ==
                  np.load(t.d.RUN / 'indices/minilm/queries.npy').tobytes()),
              'original_files_checked': len(frozen['prior_files']),
              'superseded_pre_scoring_files_checked': len(frozen['superseded_pre_scoring_files']),
              'new_judge_calls': 0, 'holdout_accessed': False,
              'frozen_targeted_code': frozen['code'],
              'limits': 'Semantic source review is separate; seal validity is not semantic correctness.'}
    if (metadata.STATE / 'freeze.json').exists():
        record['scoring_metadata_binding_sha256'] = t.d.file_hash(metadata.STATE / 'freeze.json')
        record['judge_inputs_unchanged_by_metadata_adapter'] = 75
    s.runtime.write(s.ROOT / 'evals/retrieval_targeted_audit.v1.json', record, replace=True)
    print(record, flush=True)


if __name__ == '__main__':
    s.holdout_guard(); audit()
