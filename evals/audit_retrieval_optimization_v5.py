"""Offline final audit: frozen identities, delivered inputs, sealed answers and analysis.

Never invokes the judge or a tokenizer. Every token count must already be cached.
"""
from pathlib import Path
import json

import continue_retrieval_optimization_v1 as c
import run_retrieval_optimization_v1 as d
import retrieval_optimization_scoring as s


def audit(output_paths=None):
    s.holdout_guard()
    frozen = d.verify()
    c.check_frozen()
    plan = s.runtime.read(d.RUN / 'plan.json')
    planned = plan['phase_a'] + plan['phase_b'] + plan['phase_c']
    assert len(planned) == 31
    allowed = {p['id'] for p in planned}
    observed = {p.name for p in (d.RUN / 'configurations').iterdir() if p.is_dir()}
    assert observed <= allowed, 'Unplanned configuration'
    cases = {v['id']: v for v in s.load_development()['cases']}
    corpus = s.runtime.read(s.ROOT / 'knowledge/local/knowledge.json')['items']
    certificates = s.rules()
    layer = s.runtime.read(c.LAYER)
    verified = []
    partial = []
    unique_keys = set()
    adjusted_changes = []
    partial_bindings = []
    retrieved_contexts = 0
    for config in planned:
        cid = config['id']
        target = d.RUN / 'configurations' / cid
        complete = (target / 'summary.json').exists()
        if not complete:
            partial.append({'configuration': cid, 'saved_scores': len(list(target.glob('case-*/score.json')))})
            if not (target / 'retrieved-all.json').exists():
                continue
        rows = s.runtime.read(target / 'retrieved-all.json')
        assert [r['case_id'] for r in rows] == list(cases)
        # Require all token-cache files before calling the original verifier.
        # Thus even accidental misses cannot lead to new tokenizer subprocesses.
        for row in rows:
            for name, token_field, hash_field in [('context.txt', 'context_tokens', 'context_sha256'),
                                                  ('prompt-not-executed.txt', 'prompt_tokens', 'prompt_sha256')]:
                text = (target / row['case_id'] / name).read_text(encoding='utf-8')
                text_sha = s.runtime.legacy.text_sha(text)
                assert text_sha == row[hash_field]
                cache = d.RUN / 'tokenization' / text_sha
                count = s.runtime.read(cache / 'count.json')
                assert (cache / 'input.txt').read_text(encoding='utf-8') == text
                assert d.file_hash(cache / 'stdout.txt') == count['stdout_sha256']
                assert count['tokens'] == row[token_field] == len(s.runtime.read(cache / 'stdout.txt'))
                assert row['prompt_tokens'] <= 2000
        assert d.verify_rows(cid) == rows
        retrieved_contexts += len(rows)
        raw = s.runtime.read(target / 'summary.json') if complete else None
        adjusted = s.runtime.read(c.STATE / 'adjusted' / (cid + '.json')) if complete else None
        if complete:
            assert adjusted['raw_summary_sha256'] == d.file_hash(target / 'summary.json')
            assert adjusted['analysis_layer_sha256'] == d.file_hash(c.LAYER)
            assert len(raw['scores']) == len(adjusted['scores']) == 25
        checked_scores = []
        bindings = []
        for index, row in enumerate(rows):
            case_id = row['case_id']
            if not (target / case_id / 'score.json').exists():
                assert not complete
                continue
            saved = s.runtime.read(target / case_id / 'score.json')
            if complete:
                assert saved == raw['scores'][index]
                new = adjusted['scores'][index]
            else:
                new, _ = c.adjusted(saved, layer)
            payload = s.judge_input(cases[case_id], row)
            key = s.cache_key(payload, frozen['judge_identity'])
            assert key == saved['cache_key']
            unique_keys.add(key)
            cache = s.CACHE / key
            result = cache / 'results/context-01'
            assert s.runtime.read(cache / 'inputs/context-01.json') == payload
            assert s.runtime.read(cache / 'identity.json') == frozen['judge_identity']
            for filename, field in [('prompt.md', 'prompt_sha256'), ('schema.json', 'schema_sha256')]:
                assert d.file_hash(cache / filename) == frozen['judge_identity'][field]
            seal = s.runtime.read(cache / 'result-seal.json')
            assert set(seal) == {'answer.json', 'record.json', 'intent.json', 'command.json', 'stdout.jsonl', 'stderr.txt'}
            for name, value in seal.items():
                assert d.file_hash(result / name) == value
            answer = s.runtime.read(result / 'answer.json')
            record = s.runtime.read(result / 'record.json')
            assert record['success']
            assert s.digest(answer) == saved['judge_result_sha256']
            events, malformed, usage = s.runtime.events_and_usage(result / 'stdout.jsonl')
            messages = [e['item']['text'] for e in events if e.get('type') == 'item.completed'
                        and e.get('item', {}).get('type') == 'agent_message']
            assert not malformed and messages and json.loads(messages[-1]) == answer
            assert usage == record['usage']
            assert record['input_sha256'] == s.runtime.legacy.text_sha(json.dumps(payload, ensure_ascii=False))
            context = '\n\n'.join(b['text'] for b in payload['blocks'])
            merged = s.merge(cases[case_id], row, context, corpus, answer, certificates)
            assert all(saved[k] == v for k, v in merged.items())
            expected, ids = c.adjusted(saved, layer)
            assert expected == new
            if ids:
                bindings.append({'case_id': case_id, 'records': ids, 'context_sha256': saved['context_sha256'], 'cache_key': key})
                adjusted_changes.append({'configuration': cid, **bindings[-1]})
            checked_scores.append(new)
            if not complete:
                partial_bindings.append({'configuration': cid, 'case_id': case_id,
                                         'cache_key': key, 'context_sha256': saved['context_sha256']})
        if not complete:
            continue
        assert bindings == adjusted['applied_adjudications']
        for summary, scores in [(raw, raw['scores']), (adjusted, checked_scores)]:
            assert summary['full25'] == s.aggregate(scores)
            assert summary['legacy15'] == s.aggregate(scores, legacy_only=True)
        verified.append({'configuration': cid, 'cases': len(rows), 'summary_sha256': d.file_hash(target / 'summary.json'),
                         'adjusted_sha256': d.file_hash(c.STATE / 'adjusted' / (cid + '.json'))})
    output = {'at': s.runtime.now(), 'integrity_passed': True, 'completed_configurations': len(verified),
              'configurations': verified, 'unfinished_configurations': partial,
              'verified_completed_case_inputs': 25 * len(verified), 'unique_sealed_judge_inputs': len(unique_keys),
              'verified_retrieved_contexts': retrieved_contexts, 'verified_partial_case_inputs': partial_bindings,
              'frozen_identity_files_verified': len(frozen['identities']),
              'phase_a_files_unchanged': len(s.runtime.read(c.STATE / 'freeze.json')['phase_a_files']),
              'approved_exact_input_adjustments': adjusted_changes, 'gold_prompt_schema_models_unchanged': True,
              'provenance_serialization_tokens_result_seals_and_aggregate_recalculation': True,
              'new_judge_calls': 0, 'new_tokenizer_calls': 0, 'holdout_accessed': False,
              'paid_api_calls': 0, 'production_changed': False,
              'limitation': 'Integrity verification is not independent semantic validation or production safety approval.'}
    output['verified_indices'] = {name: {key: d.checked_index(name)[key] for key in ['documents_sha256', 'queries_sha256']}
                                  for name in ['minilm', 'gemma2', 'qwen3-q4']}
    output['archived_quota_rejections'] = []
    for path in sorted((c.STATE / 'quota-retry-archives').glob('*.json')):
        manifest = s.runtime.read(path)
        archive = (s.ROOT / manifest['archive']).resolve()
        assert archive.is_relative_to(s.CACHE.resolve())
        assert not manifest['failed_record']['success']
        assert all(d.file_hash(archive / name) == value for name, value in manifest['file_sha256'].items())
        output['archived_quota_rejections'].append({'cache_key': manifest['cache_key'], 'archive': manifest['archive'],
                                                   'record_sha256': manifest['file_sha256']['record.json']})
    for path in (output_paths if output_paths is not None else
                 [c.STATE / 'final-audit.v1.json', s.ROOT / 'evals/retrieval_optimization_final_audit.v1.json']):
        path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in output.items() if k not in ['configurations', 'approved_exact_input_adjustments']}))
    return output


if __name__ == '__main__':
    audit()
