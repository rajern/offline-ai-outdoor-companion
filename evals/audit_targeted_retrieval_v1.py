"""Offline audit of existing targeted rows, seals and unchanged scorer output."""
import run_targeted_retrieval_v1 as t
import retrieval_optimization_scoring as s


def audit():
    frozen = t.verify(); cases = {c['id']: c for c in s.load_development()['cases']}
    corpus = s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']
    rows_checked = scores_checked = 0
    for config in frozen['config']['variants']:
        target = t.RUN / 'configurations' / config['id']
        if not (target / 'retrieved-all.json').exists():
            continue
        for row in t.verify_rows(config['id']):
            rows_checked += 1
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
              'original_files_checked': len(frozen['prior_files']),
              'new_judge_calls': 0, 'holdout_accessed': False,
              'frozen_targeted_code': frozen['code'],
              'limits': 'Semantic source review is separate; seal validity is not semantic correctness.'}
    s.runtime.write(s.ROOT / 'evals/retrieval_targeted_audit.v1.json', record, replace=True)
    print(record, flush=True)


if __name__ == '__main__':
    s.holdout_guard(); audit()
