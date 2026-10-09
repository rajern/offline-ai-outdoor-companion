"""Owner-authorized B/C continuation; original frozen execution stays unchanged."""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import traceback

import run_retrieval_optimization_v1 as d
import retrieval_optimization_scoring as s
from optimization_resources import Resources
from optimization_report import consumption

LAYER = s.ROOT / 'evals/retrieval_embedding_selection_adjudication.approved.v1.json'
HERE = Path(__file__)
STATE = d.RUN / 'continuation-v1'


def write_once(path, value):
    if path.exists():
        if s.runtime.read(path) != value:
            raise ValueError('Continuation identity changed: ' + str(path))
    else:
        s.runtime.write(path, value)


def adjusted(raw, layer):
    """Apply only the owner's exact blinded-input/context bindings, including reuse."""
    result = deepcopy(raw)
    applied = []
    if layer['status'] != 'owner_approved':
        raise ValueError('Unapproved adjudication')
    for record in layer['records']:
        if (raw['case_id'], raw['context_sha256'], raw['cache_key']) != (
                record['case_id'], record['context_sha256'], record['cache_key']):
            continue
        if raw['requires_review'] or raw['certificate_judge_disagreement']:
            raise ValueError('Adjudication cannot hide a new review')
        if 'item' in record:
            index = record['item'] - 1
            if result['decisions'][index] != record['original']:
                raise ValueError('Adjudication original decision changed')
            result['decisions'][index] = record['approved']
            coverage = result['coverage']
            if coverage['gap'] or not coverage['total']:
                raise ValueError('Adjudication cannot convert a knowledge gap')
            coverage['covered'] = sum(v == 'covered' for v in result['decisions'])
            coverage['coverage'] = coverage['covered'] / coverage['total']
            coverage['complete_pass'] = coverage['covered'] == coverage['total']
        else:
            if result['flags'][record['field']] != record['original']:
                raise ValueError('Adjudication original flag changed')
            result['flags'][record['field']] = record['approved']
        applied.append(record['id'])
    return result, applied


def sidecar(cid):
    raw = s.runtime.read(d.RUN / 'configurations' / cid / 'summary.json')
    layer = s.runtime.read(LAYER)
    scores = []
    bindings = []
    for row in raw['scores']:
        value, ids = adjusted(row, layer)
        scores.append(value)
        if ids:
            bindings.append({'case_id': row['case_id'], 'records': ids,
                             'context_sha256': row['context_sha256'], 'cache_key': row['cache_key']})
    result = {**raw, 'scores': scores, 'full25': s.aggregate(scores),
              'legacy15': s.aggregate(scores, legacy_only=True),
              'analysis_layer_sha256': d.file_hash(LAYER), 'applied_adjudications': bindings,
              'raw_summary_sha256': d.file_hash(d.RUN / 'configurations' / cid / 'summary.json')}
    write_once(STATE / 'adjusted' / (cid + '.json'), result)
    return result


def stage_choice(stage, ids):
    """Same conservative frozen dominance rule, using separately adjusted summaries."""
    summaries = [sidecar(cid) for cid in ids]
    if any(not r['full25']['eligible_for_selection'] for r in summaries):
        raise RuntimeError('Unresolved reviews block stage selection')
    candidates = []
    tradeoffs = []
    for candidate in summaries:
        scores = {r['case_id']: r for r in candidate['scores']}
        regressions = []
        for other in summaries:
            for row in other['scores']:
                current = scores[row['case_id']]
                for item, (a, b) in enumerate(zip(current['decisions'], row['decisions']), 1):
                    if b == 'covered' and a != 'covered':
                        regressions.append({'against': other['configuration']['id'],
                            'case_id': row['case_id'], 'item': item, 'type': 'coverage_loss'})
                for flag in ['potentially_misleading', 'contradictory', 'jurisdiction_leakage']:
                    if current['flags'][flag] and not row['flags'][flag]:
                        regressions.append({'against': other['configuration']['id'],
                            'case_id': row['case_id'], 'type': flag})
        tradeoffs.append({'configuration': candidate['configuration']['id'], 'regressions': regressions})
        if not regressions:
            candidates.append(candidate)
    write_once(STATE / ('tradeoffs-' + stage + '.json'), tradeoffs)
    if not candidates:
        raise RuntimeError('Material per-case coverage/safety tradeoffs: no configuration dominates; owner decision required')
    meta = d.checked_index('minilm')
    def order(record):
        q = record['full25']
        return (-q['complete_cases'], -q['micro_coverage'], -q['macro_coverage'],
                q['flags_supported']['irrelevant'], meta['model_size_bytes'] + meta['index_size_bytes'],
                meta['resources']['peak_process_tree_rss_bytes'], meta['resources']['cpu_seconds'],
                record['configuration']['id'])
    chosen = sorted(candidates, key=order)[0]['configuration']
    write_once(d.RUN / ('choice-' + stage + '.json'), {'configuration': chosen, 'compared': ids,
               'provisional': True, 'rule': 'original frozen dominance rule; owner-approved exact-context analysis layer',
               'analysis_layer_sha256': d.file_hash(LAYER)})
    return chosen


