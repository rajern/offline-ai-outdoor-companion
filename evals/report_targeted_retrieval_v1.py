"""Offline source-free comparison; never invokes judge or changes experiment code."""
from __future__ import annotations
import json
import statistics
from pathlib import Path
from datetime import datetime
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
        'holdout_accessed': False, 'production_changed': False, 'paid_api_calls': 0,
        'recommendation': None, 'decision_status': 'pending_complete_scoring_and_source_review'}
    compatibility = t.RUN / 'scoring-metadata-v1/freeze.json'
    if compatibility.exists():
        data['scoring_metadata_compatibility'] = s.runtime.read(compatibility)
    if (t.RUN / 'freeze.json').exists():
        frozen = s.runtime.read(t.RUN / 'freeze.json')
        data['judge_identity'] = frozen['judge_identity']
        data['technical_sealed_cache_checks'] = sum(s.runtime.read(folder / 'freeze.json')['preflight_cache_checks']
            for folder in [t.PREVIOUS, t.RUN])
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
                  'comparison': compare(adjusted, baseline) if adjusted else None,
                  'scored_comparison_available': bool(adjusted),
                  'review_cases': [r['case_id'] for r in scores if r['requires_review']]}
        rows = [s.runtime.read(p) for p in sorted(target.glob('case-*/retrieved.json'))]
        record['retrieved_cases'] = len(rows)
        if rows:
            if (target / 'retrieved-all.json').exists(): rows = t.verify_rows(config['id'])
            record['resources'] = {'mean_prompt_tokens': statistics.mean(r['prompt_tokens'] for r in rows),
                'measured_cases': len(rows), 'all25_comparable': len(rows) == 25,
                'max_prompt_tokens': max(r['prompt_tokens'] for r in rows),
                'mean_context_tokens': statistics.mean(r['context_tokens'] for r in rows),
                'passages': sum(r['chunk_count'] for r in rows),
                'excluded_packets': sum(r['budget_excluded_packets'] for r in rows),
                'ranking_seconds': sum(r['ranking_seconds'] for r in rows),
                'retrieval_packing_seconds': sum(r['retrieval_and_packing_seconds'] for r in rows)}
            for name in ['retrieval-resources.json', 'judge-resources.json']:
                if (target / name).exists(): record['resources'][name] = s.runtime.read(target / name)
            record['resources']['retrieval_attempts'] = [s.runtime.read(p) for p in
                sorted((target / 'retrieval-resource-attempts').glob('attempt-*.json'))]
            record['resources']['judge_attempts'] = [s.runtime.read(p) for p in
                sorted((target / 'judge-resource-attempts').glob('attempt-*.json'))]
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
        data['index']['fresh_query_vector_bytes_equal_baseline'] = (
            np.load(t.RUN / 'index/queries.npy').tobytes() ==
            np.load(t.d.RUN / 'indices/minilm/queries.npy').tobytes())
    data['known_gap_source_exposure'] = gap_exposure()
    data['quota_snapshots'] = [s.runtime.read(p) for folder in [t.PREVIOUS, t.RUN]
                              for p in sorted(folder.glob('quota-*.json'))]
    latest_quota = max(data['quota_snapshots'], key=lambda q: datetime.fromisoformat(
        q['at'].replace(' UTC', '+00:00').replace(' ', 'T', 1))) if data['quota_snapshots'] else None
    review = s.ROOT / 'evals/retrieval_targeted_preflight_review.v1.json'
    if review.exists(): data['pre_scoring_source_review'] = s.runtime.read(review)
    source_review = s.ROOT / 'evals/retrieval_targeted_source_review.v1.json'
    if source_review.exists(): data['source_review'] = s.runtime.read(source_review)
    required = s.ROOT / 'evals/retrieval_targeted_review_required.v1.json'
    if required.exists():
        data['required_source_review'] = s.runtime.read(required)
        data['decision_status'] = 'blocked_source_review_and_incomplete_combined'
        data['analytical_selection_blocked'] = True
        data['best_observed_complete_variant'] = 'T-ranking'
    if data['error']:
        lines += ['', '**Stoppårsak:** ' + data['error']]
    if required.exists():
        lines += ['', '## Metodisk stopp før tredje variant', '',
            'Case 16 har identiske trykk-/liggende-instrukser fra `source-02-007/008` i P3, ranking og packing. '
            'Packing flagges som misvisende; de andre flagges ikke. Packing legger til en innledning om stort blodtap, '
            'men ingen meningsfull sikkerhetsforskjell som forklarer flaggskiftet er etablert. '
            'Dette er `requires_review` i et separat kontekstbundet analyselag; rå dommerresultater og historiske scorer er bevart. '
            'En ny risiko kan ikke fastslås bare fra flaggskiftet. '
            'Se `retrieval_targeted_review_required.v1.json` for eksakte bindinger og beslutningen som gjenstår.', '',
            'Ranking er beste **fullførte observerte** variant med én bekreftet kravgevinst og ingen kravtap. '
            'Packing taper 12 krav for tre gevinster og kan ikke anbefales. '
            'Den kombinerte varianten har 25 kontrollerte kontekster, men er ikke scoret. '
            'Ingen endelig anbefaling eller produksjonsendring gjøres før risikovurderingen er konsistent; '
            'P3 forblir eksisterende utviklingsgrunnlag. Kvoteavslag utløste ikke dette stoppet.', '',
            'Ranking mangler fortsatt 01/1–3, 03/3–4, 06/1, 08/4, 13/1–2, 17/1–2 og 21/2. '
            'Det er ikke klart for holdout. Neste steg er avgrenset adjudikasjon av case 16 under eksisterende V3-regler, '
            'med vurdering av resterende case 13/17-risiko. Ved senere autorisert gjenopptakelse beholdes '
            'de 50 vurderingene og alle 75 kontekstene; kun kombinert scoring gjenstår.']
    if compatibility.exists():
        lines += ['', 'En teknisk scoreradapter kompletterer `section_count` fra dokument/seksjon i leverte utdrag. '
            'De 75 retrieval-filene, dommerinputene, prompten og scorerreglene er uendret og hashbundet separat. '
            'Første lagrede dommersvar gjenbrukes etter metadatafeilen; ingen inferens gjentas. '
            'Regresjonskontrollen viser identisk output fra gammel scorer med fullstendig metadata.']
    lines += ['', '## Kjøring og bevarte tekniske stopp', '',
        '| Variant | Lagrede kontekster | Dommervurderinger |', '|---|---:|---:|']
    for record in data['variants']:
        lines.append(f'| {record["configuration"]["id"]} | {record["retrieved_cases"]}/25 | {record["judged_cases"]}/25 |')
    for record in data['variants']:
        for attempt in record.get('resources', {}).get('retrieval_attempts', []):
            if attempt['exception_type']:
                lines += ['', f'Stoppmåling {record["configuration"]["id"]}: '
                    f'{attempt["minimum_available_ram_bytes"]/1048576:.2f} MiB tilgjengelig RAM '
                    f'(krav 256 MiB); topp prosess-tre-RSS {attempt["peak_process_tree_rss_bytes"]/1048576:.2f} MiB '
                    f'(grense 4096 MiB). Tilgjengelig vertsmaskin-RAM utløste stoppet; ekstern årsak er ikke fastslått. '
                    'Ingen automatisk retry eller lemping av grensen.']
    lines += ['', '## Kravgevinster og tap', '']
    def names(records):
        return ', '.join(r['case_id'].replace('case-', '') + '/' + str(r['item']) for r in records) or 'ingen'
    for record in data['variants']:
        delta = record['comparison']
        if delta is None:
            lines += [f'**{record["configuration"]["id"]}**: kravgevinster, kravtap, udekkede krav og nye '
                      'dommerflagg er **ikke vurdert** (0/25 scoret). Fravær av score er ingen dokumentasjon på fravær av risiko.', '']
            continue
        lines += [f'**{record["configuration"]["id"]}** ({record["judged_cases"]}/25): gevinster {names(delta["gains"])}; '
                  f'tap {names(delta["losses"])}. Udekket i scorede caser: {names(delta["remaining"])}. '
                  'Nye dommerflagg: ' + (', '.join(r['case_id'].replace('case-', '') + '/' + r['flag']
                      for r in delta['new_risks']) or 'ingen') + '. Eksakte bindinger finnes i sammenlignings-JSON.', '']
    lines += ['## Ressurser og abonnement', '',
        'Indeksarbeid og ferske enkeltspørsmål måles separat fra ranking/packing på lagrede spørsmålsvektorer. '
        'Tid påvirkes av token-cache og integritetskontroller. Originalmodell og original indeks gjenbrukes '
        'for packing-forsøket; gammel indeksbyggetid er ikke en ny sammenlignbar benchmark. '
        'Windows-målinger dokumenterer ikke mobilens minne eller energibruk. '
        'Prosessgrense 4 GiB og tilgjengelig-RAM-reserve 256 MiB er uendret.', '',
        f'Tekniske forseglede cachekontroller: {data.get("technical_sealed_cache_checks", 0)}; '
        'disse utløser ingen fersk dommerinferens. Nye kall og cachetreff for konfigurasjonene loggføres separat nedenfor. '
        'GPT-6.1 Sol / Codex CLI / Medium / ChatGPT-auth og CLI-versjon er verifisert mot den frosne identiteten; '
        'CLI-resultatformatet eksponerer fortsatt ikke faktisk servermodell/revisjon.', '',
        f'Nye abonnementskall: {data["consumption"]["actual_calls"]}; '
        f'vellykkede {data["consumption"]["successful_calls"]}; cachegjenbruk {data["consumption"]["cache_hits"]}. '
        f'Input {data["consumption"]["usage"]["input_tokens"]:,}, output {data["consumption"]["usage"]["output_tokens"]:,}, '
        f'reasoning {data["consumption"]["usage"]["reasoning_output_tokens"]:,}; '
        f'total {data["consumption"]["usage"]["total_tokens"]:,} tokens. '
        f'Dommerkalletid {data["consumption"]["sum_call_seconds"]/60:.2f} minutter.', '',
        f'Historiske A+B+C-tokens holdes separat: {data["original_consumption"]["usage"]["total_tokens"]:,}. '
        f'Samlet kjent forbruk {data["original_consumption"]["usage"]["total_tokens"] + data["consumption"]["usage"]["total_tokens"]:,}; '
        'ett historisk kvoteavslag har ukjent tokenbruk. '
        f'Feil i nye dommerkall: {len(data["consumption"]["errors"])}.', '',
        'Reasoning inngår i output; prefix-cached input inngår i input. Ingen betalt API-fallback eller automatisk kvotereset.', '',
        (f'Siste registrerte kvote: {latest_quota["primary"]["usedPercent"]} % av femtimersvinduet og '
         f'{latest_quota["secondary"]["usedPercent"]} % av uken brukt. ' if latest_quota else 'Kvote er ikke registrert. ')
        +
        'Dette er delt kontobruk; prosentendringer kan ikke tilskrives dommerkallene alene. '
        'Alle snapshots og detaljerte tokenfelt er bevart i sammenlignings-JSON.', '',
        '## Beslutningsstatus', '',
        'Ingen automatisk produksjonsvinner. Alle nye sikkerhetsflagg, kravtap og viktige positive vurderinger '
        'må kildegjennomgås før anbefaling. Et ufullstendig eller review-blokkert forsøk kan ikke velges. '
        'De tre forhåndsdefinerte kunnskapshullene er fortsatt separate og gir ikke automatisk komplett pass. '
        'Det gjentatte utviklingssettet gir kalibreringsresultater, ikke uavhengig sikkerhetsvalidering.']
    if data['variants'] and not any(v['judged_cases'] for v in data['variants']):
        lines += ['', 'Ingen nye micro/macro-scorer, komplette caser eller dommerflagg kan rapporteres. '
            'Baselinen 59/72 og 15/22 beholdes som utviklingsgrunnlag; nye varianter kan ikke anbefales eller rangeres ennå. '
            'Kontrollsettet er fortsatt ikke aktuelt: de 13 tidligere dokumenterte kravmanglene er ikke avklart gjennom denne kjøringen.', '',
            'Etter frigjort RAM og eierens beskjed om gjenopptakelse kjøres samme '
            '`run_targeted_retrieval_v1.py run`. Den verifiserer/rebruker indeks, 25 packing-kontekster og 22 ranking-kontekster, '
            'ferdigstiller de siste tre ranking-kontekstene og kombinert variant, og kontrollerer alle input før dommerkall. '
            'Ingen justering av de frosne metodene fra disse observasjonene.']
    if data.get('index'):
        index = data['index']; memory = index['resources']
        lines += ['', 'Korrigert indeks: '
            f'{index["window_inputs"]} embedding-visninger, null avkortet brødtekst, '
            f'{index["header_truncated_parents"]} avkortede metadataoverskrifter; '
            f'bygging {index["total_build_seconds"]:.2f} s / varm embedding {index["build_seconds_warm"]:.2f} s. '
            f'CPU {memory["cpu_seconds"]:.2f} s; maksimal indeksbygge-RSS {memory["peak_process_tree_rss_bytes"]/1048576:.2f} MiB; '
            f'minimum tilgjengelig RAM {memory["minimum_available_ram_bytes"]/1048576:.2f} MiB. '
            f'Fersk query-embedding snitt {1000*statistics.mean(index["query_embedding_seconds"]):.2f} ms / '
            f'maks {1000*max(index["query_embedding_seconds"]):.2f} ms. '
            f'Query-vektorbytes identiske med baseline: {index["fresh_query_vector_bytes_equal_baseline"]}. '
            f'Modell {index["model_size_bytes"]/1e6:.3f} MB; parent-indeks {index["parent_index_size_bytes"]/1e6:.3f} MB; '
            f'diagnostiske vindusvektorer {index["window_index_size_bytes"]/1e6:.3f} MB. '
            'Indeksbygge-RSS er ikke en måling av mobilappens RAM under vanlig spørsmålskjøring.']
    lines += ['', '| Variant | Målte caser | Prompt snitt / maks | Kontekst snitt | Passasjer / forkastede pakker | Ranking / packing s |',
              '|---|---:|---:|---:|---:|---:|']
    for record in data['variants']:
        if 'resources' not in record: continue
        r = record['resources']
        lines.append(f'| {record["configuration"]["id"]} | {r["measured_cases"]} | '
            f'{r["mean_prompt_tokens"]:.2f} / {r["max_prompt_tokens"]} | {r["mean_context_tokens"]:.2f} | '
            f'{r["passages"]} / {r["excluded_packets"]} | {r["ranking_seconds"]:.4f} / {r["retrieval_packing_seconds"]:.2f} |')
    lines += ['', 'Ufullstendige ressursutvalg kan ikke sammenlignes som like store utvalg. Packing-målingene '
        'er fra første revisjons uendrede, gjenbrukte input; ranking-målingene er fra korrigert revisjon.']
    lines += ['', '| Fullført dommerfase | CPU s | Topp RSS MiB | Min tilgjengelig RAM MiB |',
              '|---|---:|---:|---:|']
    for record in data['variants']:
        memory = record.get('resources', {}).get('judge-resources.json')
        if memory:
            lines.append(f'| {record["configuration"]["id"]} | {memory["cpu_seconds"]:.2f} | '
                f'{memory["peak_process_tree_rss_bytes"]/1048576:.2f} | {memory["minimum_available_ram_bytes"]/1048576:.2f} |')
    lines += ['', 'CPU/RAM gjelder lokal, overvåket dommerfase, ikke servermodellens ressurser eller alle hashkontroller. '
        'Begge fullførte faser bestod uendrede grenser. Metadatafeilens første ressurslogg beholdes separat. '
        'Flaggtall i hovedtabellen er dommervurderinger med tidligere godkjente eksakte lag; '
        'de manuelle risikoreviewene endrer ikke disse tallene og blokkerer en endelig anbefaling.']
    if data.get('pre_scoring_source_review'):
        lines += ['', '## Kildefunn før scoring', '',
            'Dette er eksakt kontekstbundet kildegjennomgang, uten nye adjudikasjoner eller tildelte dekningspoeng.', '',
            '- Packing/case 07: `source-03-006` forkastes ved 2 305 prompttokens. Symptom- og legekontakttekst er levert, '
            'mens baselinens komplette førstehjelpspassasje mangler. Det er en konkret eksponeringsregresjon for 07/1–3.',
            '- Packing/case 17: `source-08-011` leverer generell legevaktinstruks under anafylaksitittel, mens akuttpassasjene '
            '`source-08-001/003/004` mangler. Samme risiko som tidligere P1 er gjeninnført; varianten kan ikke anbefales på totalscore.',
            '- Packing/case 13: `source-11-003` er faktisk levert, med aktivering ved livsfare og ved usikkerhet. '
            'Generelle 113-instrukser finnes fortsatt; risikovurdering av hele den nye konteksten gjenstår.',
            '- Ranking: bruddpassasjen flyttes 20→12, men forkastes ved 2 131 tokens; kjemipassasjen flyttes 13→7 og leveres i case 03. '
            'Kokepassasjen forkastes ved 2 068 tokens. Dette er kildeeksponering, ikke scorede kravgevinster.',
            '- Ytre blødning/113 (rang 47), full pust/HLR (22), nødpeiler (17) og anafylaksisymptomer/akuttkilder (23/44/52) '
            'er fortsatt utenfor den nye rangeringens topp 16. Å representere hele teksten løser ikke disse alene.', '',
            'De fulle bindingene, sporene og source-teksthashene finnes i maskinlesbar sammenligning og separat preflight-review. '
            'Dette dokumenterer effekt av den nye representasjonen samlet; det isolerer ikke avkorting som eneste årsak.']
    if data.get('source_review'):
        lines += ['', '## Kildekontroll av scorede resultater', '',
            'Separat kontroll med eksakt kontekst- og cachebinding, uten endrede råscorer eller nye adjudikasjoner.']
        for review in data['source_review']['reviews']:
            lines.append(f'- {review["configuration"]}/{review["case_id"]}: {review["conclusion"]}')
    s.runtime.write(s.ROOT / 'evals/retrieval_targeted_comparison.v1.json', data, replace=True)
    (s.ROOT / 'evals/retrieval_targeted_report.v1.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(data['status'], 'judged', [v['judged_cases'] for v in data['variants']], flush=True)


if __name__ == '__main__':
    s.holdout_guard(); report()
