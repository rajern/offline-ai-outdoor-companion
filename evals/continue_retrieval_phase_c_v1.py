"""Owner-authorized three-config C continuation using the unchanged frozen workers."""
from copy import deepcopy
import json
from pathlib import Path
import traceback

import continue_retrieval_optimization_v1 as previous
import run_retrieval_optimization_v1 as d
import retrieval_optimization_scoring as s
from optimization_report import consumption
from optimization_resources import Resources

STATE = d.RUN / 'phase-c-v1'
LAYER = s.ROOT / 'evals/retrieval_phase_c_adjudication.v1.json'
AUTHORIZATION = s.ROOT / 'evals/retrieval_phase_c_authorization.v1.json'


def adjusted(raw, layer):
    value, applied = previous.adjusted(raw, s.runtime.read(previous.LAYER))
    if layer['status'] != 'registered_under_explicit_owner_review_authority':
        raise ValueError('Undocumented review authority')
    for record in layer['records']:
        if (raw['case_id'], raw['context_sha256'], raw['cache_key']) != (
                record['case_id'], record['context_sha256'], record['cache_key']):
            continue
        if raw['requires_review'] or raw['certificate_judge_disagreement']:
            raise ValueError('Risk review cannot hide original review/disagreement')
        if record['field'] != 'potentially_misleading' or record['case_id'] not in ['case-13', 'case-19']:
            raise ValueError('Risk review exceeds authorized scope')
        if value['flags'][record['field']] != record['original']:
            raise ValueError('Original risk flag changed')
        value['flags'][record['field']] = record['registered']
        if record['requires_review']:
            value.update(requires_review=True, eligible_for_selection=False)
            value['coverage'].update(requires_review=True, coverage=None, complete_pass=None)
        applied.append(record['id'])
    return value, applied


def sidecar(cid):
    target = d.RUN / 'configurations' / cid
    raw = s.runtime.read(target / 'summary.json')
    scores, bindings = [], []
    for row in raw['scores']:
        value, ids = adjusted(row, s.runtime.read(LAYER))
        scores.append(value)
        if ids:
            bindings.append({'case_id': row['case_id'], 'records': ids,
                             'context_sha256': row['context_sha256'], 'cache_key': row['cache_key']})
    result = {**raw, 'scores': scores, 'full25': s.aggregate(scores),
              'legacy15': s.aggregate(scores, legacy_only=True), 'applied_adjudications': bindings,
              'raw_summary_sha256': d.file_hash(target / 'summary.json'),
              'original_owner_layer_sha256': d.file_hash(previous.LAYER), 'review_layer_sha256': d.file_hash(LAYER)}
    previous.write_once(STATE / 'adjusted' / (cid + '.json'), result)
    return result


def protected_prior(plan):
    paths = [p for config in plan['phase_a'] + plan['phase_b']
             for p in (d.RUN / 'configurations' / config['id']).rglob('*') if p.is_file()]
    paths += list((previous.STATE / 'adjusted').glob('[AB]-*.json'))
    return {str(p.relative_to(d.RUN)): d.file_hash(p) for p in paths}


def prepare():
    s.holdout_guard()
    d.verify()
    previous.check_frozen()
    plan = s.runtime.read(d.RUN / 'plan.json')
    assert [r['id'] for r in plan['phase_c']] == ['C-P1', 'C-P2', 'C-P3']
    authorization = s.runtime.read(AUTHORIZATION)
    selected = s.runtime.read(d.RUN / 'configurations/B-k16-none/config.json')
    assert authorization['configuration'] == selected
    assert (selected['model'], selected['k'], selected['threshold'], selected['packing']) == ('minilm', 16, None, 'P2')
    layer = s.runtime.read(LAYER)
    assert layer['gold_sha256'] == d.file_hash(s.ROOT / 'evals/retrieval_development.v2.yaml')
    assert layer['judge_prompt_sha256'] == d.file_hash(s.PROMPT)
    assert layer['schema_sha256'] == d.file_hash(s.SCHEMA)
    audit = s.runtime.read(s.ROOT / 'evals/retrieval_optimization_final_audit.v1.json')
    assert audit['integrity_passed'] and audit['completed_configurations'] == 28
    for verified in audit['configurations']:
        assert d.file_hash(d.RUN / 'configurations' / verified['configuration'] / 'summary.json') == verified['summary_sha256']
    with Resources() as resources:
        resources.check()
    with s.runtime.JudgeLock():
        s.runtime.recover_active()
        pre = s.runtime.preflight()
        ident = s.identity(pre)
        assert ident == s.runtime.read(d.RUN / 'freeze.json')['judge_identity']
        checks = {s.runtime.read(d.RUN / 'configurations/B-k16-none' / row['case_id'] / 'score.json')['cache_key']
                  for row in d.verify_rows('B-k16-none')}
        checks |= {r['cache_key'] for r in layer['records']}
        for key in sorted(checks):
            assert (s.CACHE / key / 'results/context-01/record.json').exists()
            assert (s.CACHE / key / 'result-seal.json').exists()
            result = s.judge(s.runtime.read(s.CACHE / key / 'inputs/context-01.json'), pre, ident)
            assert result['cache_hit'] and result['calls'] == 0
    d.checked_index('minilm')
    # Only the owner-selected B input bypasses the B dominance gate.
    previous.write_once(d.RUN / 'choice-B.json', {'configuration': selected, 'provisional': True,
        'authority': authorization['authority'], 'limited_override': authorization['limited_override'],
        'authorization_sha256': d.file_hash(AUTHORIZATION), 'production_approval': False})
    for config in plan['phase_a'] + plan['phase_b']:
        sidecar(config['id'])
    previous.write_once(STATE / 'freeze.json', {'code_sha256': d.file_hash(Path(__file__)),
        'authorization_sha256': d.file_hash(AUTHORIZATION), 'review_layer_sha256': d.file_hash(LAYER),
        'choice_B_sha256': d.file_hash(d.RUN / 'choice-B.json'), 'plan_sha256': d.file_hash(d.RUN / 'plan.json'),
        'original_freeze_sha256': d.file_hash(d.RUN / 'freeze.json'), 'protected_A_B_files': protected_prior(plan),
        'configurations': plan['phase_c'], 'preflight_cache_checks': len(checks), 'new_preflight_judge_calls': 0})
    if not (STATE / 'started.json').exists():
        s.runtime.write(STATE / 'started.json', {'at': s.runtime.now(), 'consumption_before': accounted_consumption()})
    return plan