def protected_a():
    paths = [p for c in ['A-minilm', 'A-gemma2', 'A-qwen3-q4']
             for p in (d.RUN / 'configurations' / c).rglob('*') if p.is_file()]
    return {str(p.relative_to(d.RUN)): d.file_hash(p) for p in paths}


def prepare():
    d.verify()
    plan = s.runtime.read(d.RUN / 'plan.json')
    if len(plan['phase_b']) != 25 or len(plan['phase_c']) != 3:
        raise ValueError('Expected exactly 28 remaining configurations')
    layer = s.runtime.read(LAYER)
    if layer['gold_sha256'] != d.file_hash(s.ROOT / 'evals/retrieval_development.v2.yaml'):
        raise ValueError('Adjudication gold binding changed')
    if layer['judge_prompt_sha256'] != d.file_hash(s.PROMPT):
        raise ValueError('Adjudication prompt binding changed')
    with s.runtime.JudgeLock():
        s.runtime.recover_active()
        pre = s.runtime.preflight()
        ident = s.identity(pre)
        if ident != s.runtime.read(d.RUN / 'freeze.json')['judge_identity']:
            raise ValueError('Judge identity differs from the frozen experiment')
        cases = {c['id']: c for c in s.load_development()['cases']}
        for cid in ['A-minilm', 'A-gemma2', 'A-qwen3-q4']:
            for row in d.verify_rows(cid):
                saved = s.runtime.read(d.RUN / 'configurations' / cid / row['case_id'] / 'score.json')
                payload = s.judge_input(cases[row['case_id']], row)
                key = s.cache_key(payload, ident)
                if key != saved['cache_key'] or not (s.CACHE / key / 'results/context-01/record.json').exists():
                    raise ValueError('Existing A cache binding missing/changed')
                result = s.judge(payload, pre, ident)
                if not result['cache_hit'] or result['calls'] or s.digest(result['answer']) != saved['judge_result_sha256']:
                    raise ValueError('Existing A judgment changed')
    d.checked_index('minilm')
    for cid in ['A-minilm', 'A-gemma2', 'A-qwen3-q4']:
        sidecar(cid)
    # Assert the complete phase-A delta, rather than just its aggregate.
    changes = []
    for cid in ['A-minilm', 'A-gemma2', 'A-qwen3-q4']:
        old = s.runtime.read(d.RUN / 'configurations' / cid / 'summary.json')['scores']
        new = s.runtime.read(STATE / 'adjusted' / (cid + '.json'))['scores']
        for a, b in zip(old, new):
            if a != b:
                changes.append({'configuration': cid, 'case_id': a['case_id'],
                    'changed_fields': [k for k in a if a[k] != b[k]]})
    expected = [{'configuration': 'A-minilm', 'case_id': 'case-20', 'changed_fields': ['coverage', 'decisions']},
                {'configuration': 'A-gemma2', 'case_id': 'case-13', 'changed_fields': ['flags']}]
    if changes != expected:
        raise ValueError('Unexpected phase-A adjudication delta: ' + str(changes))
    write_once(STATE / 'adjudication-audit.json', {'changes': changes, 'cache_checks': 75, 'fresh_calls': 0})
    selected = next(c for c in plan['phase_a'] if c['id'] == 'A-minilm')
    write_once(d.RUN / 'choice-A.json', {'configuration': selected, 'provisional': True,
        'authority': 'owner explicitly selected MiniLM for phases B/C, 2026-10-09',
        'analysis_layer_sha256': d.file_hash(LAYER), 'production_approval': False})
    rows = d.verify_rows('A-minilm')
    write_once(d.RUN / 'thresholds.json', {'model': 'minilm', 'values': d.threshold_values(rows),
        'method': 'numpy.percentile linear pooled allowed top16',
        'score_count': sum(len(r['candidates_top16']) for r in rows),
        'source_sha256': d.file_hash(d.RUN / 'configurations/A-minilm/retrieved-all.json')})
    write_once(STATE / 'freeze.json', {'code_sha256': d.file_hash(HERE), 'adjudication_sha256': d.file_hash(LAYER),
        'original_freeze_sha256': d.file_hash(d.RUN / 'freeze.json'), 'phase_a_files': protected_a(),
        'threshold_sha256': d.file_hash(d.RUN / 'thresholds.json'), 'planned_remaining': plan['phase_b'] + plan['phase_c'],
        'scope': 'MiniLM B/C only; original frozen scorer/cache identity/packing/resources unchanged'})
    if not (STATE / 'started.json').exists():
        s.runtime.write(STATE / 'started.json', {'at': s.runtime.now(), 'consumption_before': consumption(d.RUN)})
    return plan


