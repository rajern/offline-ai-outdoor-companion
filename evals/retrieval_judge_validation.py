"""Prepare/run/analyze frozen Codex-only stress and saved-history validation."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
import json
from pathlib import Path
import random
import statistics

import codex_judge_runtime as runtime
from codex_judge_runtime import legacy

ROOT = runtime.ROOT
CONFIG = ROOT / 'evals/retrieval_judge_validation.v2.json'
BASE = ROOT / 'knowledge/local/diagnostics/retrieval-judge-validation-v2-2026-10-08'
CODE = [Path(__file__).resolve(), ROOT/'evals/codex_judge_runtime.py',
        ROOT/'evals/retrieval_judge_pilot.py', CONFIG]


def check_directory(directory):
    directory = directory.resolve()
    if not directory.is_relative_to(runtime.LOCAL.resolve()):
        raise ValueError('Source-bearing outputs must stay under ignored knowledge/local')
    return directory


def prepare(stage, directory):
    if directory.exists():
        raise FileExistsError('New stage directory required; never overwrite an existing freeze')
    config = runtime.read(CONFIG)
    prompt_path, schema_path = ROOT/config['prompt'], ROOT/config['schema']
    schema = runtime.read(schema_path)
    legacy.Draft202012Validator.check_schema(schema)
    entries, hashes = [], {}
    if stage == 'stress':
        data_path = ROOT/config['stress_data']
        data = runtime.read(data_path)
        selected = data['cases'] + [next(c for c in data['cases'] if c['test_id']==t) for t in data['repeat_test_ids']]
        if len(data['cases']) != 15 or len(selected) != 18:
            raise ValueError('Expected 15 synthetic tests and three planned repeats')
        for number, case in enumerate(selected,1):
            entries.append({'payload':case['input'], 'reference':case['expected'],
                            'test_id':case['test_id'], 'purpose':case['purpose'],
                            'expected_result':case['expected_result'], 'repeat':number>15})
        hashes[str(data_path.relative_to(ROOT))] = legacy.sha(data_path)
    else:
        # Only the explicitly named original nine; no directory traversal of evals.
        lock = runtime.read(ROOT/'evals/retrieval_foundation.lock.json')
        dev_path = ROOT/'evals/retrieval_development.v2.yaml'
        if legacy.sha(dev_path) != lock['files']['evals/retrieval_development.v2.yaml']['sha256']:
            raise ValueError('Development identity changed')
        if legacy.sha(ROOT/'knowledge/local/knowledge.json') != lock['corpus_sha256']:
            raise ValueError('Corpus identity changed')
        cases = legacy.yaml.safe_load(dev_path.read_text(encoding='utf-8'))['cases'][:15]
        pilot = runtime.read(legacy.CONFIG)
        selected = {c['id']:c for c in cases if c['id'] in config['validation_cases']}
        if set(selected) != {c['id'] for c in cases} - set(pilot['cases']) or len(selected)!=9:
            raise ValueError('Validation must be exactly the nine non-pilot legacy cases')
        for mode, folder in pilot['historical_runs'].items():
            source = ROOT/'knowledge/local/diagnostics'/folder
            rows_path, refs_path = source/'retrieved-all.json', source/'scoring.json'
            refs = runtime.read(refs_path)
            for path in [rows_path, refs_path]: hashes[str(path.relative_to(ROOT))] = legacy.sha(path)
            for row in runtime.read(rows_path):
                if row['configuration'] != mode or row['case_id'] not in selected:
                    continue
                if row['corpus_hash'] != lock['corpus_sha256'] or row['gold_hash'] != lock['gold_legacy_immutable']:
                    raise ValueError('Historical corpus/gold identity differs')
                context_path = source/mode/row['case_id']/'context.txt'
                context = context_path.read_text(encoding='utf-8')
                if '\n\n'.join(b['text'] for b in legacy.serialize_blocks(row['excerpts'])) != context:
                    raise ValueError('Saved delivered context differs')
                if legacy.text_sha(context) != row['context_sha256']:
                    raise ValueError('Saved context hash differs')
                for excerpt in row['excerpts']:
                    if not excerpt['item'].get('license') or not excerpt['item']['metadata'].get('licence_url'):
                        raise ValueError('Reuse metadata missing')
                case = selected[row['case_id']]
                payload = legacy.judge_input(case, row)
                payload.pop('expected_result')  # Cohort/gap classification is private.
                entries.append({'payload':payload, 'reference':refs[mode][row['case_id']],
                                'configuration':mode, 'expected_result':case['expected_result'],
                                'context_sha256':row['context_sha256']})
                hashes[str(context_path.relative_to(ROOT))] = legacy.sha(context_path)
        if len(entries)!=45:
            raise ValueError('Expected 45 saved contexts')
        random.Random(config['selection_seed']).shuffle(entries)
    directory.mkdir(parents=True)
    index = []
    for number, entry in enumerate(entries,1):
        inp = entry['payload']
        cid = f'context-{number:02}'
        meta = {k:v for k,v in entry.items() if k not in {'payload','reference'}}
        meta.update(context_id=cid, case_id=inp['case_id'], input_sha256=legacy.text_sha(json.dumps(inp,ensure_ascii=False)))
        runtime.write(directory/'inputs'/(cid+'.json'), inp)
        runtime.write(directory/'references'/(cid+'.json'), entry['reference'])
        index.append(meta)
    runtime.write(directory/'index.json', index)
    runtime.write(directory/'schema.json', schema)
    runtime.write(directory/'settings.json', {**config,'stage':stage})
    (directory/'prompt.md').write_text(prompt_path.read_text(encoding='utf-8'),encoding='utf-8')
    # Preserve source code bytes as well as hashes for later audit/version changes.
    code_paths = CODE + [prompt_path, schema_path, ROOT/config['stress_data']]
    for path in code_paths:
        snapshot = directory/'artifacts'/path.name
        snapshot.parent.mkdir(parents=True,exist_ok=True)
        snapshot.write_bytes(path.read_bytes())
    protected = {str(p.relative_to(ROOT)):legacy.sha(p) for p in legacy.protected_files()}
    # All original pilot records stay intact, not just the nine excluded questions.
    old_index = runtime.read(legacy.DEFAULT_RUN/'index.json')
    for alternative in ['luna-api','sol-api','sol-codex']:
        for meta in old_index:
            for name in ['raw.json','answer.json','record.json']:
                path = legacy.DEFAULT_RUN/'results'/alternative/meta['context_id']/name
                protected[str(path.relative_to(ROOT))] = legacy.sha(path)
    private_paths = [directory/'index.json',directory/'schema.json',directory/'settings.json',directory/'prompt.md']
    private_paths += list((directory/'inputs').glob('*.json')) + list((directory/'references').glob('*.json'))
    private_paths += list((directory/'artifacts').glob('*'))
    freeze = {'created_at':runtime.now(), 'stage':stage,'planned_calls':len(index),
              'protected_files':protected,'historical_inputs':hashes,
              'code_hashes':{str(p.relative_to(ROOT)):legacy.sha(p) for p in code_paths},
              'private_files':{str(p.relative_to(directory)):legacy.sha(p) for p in private_paths},
              'holdout_accessed':False,'api_calls_permitted':False,
              'reference_caution':config['reference_caution']}
    runtime.write(directory/'freeze.json', freeze)
    print(json.dumps({'stage':stage,'prepared':len(index),'unique_inputs':len({m['input_sha256'] for m in index})}))


def verify(directory, *, code=True):
    frozen = runtime.read(directory/'freeze.json')
    for field in ['protected_files','historical_inputs'] + (['code_hashes'] if code else []):
        for name, expected in frozen[field].items():
            if legacy.sha(ROOT/name) != expected:
                raise ValueError(f'Frozen {field} changed: {name}')
    for name, expected in frozen['private_files'].items():
        if legacy.sha(directory/name) != expected:
            raise ValueError('Frozen input/artifact changed: '+name)
    return frozen


def run(directory):
    verify(directory)
    with runtime.JudgeLock():
        if runtime.ACTIVE.exists() and runtime.read(runtime.ACTIVE)['state']=='in_flight':
            verify(Path(runtime.read(runtime.ACTIVE)['run_dir']))
        runtime.recover_active()
        index = runtime.read(directory/'index.json')
        missing = [m for m in index if not (directory/'results'/m['context_id']/'record.json').exists()]
        if not missing:
            print('All attempts recorded; no new inference')
            return
        pre = runtime.preflight()  # CLI authentication/catalog only, no API.
        pre_path = directory/'preflight.json'
        if pre_path.exists():
            old = runtime.read(pre_path)
            if old['cli_version'] != pre['cli_version'] or old['model_requested'] != pre['model_requested']:
                raise RuntimeError('CLI/model changed since first call; no silent substitution')
        else:
            runtime.write(pre_path, pre)
        for meta in missing:
            record = runtime.execute(directory,meta,pre,timeout=runtime.read(directory/'settings.json')['timeout_seconds'])
            usage = record['usage'] or {}
            print(f"{meta['context_id']} {meta['case_id']}: {'valid' if record['success'] else 'FAILED'}; "
                  f"tokens={usage.get('total_tokens','unknown')}; seconds={record.get('elapsed_seconds')}",flush=True)
            if not record['success']:
                break  # Inspect before further calls; never automatically retry.
    verify(directory)


def summarize(directory):
    verify(directory, code=False)
    index = runtime.read(directory/'index.json')
    stage = runtime.read(directory/'settings.json')['stage']
    counts, tokens, latencies, details, rows = Counter(),Counter(),[],[],[]
    for meta in index:
        out = directory/'results'/meta['context_id']
        if not (out/'record.json').exists(): continue
        record = runtime.read(out/'record.json')
        counts['attempted']+=1
        usage = record.get('usage') or {}
        for key,value in usage.items():
            if isinstance(value,int): tokens[key]+=value
        counts['usage_unknown']+=int(not record.get('usage_known'))
        if record.get('elapsed_seconds') is not None: latencies.append(record['elapsed_seconds'])
        else: counts['elapsed_unknown']+=1
        if not record['success']:
            counts['invalid_or_failed']+=1
            details.append({**meta,'type':'invalid','errors':record['validation_errors']})
            continue
        answer = runtime.read(out/'answer.json')
        inp = runtime.read(directory/'inputs'/(meta['context_id']+'.json'))
        reference = runtime.read(directory/'references'/(meta['context_id']+'.json'))
        counts['valid']+=1
        counts['requires_review']+=int(answer['requires_review'])
        gap = meta['expected_result']=='insufficient_coverage'
        group = 'gap' if gap else 'supported'
        counts[group+'_contexts']+=1
        judges = sorted(answer['items'],key=lambda i:i['item'])
        expected = reference['items']
        for item,ref in zip(judges,expected):
            ref_decision = ref if stage=='stress' else ('covered' if ref['covered'] else 'not_covered')
            counts[group+'_items']+=1
            counts[group+'_uncertain']+=int(item['decision']=='uncertain')
            if item['decision']=='uncertain': continue
            counts[group+'_resolved']+=1
            counts[group+'_agreement']+=int(item['decision']==ref_decision)
            counts[group+'_fp_vs_reference']+=int(item['decision']=='covered' and ref_decision!='covered')
            counts[group+'_fn_vs_reference']+=int(item['decision']=='not_covered' and ref_decision=='covered')
            if item['decision'] != ref_decision:
                details.append({**meta,'type':'item','requirement':inp['requirements'][item['item']-1]['requirement'],
                                'judge':item,'reference':ref})
        score = record['coverage']
        if not gap:
            counts['case_resolved']+=int(score['complete_pass'] is not None)
            ref_pass = bool(expected) and all((v=='covered' if stage=='stress' else v['covered']) for v in expected)
            counts['complete_passes']+=int(score['complete_pass'] is True)
            counts['case_agreement']+=int(score['complete_pass'] is not None and score['complete_pass']==ref_pass)
            counts['false_complete_vs_reference']+=int(score['complete_pass'] is True and not ref_pass)
        else: counts['gap_false_pass']+=int(score['complete_pass'] is True)
        flags = {}
        for label in ['irrelevant','potentially_misleading','jurisdiction_leakage','contradictory']:
            positive = bool(answer[label]); flags[label]=positive
            counts[group+'_'+label+'_positive']+=int(positive)
            # Legacy references have no separate contradiction labels.
            if stage=='validation' and label=='contradictory': continue
            ref_flag = reference['flags'][label] if stage=='stress' else bool(reference[label])
            counts[group+'_'+label+'_disagreement']+=int(positive!=ref_flag)
            counts[group+'_'+label+'_fp_vs_reference']+=int(positive and not ref_flag)
            counts[group+'_'+label+'_fn_vs_reference']+=int(ref_flag and not positive)
            if positive!=ref_flag:
                details.append({**meta,'type':label,'judge':answer[label],
                                'reference':ref_flag if stage=='stress' else reference[label]})
        if stage=='stress':
            match = [i['decision'] for i in judges]==expected and flags==reference['flags'] and answer['requires_review']==reference['requires_review']
            counts['stress_exact_matches']+=int(match)
        rows.append({**meta,'coverage':score,'flags':flags,'decisions':[i['decision'] for i in judges]})
    same = defaultdict(list)
    for row in rows: same[row['input_sha256']].append(row)
    stability = []
    for group in same.values():
        for a,b in combinations(group,2):
            stability.append({'contexts':[a['context_id'],b['context_id']], 'case_id':a['case_id'],
                              'items_equal':a['decisions']==b['decisions'],
                              'flags_different':[l for l in a['flags'] if a['flags'][l]!=b['flags'][l]],
                              'review_equal':a['coverage']['requires_review']==b['coverage']['requires_review']})
    result = {'stage':stage,'planned':len(index),'counts':dict(counts),'tokens':dict(tokens),
              'elapsed_sum_seconds':sum(latencies),'median_seconds':statistics.median(latencies) if latencies else None,
              'billing':'ChatGPT subscription; no API calls or USD estimate',
              'reference_caution':'synthetic developer expectations' if stage=='stress' else runtime.read(CONFIG)['reference_caution'],
              'configuration_selection_authorized':False,'rows':rows,'stability':stability}
    runtime.write(directory/'summary.json',result,replace=True)
    runtime.write(directory/'disagreements.json',details,replace=True)
    print(json.dumps({k:v for k,v in result.items() if k not in {'rows','stability'}},indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run','summarize','verify'])
    parser.add_argument('--stage',choices=['stress','validation'],required=True)
    parser.add_argument('--run-dir',type=Path)
    args = parser.parse_args()
    directory = check_directory(args.run_dir or BASE/args.stage)
    if args.command=='prepare': prepare(args.stage,directory)
    elif args.command=='run': run(directory)
    elif args.command=='summarize': summarize(directory)
    else:
        verify(directory)
        print('Frozen inputs, code, original pilot/history and production verified')


if __name__=='__main__':
    main()
