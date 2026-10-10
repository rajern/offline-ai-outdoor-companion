"""Offline source-free comparison; never invokes judge or changes experiment code."""
from __future__ import annotations
import json
import statistics
from pathlib import Path
import numpy as np

import run_targeted_retrieval_v1 as t
import continue_retrieval_phase_c_v1 as c
import retrieval_optimization_scoring as s
from optimization_report import consumption


def gap_exposure():
    """Analyst-only known source locations; never imported by retrieval methods."""
    locations = {'case-01': ['source-04-005'], 'case-03': ['source-21-009', 'source-21-010'],
        'case-06': ['source-02-006'], 'case-08': ['source-07-005'], 'case-13': ['source-11-003'],
        'case-17': ['source-08-001', 'source-08-003', 'source-08-004'], 'case-21': ['source-21-009']}
    parents = [t.d.KnowledgeItem(**p) for p in s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']]
    cases = s.load_development()['cases']; output = []
    old = t.d.RUN / 'indices/minilm'; new = t.RUN / 'index'
    if not (new / 'index.json').exists(): return output
    for i, case in enumerate(cases):
        if case['id'] not in locations: continue
        rankings = {}
        for name, index in [('baseline', old), ('window-mean', new)]:
            scores = np.load(index / 'documents.npy') @ np.load(index / 'queries.npy')[i]
            eligible = [n for n, p in enumerate(parents) if t.d.allowed_in_jurisdiction(p, case['jurisdiction'])]
            order = sorted(eligible, key=lambda n: (-float(scores[n]), parents[n].id))
            rankings[name] = {parents[n].id: rank for rank, n in enumerate(order, 1)}
        for source in locations[case['id']]:
            row = {'case_id': case['id'], 'parent_id': source,
                   'ranks': {name: values.get(source) for name, values in rankings.items()}, 'variants': {}}
            parent = next(p for p in parents if p.id == source)
            row['source_text_sha256'] = s.runtime.legacy.text_sha(parent.text)
            for config in s.runtime.read(t.CONFIG)['variants']:
                path = t.RUN / 'configurations' / config['id'] / case['id'] / 'retrieved.json'
                if path.exists():
                    context = s.runtime.read(path)
                    row['variants'][config['id']] = {'delivered': source in [e['item']['id'] for e in context['excerpts']],
                        'context_sha256': context['context_sha256'],
                        'related_trace': [r for r in context['trace'] if source in r['would_add']]}
            output.append(row)
    return output


def compare(current, baseline):
    old = {r['case_id']: r for r in baseline}
    gains, losses, risks, remaining = [], [], [], []
    for row in current:
        prior = old[row['case_id']]
        if not row['coverage']['gap']:
            for i, (a, b) in enumerate(zip(prior['decisions'], row['decisions']), 1):
                identity = {'case_id': row['case_id'], 'item': i,
                            'context_sha256': row['context_sha256'], 'cache_key': row['cache_key']}
                if a != 'covered' and b == 'covered': gains.append(identity)
                if a == 'covered' and b != 'covered': losses.append(identity)
                if b != 'covered': remaining.append(identity)
        for label in ['potentially_misleading', 'contradictory', 'jurisdiction_leakage']:
            if row['flags'][label] and not prior['flags'][label]:
                risks.append({'case_id': row['case_id'], 'flag': label,
                              'context_sha256': row['context_sha256'], 'cache_key': row['cache_key']})
    return {'gains': gains, 'losses': losses, 'new_risks': risks, 'remaining': remaining}


def report():
    progress = s.runtime.read(t.RUN / 'progress.json') if (t.RUN / 'progress.json').exists() else {'status': 'preflight'}
    raw_baseline = s.runtime.read(t.d.RUN / 'configurations/C-P3/summary.json')
    baseline = [c.adjusted(r, s.runtime.read(c.LAYER))[0] for r in raw_baseline['scores']]
    data = {'status': progress['status'], 'error': progress.get('error'),
        'baseline': {'full25': s.aggregate(baseline), 'legacy15': s.aggregate(baseline, legacy_only=True)},
        'variants': [], 'consumption': consumption(t.RUN),
        'original_consumption': c.accounted_consumption(),
        'holdout_accessed': False, 'production_changed': False, 'paid_api_calls': 0}
    lines = ['# M2-06 — målrettet retrieval-runde', '', f'**Status: {data["status"]}.**', '',
        'Tre varianter er frosset samlet før scoring. MiniLM, 16 unike parent-passasjer, ingen terskel, '
        '2 000 tokens, samme kilder/gold/V3-dommer og eksakte adjudikasjonsbindinger. Ingen tidligere '
        'resultater er endret. Se `retrieval_targeted_plan.v2.md` og konfigurasjonsfilen v2. '
        'Teknisk revisjon 02 retter manglende skille mellom avkortet overskrift og brødtekst før scoring. '
        'Første revisjons 75 ubedømte kontekster er bevart; packing-forsøkets 25 kontekster gjenbrukes.', '',
        '| Oppsett | Vurdert | Micro25 | Macro25 | Komplette25 | Micro15 / macro15 / komplette15 | I / M / K / G |',
        '|---|---:|---:|---:|---:|---|---|',
        '| P3 baseline | 25 | 59/72 (81,94 %) | 80,23 % | 15/22 | 41/51 / 78,08 % / 8/13 | 22 / 1 / 0 / 0 |']
    for config in s.runtime.read(t.CONFIG)['variants']:
        target = t.RUN / 'configurations' / config['id']
        scores = [s.runtime.read(p) for p in sorted(target.glob('case-*/score.json'))]
        adjusted = [c.adjusted(r, s.runtime.read(c.LAYER))[0] for r in scores]
        record = {'configuration': config, 'judged_cases': len(scores), 'complete': len(scores) == 25,
                  'comparison': compare(adjusted, baseline),
                  'review_cases': [r['case_id'] for r in scores if r['requires_review']]}
        if (target / 'retrieved-all.json').exists():
            rows = t.verify_rows(config['id'])
            record['resources'] = {'mean_prompt_tokens': statistics.mean(r['prompt_tokens'] for r in rows),
                'max_prompt_tokens': max(r['prompt_tokens'] for r in rows),
                'mean_context_tokens': statistics.mean(r['context_tokens'] for r in rows),
                'passages': sum(r['chunk_count'] for r in rows),
                'excluded_packets': sum(r['budget_excluded_packets'] for r in rows),
                'ranking_seconds': sum(r['ranking_seconds'] for r in rows),
                'retrieval_packing_seconds': sum(r['retrieval_and_packing_seconds'] for r in rows)}
            for name in ['retrieval-resources.json', 'judge-resources.json']:
                if (target / name).exists(): record['resources'][name] = s.runtime.read(target / name)
        if record['complete']:
            q, legacy = s.aggregate(adjusted), s.aggregate(adjusted, legacy_only=True)
            record.update(full25=q, legacy15=legacy)
            pct = lambda x: 'review' if x is None else f'{100*x:.2f}%'
            flags = ' / '.join(str(v) for v in q['flags_supported'].values())
            lines.append(f'| {config["id"]} | 25 | {q["covered"]}/72 ({pct(q["micro_coverage"])}) | '
                f'{pct(q["macro_coverage"])} | {q["complete_cases"]}/22 | '
                f'{legacy["covered"]}/51 / {pct(legacy["macro_coverage"])} / {legacy["complete_cases"]}/13 | {flags} |')
        else:
            lines.append(f'| {config["id"]} | {len(scores)}/25 | ufullstendig | — | — | — | — |')
        data['variants'].append(record)
    if (t.RUN / 'index/index.json').exists():
        data['index'] = t.checked_index()
    data['known_gap_source_exposure'] = gap_exposure()
    data['quota_snapshots'] = [s.runtime.read(p) for folder in [t.PREVIOUS, t.RUN]
                              for p in sorted(folder.glob('quota-*.json'))]
    if data['error']:
        lines += ['', '**Stoppårsak:** ' + data['error']]
    lines += ['', '## Kravgevinster og tap', '']
    def names(records):
        return ', '.join(r['case_id'].replace('case-', '') + '/' + str(r['item']) for r in records) or 'ingen'
    for record in data['variants']:
        delta = record['comparison']
        lines += [f'**{record["configuration"]["id"]}** ({record["judged_cases"]}/25): gevinster {names(delta["gains"])}; '
                  f'tap {names(delta["losses"])}. Udekket i scorede caser: {names(delta["remaining"])}. '
                  f'Nye sikkerhetsflagg: {json.dumps(delta["new_risks"], ensure_ascii=False)}.', '']
    lines += ['## Ressurser og abonnement', '',
        'Indeksarbeid og ferske enkeltspørsmål måles separat fra ranking/packing på lagrede spørsmålsvektorer. '
        'Tid påvirkes av token-cache og integritetskontroller. Originalmodell og original indeks gjenbrukes '
        'for packing-forsøket; gammel indeksbyggetid er ikke en ny sammenlignbar benchmark. '
        'Windows-målinger dokumenterer ikke mobilens minne eller energibruk. '
        'Prosessgrense 4 GiB og tilgjengelig-RAM-reserve 256 MiB er uendret.', '',
        'Nye kall/tokens: `' + json.dumps(data['consumption'], ensure_ascii=False) + '`.', '',
        'Historiske A+B+C-tokens holdes separat: `' + json.dumps(data['original_consumption'], ensure_ascii=False) + '`.', '',
        'Reasoning inngår i output; prefix-cached input inngår i input. Ingen betalt API-fallback eller automatisk kvotereset.', '',
        'Registrerte kvotevinduer: `' + json.dumps(data['quota_snapshots'], ensure_ascii=False) + '`. '
        'Dette er delt kontobruk; prosentendringer kan ikke tilskrives dommerkallene alene.', '',
        '## Beslutningsstatus', '',
        'Ingen automatisk produksjonsvinner. Alle nye sikkerhetsflagg, kravtap og viktige positive vurderinger '
        'må kildegjennomgås før anbefaling. Et ufullstendig eller review-blokkert forsøk kan ikke velges. '
        'De tre forhåndsdefinerte kunnskapshullene er fortsatt separate og gir ikke automatisk komplett pass. '
        'Det gjentatte utviklingssettet gir kalibreringsresultater, ikke uavhengig sikkerhetsvalidering.']
    s.runtime.write(s.ROOT / 'evals/retrieval_targeted_comparison.v1.json', data, replace=True)
    (s.ROOT / 'evals/retrieval_targeted_report.v1.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(data['status'], 'judged', [v['judged_cases'] for v in data['variants']], flush=True)


if __name__ == '__main__':
    s.holdout_guard(); report()