def check_frozen():
    freeze = s.runtime.read(STATE / 'freeze.json')
    if freeze['code_sha256'] != d.file_hash(HERE) or freeze['adjudication_sha256'] != d.file_hash(LAYER):
        raise ValueError('Continuation code/layer changed after freeze')
    if freeze['phase_a_files'] != protected_a():
        raise ValueError('Phase A artifacts changed')
    if freeze['original_freeze_sha256'] != d.file_hash(d.RUN / 'freeze.json') or freeze['threshold_sha256'] != d.file_hash(d.RUN / 'thresholds.json'):
        raise ValueError('Original freeze or thresholds changed')


def guarded_worker(command, cid):
    attempts = STATE / 'resources'
    attempts.mkdir(parents=True, exist_ok=True)
    number = len(list(attempts.glob(command + '-' + cid + '-*.json'))) + 1
    with Resources() as resources:
        try:
            resources.check()
            d.worker(command, config_id=cid)
            resources.check()
        finally:
            s.runtime.write(attempts / f'{command}-{cid}-{number:03}.json', resources.result())


def export(status, error=None):
    plan = s.runtime.read(d.RUN / 'plan.json')
    records = []
    for c in plan['phase_a'] + plan['phase_b'] + plan['phase_c']:
        cid = c['id']
        directory = d.RUN / 'configurations' / cid
        scores = [s.runtime.read(p) for p in sorted(directory.glob('case-*/score.json'))]
        entry = {'configuration': s.runtime.read(directory / 'config.json') if (directory / 'config.json').exists() else c,
                 'judged_cases': len(scores), 'status': 'not_run' if not scores else 'partial',
                 'partial_scores': [{k: r[k] for k in ['case_id', 'decisions', 'flags', 'requires_review',
                    'certificate_judge_disagreement', 'context_sha256', 'cache_key']} for r in scores]}
        if (directory / 'summary.json').exists():
            raw = s.runtime.read(directory / 'summary.json')
            adj = sidecar(cid)
            entry.update(status='complete', raw_full25=raw['full25'], adjusted_full25=adj['full25'],
                         raw_legacy15=raw['legacy15'], adjusted_legacy15=adj['legacy15'],
                         applied_adjudications=adj['applied_adjudications'], resources=raw['resources'])
        records.append(entry)
    data = {'at': s.runtime.now(), 'status': status, 'error': error, 'configurations': records,
            'completed': sum(r['status'] == 'complete' for r in records), 'consumption': consumption(d.RUN),
            'consumption_before': s.runtime.read(STATE / 'started.json')['consumption_before'] if (STATE / 'started.json').exists() else None,
            'thresholds': s.runtime.read(d.RUN / 'thresholds.json') if (d.RUN / 'thresholds.json').exists() else None,
            'analysis_layer_sha256': d.file_hash(LAYER), 'holdout_accessed': False, 'paid_api_calls': 0,
            'production_changed': False, 'generation_calls': 0}
    # Source-free export only; never replace historical phase-A reports.
    (s.ROOT / 'evals/retrieval_optimization_results.v4.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    s.runtime.write(STATE / 'status.json', {'at': data['at'], 'status': status, 'error': error}, replace=True)
    return data


def run():
    plan = prepare()
    export('prepared')
    for stage, key in [('B', 'phase_b'), ('C', 'phase_c')]:
        for c in plan[key]:
            cid = c['id']
            check_frozen()
            if not (d.RUN / 'configurations' / cid / 'summary.json').exists():
                print('Continuing', cid, flush=True)
                guarded_worker('retrieve', cid)
                guarded_worker('score', cid)
            else:
                d.verify_rows(cid)
            sidecar(cid)
            export('running-' + stage)
            print('Completed', cid, flush=True)
        stage_choice(stage, [c['id'] for c in plan[key]])
    check_frozen()
    export('complete')
    print('Exactly 31 configurations complete; recommendation only', flush=True)


if __name__ == '__main__':
    s.holdout_guard()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'run'])
    args = parser.parse_args()
    with s.runtime.JudgeLock(d.EXPERIMENT_LOCK):
        try:
            if args.command == 'prepare':
                prepare()
                export('prepared')
            else:
                run()
        except Exception as error:
            export('blocked', str(error))
            (STATE / 'failure.txt').write_text(traceback.format_exc(), encoding='utf-8', newline='\n')
            raise