def check_frozen():
    previous.check_frozen()
    frozen = s.runtime.read(STATE / 'freeze.json')
    for path, key in [(Path(__file__), 'code_sha256'), (AUTHORIZATION, 'authorization_sha256'),
                      (LAYER, 'review_layer_sha256'), (d.RUN / 'choice-B.json', 'choice_B_sha256'),
                      (d.RUN / 'plan.json', 'plan_sha256'), (d.RUN / 'freeze.json', 'original_freeze_sha256')]:
        if d.file_hash(path) != frozen[key]:
            raise ValueError('Phase-C frozen identity changed: ' + str(path))
    if protected_prior(s.runtime.read(d.RUN / 'plan.json')) != frozen['protected_A_B_files']:
        raise ValueError('Historical A/B files changed')


def accounted_consumption():
    result = consumption(d.RUN)
    for path in (previous.STATE / 'quota-retry-archives').glob('*.json'):
        manifest = s.runtime.read(path)
        archive = (s.ROOT / manifest['archive']).resolve()
        assert archive.is_relative_to(s.CACHE.resolve())
        assert all(d.file_hash(archive / name) == value for name, value in manifest['file_sha256'].items())
        record = manifest['failed_record']
        result['actual_calls'] += 1
        result['unknown_usage_calls'] += record['usage'] is None
        result['sum_call_seconds'] += record['elapsed_seconds']
        for key, value in (record['usage'] or {}).items():
            result['usage'][key] = result['usage'].get(key, 0) + value
        result['errors'].append({'cache_key': manifest['cache_key'], 'status': 'archived_quota_rejection'})
    return result


def export(status, error=None):
    plan = s.runtime.read(d.RUN / 'plan.json')
    records = []
    for config in plan['phase_a'] + plan['phase_b'] + plan['phase_c']:
        target = d.RUN / 'configurations' / config['id']
        scores = [s.runtime.read(p) for p in sorted(target.glob('case-*/score.json'))]
        record = {'configuration': s.runtime.read(target / 'config.json') if (target / 'config.json').exists() else config,
                  'status': 'partial' if scores else 'not_run', 'judged_cases': len(scores),
                  'partial_scores': [{k: r[k] for k in ['case_id', 'decisions', 'flags', 'requires_review',
                      'certificate_judge_disagreement', 'context_sha256', 'cache_key']} for r in scores]}
        if (target / 'summary.json').exists():
            previous.sidecar(config['id'])  # Preserve the original layer's separate analysis as well.
            raw = s.runtime.read(target / 'summary.json')
            analysis = sidecar(config['id'])
            record.update(status='complete', raw_full25=raw['full25'], adjusted_full25=analysis['full25'],
                          raw_legacy15=raw['legacy15'], adjusted_legacy15=analysis['legacy15'],
                          applied_adjudications=analysis['applied_adjudications'], resources=raw['resources'])
        records.append(record)
    data = {'at': s.runtime.now(), 'status': status, 'error': error,
            'completed': sum(r['status'] == 'complete' for r in records), 'configurations': records,
            'consumption': accounted_consumption(), 'consumption_before_C': s.runtime.read(STATE / 'started.json')['consumption_before'],
            'judge_identity': s.runtime.read(d.RUN / 'freeze.json')['judge_identity'],
            'authorization': s.runtime.read(AUTHORIZATION), 'review_layer': s.runtime.read(LAYER),
            'resources_by_worker': [dict(file=p.name, **s.runtime.read(p)) for p in sorted((previous.STATE / 'resources').glob('*.json'))],
            'holdout_accessed': False, 'paid_api_calls': 0, 'production_changed': False, 'generation_calls': 0}
    path = s.ROOT / 'evals/retrieval_optimization_results.v6.json'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    s.runtime.write(STATE / 'status.json', {'at': data['at'], 'status': status, 'error': error}, replace=True)
    return data


def run():
    plan = prepare()
    export('prepared_C')
    for config in plan['phase_c']:
        cid = config['id']
        check_frozen()
        if not (d.RUN / 'configurations' / cid / 'summary.json').exists():
            print('Continuing', cid, flush=True)
            previous.guarded_worker('retrieve', cid)
            previous.guarded_worker('score', cid)
        else:
            d.verify_rows(cid)
        export('running_C')
        print('Completed', cid, flush=True)
    check_frozen()
    export('comparison_complete')
    print('Exactly 31 configurations complete; no automatic production selection', flush=True)


if __name__ == '__main__':
    s.holdout_guard()
    with s.runtime.JudgeLock(d.EXPERIMENT_LOCK):
        try:
            run()
        except Exception as error:
            if (STATE / 'started.json').exists():
                export('blocked', str(error))
            STATE.mkdir(parents=True, exist_ok=True)
            (STATE / 'failure.txt').write_text(traceback.format_exc(), encoding='utf-8', newline='\n')
            raise
