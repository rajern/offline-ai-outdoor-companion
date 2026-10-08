"""Bounded calibration of owner-approved corrections; no new retrieval."""
import argparse
from collections import Counter
from pathlib import Path
import json
import retrieval_optimization_scoring as s
from codex_judge_runtime import legacy
import retrieval_judge_validation as v2

BASE=s.runtime.LOCAL/'diagnostics/retrieval-optimization-v1-2026-10-08'
RUN=BASE/'regression'


def prepare():
    if RUN.exists():raise FileExistsError('Never overwrite regression plan')
    dev={c['id']:c for c in s.load_development()['cases']}
    folders=s.runtime.read(legacy.CONFIG)['historical_runs']
    entries=[]
    hashes={}
    for mode,folder in folders.items():
        historical=legacy.ROOT/'knowledge/local/diagnostics'/folder
        rows_path=historical/'retrieved-all.json'
        refs_path=historical/'scoring.json'
        hashes[str(rows_path.relative_to(s.ROOT))]=legacy.sha(rows_path)
        hashes[str(refs_path.relative_to(s.ROOT))]=legacy.sha(refs_path)
        refs=s.runtime.read(refs_path)
        for row in s.runtime.read(rows_path):
            if row['configuration']!=mode or row['case_id'] not in ['case-05','case-08','case-09']:continue
            if row['case_id']=='case-05' and mode not in ['A','B']:continue
            case=dev[row['case_id']]
            payload=s.judge_input(case,row)
            context='\n\n'.join(b['text'] for b in payload['blocks'])
            if legacy.text_sha(context)!=row['context_sha256']:raise ValueError('Historical delivered context changed')
            ref=s.adjudicated_reference(case['id'],mode,row['context_sha256'],refs[mode][case['id']])
            entries.append({'input':payload,'expected':{'items':['covered' if i['covered'] else 'not_covered' for i in ref['items']],
                            'flags':{label:bool(ref[label]) for label in ['irrelevant','potentially_misleading','jurisdiction_leakage']},
                            'requires_review':False},'case_id':case['id'],'configuration':mode,'row':row,
                            'expected_result':case['expected_result']})
    stress=s.runtime.read(s.ROOT/'evals/retrieval_judge_stress.v2.json')
    selected=['stress-02','stress-03','stress-04','stress-05','stress-06','stress-07','stress-09','stress-10','stress-12','stress-14']
    for case in stress['cases']:
        if case['test_id'] in selected:
            entries.append({'input':case['input'],'expected':case['expected'],'case_id':case['input']['case_id'],
                            'test_id':case['test_id'],'expected_result':case['expected_result']})
    assert len(entries)==22
    RUN.mkdir(parents=True)
    s.runtime.write(RUN/'plan.json',entries)
    paths=s.CODE+[s.PROMPT,s.SCHEMA,s.ADJUDICATION,Path(__file__),s.ROOT/'evals/retrieval_judge_stress.v2.json']
    for path in paths:
        target=RUN/'artifacts'/path.name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(path.read_bytes())
    for path in legacy.protected_files():hashes[str(path.relative_to(s.ROOT))]=legacy.sha(path)
    # Preserve all original model outputs and v2 inputs/references/results.
    for old in [legacy.DEFAULT_RUN,v2.BASE/'stress',v2.BASE/'validation']:
        for folder in ['results','inputs','references']:
            for path in (old/folder).rglob('*'):
                if path.is_file():hashes[str(path.relative_to(s.ROOT))]=legacy.sha(path)
    s.runtime.write(RUN/'freeze.json',{'code':{str(p.relative_to(s.ROOT)):legacy.sha(p) for p in paths},
        'protected':hashes,'plan_sha256':legacy.sha(RUN/'plan.json'),'calibration_only':True,
        'holdout_accessed':False,'planned_contexts':22,'unique_inputs':len({s.digest(e['input']) for e in entries})})
    print('Prepared',len(entries),'targeted regression rows; distinct input count',len({s.digest(e['input']) for e in entries}))


def verify():
    frozen=s.runtime.read(RUN/'freeze.json')
    for field in ['code','protected']:
        for name,expected in frozen[field].items():
            if legacy.sha(s.ROOT/name)!=expected:raise ValueError('Frozen identity changed: '+name)
    if legacy.sha(RUN/'plan.json')!=frozen['plan_sha256']:raise ValueError('Regression plan changed')


def run():
    verify()
    with s.runtime.JudgeLock():
        s.runtime.recover_active()
        pre=s.runtime.preflight()
        ident=s.identity(pre)
        if (RUN/'judge-identity.json').exists():
            if s.runtime.read(RUN/'judge-identity.json')!=ident:raise ValueError('Judge identity changed')
        else:s.runtime.write(RUN/'judge-identity.json',ident)
        for number,entry in enumerate(s.runtime.read(RUN/'plan.json'),1):
            result_path=RUN/'results'/f'{number:02}.json'
            if result_path.exists():continue
            result=s.judge(entry['input'],pre,ident)
            answer=result.pop('answer')
            record=result.pop('record')
            flags={label:bool(answer[label]) for label in entry['expected']['flags']}
            decisions=[i['decision'] for i in answer['items']]
            match=decisions==entry['expected']['items'] and flags==entry['expected']['flags'] and answer['requires_review']==entry['expected']['requires_review']
            proof_conflicts=[]
            if 'row' in entry:
                dev={c['id']:c for c in s.load_development()['cases']}
                corpus=s.runtime.read(s.ROOT/'knowledge/local/knowledge.json')['items']
                merged=s.merge(dev[entry['case_id']],entry['row'],'\n\n'.join(b['text'] for b in entry['input']['blocks']),corpus,answer,s.rules())
                proof_conflicts=merged['certificate_judge_disagreement']
                match=match and merged['eligible_for_selection']
            s.runtime.write(result_path,{**result,'case_id':entry['case_id'],'configuration':entry.get('configuration'),
                         'test_id':entry.get('test_id'),'decisions':decisions,'flags':flags,
                         'requires_review':answer['requires_review'],'match':match,'proof_conflicts':proof_conflicts})
            print(f'{number:02} {entry["case_id"]}: match={match}, cache_hit={result["cache_hit"]}',flush=True)
            if not match:raise RuntimeError('Regression disagreement; inspect before any optimization')
    verify()
    summarize()


def summarize():
    results=[s.runtime.read(p) for p in sorted((RUN/'results').glob('*.json'))]
    tokens=Counter()
    for result in results:
        for key,value in (result.get('usage') or {}).items():tokens[key]+=value
    summary={'planned_contexts':22,'completed':len(results),'matches':sum(r['match'] for r in results),
             'actual_judge_calls':sum(r['calls'] for r in results),'cache_hits':sum(r['cache_hit'] for r in results),
             'usage':dict(tokens),'elapsed_seconds':sum(r['elapsed_seconds'] or 0 for r in results),
             'calibration_only':True,'api_calls':0,'holdout_accessed':False,
             'passed':len(results)==22 and all(r['match'] for r in results),'results':results}
    s.runtime.write(RUN/'summary.json',summary,replace=True)
    print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2))


if __name__=='__main__':
    s.holdout_guard()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run','summarize','verify'])
    args=parser.parse_args()
    globals()[args.command]()
