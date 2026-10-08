"""Blinded delivered-context adapter and immutable Codex cache; no API calls."""
from __future__ import annotations

from copy import deepcopy
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys

import codex_judge_runtime as runtime
from automatic_retrieval_scoring import score_saved, CERTIFICATES
from eval_foundation import load_development

ROOT = runtime.ROOT
PROMPT = ROOT/'evals/retrieval_judge_prompt.v3.md'
SCHEMA = ROOT/'evals/retrieval_judge_output.schema.v2.json'
ADJUDICATION = ROOT/'evals/retrieval_adjudication.v1.json'
CACHE = runtime.LOCAL/'judge-cache-v3'
CODE = [Path(__file__), ROOT/'evals/codex_judge_runtime.py',
        ROOT/'evals/retrieval_judge_pilot.py', ROOT/'evals/automatic_retrieval_scoring.py',
        ROOT/'evals/eval_foundation.py']


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def holdout_guard():
    """Deny Python open/traversal of holdout. No read to discover its contents."""
    forbidden = str((ROOT/'evals/holdout').resolve()).casefold()
    def guard(event, args):
        if event in {'open','os.listdir','os.scandir'} and args and isinstance(args[0],(str,bytes,Path)):
            path = str(Path(os.fsdecode(args[0])).resolve()).casefold()
            if path==forbidden or path.startswith(forbidden+'\\') or path.startswith(forbidden+'/'):
                raise PermissionError('Holdout is excluded from optimization')
    sys.addaudithook(guard)


def rules():
    value = deepcopy(runtime.read(CERTIFICATES))
    for record in runtime.read(ADJUDICATION)['disabled_certificate_routes']:
        routes=value['rules'][record['case_id']][record['item']-1]['alternatives']
        del routes[record['alternative_index_1based']-1]
    return value


def adjudicated_reference(case_id, mode, context_hash, reference):
    result=deepcopy(reference)
    for record in runtime.read(ADJUDICATION)['records']:
        if (record['case_id'],record['configuration'],record['context_sha256']) != (case_id,mode,context_hash):
            continue
        if 'item' in record:
            result['items'][record['item']-1]={'covered':record['decision']=='covered',
                                            'reason':record['basis'],'adjudication_version':'1.0.0'}
        for label,positive in record.get('flags',{}).items():
            result[label]=[{'reason':record['basis'],'adjudication_version':'1.0.0'}] if positive else []
    return result


def judge_input(case, row):
    if row['case_id']!=case['id'] or row['question']!=case['question']:
        raise ValueError('Case/question mismatch')
    payload=runtime.legacy.judge_input(case,row)
    payload.pop('expected_result')
    # Hidden source locators, ranks, config and certificates are never serialized.
    return payload


def identity(pre):
    return {'prompt_sha256':runtime.legacy.sha(PROMPT),'schema_sha256':runtime.legacy.sha(SCHEMA),
            'model':runtime.MODEL,'reasoning_effort':'medium','authentication':'chatgpt_subscription',
            'cli_version':pre['cli_version'],'catalog_model':pre['catalog_model'],
            'actual_server_revision':None,'settings':{'ephemeral':True,'tools':False,
                'timeout_seconds':240,'forced_auth_method':'chatgpt'},
            'code_hashes':{str(p.relative_to(ROOT)):runtime.legacy.sha(p) for p in CODE},
            'validator_versions':{n:version(n) for n in ['jsonschema','PyYAML']}}


def cache_key(payload, ident):
    return digest({'input':payload,'judge_identity':ident})


def prepare_cached_call(payload, ident, cache=CACHE):
    key=cache_key(payload,ident)
    directory=cache/key
    meta={'context_id':'context-01','case_id':payload['case_id'],
          'expected_result':'supported_context',
          'input_sha256':runtime.legacy.text_sha(json.dumps(payload,ensure_ascii=False))}
    # Gap classification is applied after judging, never put in the blinded input.
    if directory.exists():
        frozen=runtime.read(directory/'identity.json')
        if frozen!=ident or runtime.read(directory/'inputs/context-01.json')!=payload:
            raise RuntimeError('Cache identity/content mismatch')
        if runtime.legacy.sha(directory/'prompt.md')!=ident['prompt_sha256'] or runtime.legacy.sha(directory/'schema.json')!=ident['schema_sha256']:
            raise RuntimeError('Cache prompt/schema changed')
        return key,directory,meta
    directory.mkdir(parents=True)
    runtime.write(directory/'identity.json',ident)
    runtime.write(directory/'inputs/context-01.json',payload)
    runtime.write(directory/'index.json',[meta])
    (directory/'prompt.md').write_bytes(PROMPT.read_bytes())
    (directory/'schema.json').write_bytes(SCHEMA.read_bytes())
    return key,directory,meta


def judge(payload, pre, ident, *, cache=CACHE):
    # Caller holds the existing global OS lock through cache lookup and inference.
    if identity(pre)!=ident:
        raise RuntimeError('Judge code/prompt/settings changed; stop before inference')
    key,directory,meta=prepare_cached_call(payload,ident,cache)
    result=directory/'results/context-01'
    hit=(result/'record.json').exists()
    record=runtime.read(result/'record.json') if hit else runtime.execute(directory,meta,pre)
    if not record['success']:
        raise RuntimeError('Recorded failed/invalid judge attempt; no automatic retry or API fallback: '+key)
    answer=runtime.read(result/'answer.json')
    events,malformed,usage=runtime.events_and_usage(result/'stdout.jsonl')
    messages=[e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
    if malformed or not messages or json.loads(messages[-1])!=answer or usage!=record.get('usage') or record['input_sha256']!=meta['input_sha256']:
        raise RuntimeError('Cached answer/log/usage/input identity mismatch')
    seal={name:runtime.legacy.sha(result/name) for name in ['record.json','answer.json','intent.json','stdout.jsonl','stderr.txt','command.json']}
    seal_path=directory/'result-seal.json'
    if seal_path.exists():
        if runtime.read(seal_path)!=seal:raise RuntimeError('Immutable cached result changed')
    else:runtime.write(seal_path,seal)
    errors=runtime.validate(answer,payload,runtime.read(SCHEMA))
    if errors:raise RuntimeError('Cached answer failed current validation')
    return {'cache_key':key,'cache_hit':hit,'answer':answer,'record':record,
            'calls':0 if hit else 1,'usage':{} if hit else record.get('usage'),
            'elapsed_seconds':0 if hit else record.get('elapsed_seconds')}


def merge(case, row, context, corpus, answer, certificates):
    proof=score_saved(case,row,context,corpus,certificates)
    payload=judge_input(case,row)
    errors=runtime.validate(answer,payload,runtime.read(SCHEMA))
    if errors:raise ValueError('Invalid answer: '+str(errors))
    conflicts=[i+1 for i,(p,j) in enumerate(zip(proof['items'],answer['items']))
               if p['decision']=='covered' and j['decision']!='covered']
    review=bool(answer['requires_review'] or conflicts or proof['provenance_issues'])
    coverage=runtime.coverage(answer,payload,case['expected_result'])
    if review:
        coverage.update(coverage=None,complete_pass=None,requires_review=True)
    return {'case_id':case['id'],'configuration':row['configuration'],
            'coverage':coverage,'decisions':[i['decision'] for i in answer['items']],
            'certificate_positive':[i+1 for i,p in enumerate(proof['items']) if p['decision']=='covered'],
            'certificate_judge_disagreement':conflicts,'provenance_issues':proof['provenance_issues'],
            'flags':{label:bool(answer[label]) for label in ['irrelevant','potentially_misleading','contradictory','jurisdiction_leakage']},
            'requires_review':review,'eligible_for_selection':not review,
            'context_sha256':runtime.legacy.text_sha(context)}


def aggregate(rows, *, legacy_only=False):
    rows=[r for r in rows if not legacy_only or int(r['case_id'].split('-')[-1])<=15]
    supported=[r for r in rows if not r['coverage']['gap']]
    gaps=[r for r in rows if r['coverage']['gap']]
    blocked=any(r['requires_review'] for r in rows)
    total=sum(r['coverage']['total'] for r in supported)
    known=sum(r['coverage']['covered'] for r in supported)
    return {'cases':len(rows),'supported_cases':len(supported),'gap_cases':len(gaps),
            'must_have_total':total,'covered':known,'micro_coverage':None if blocked or not total else known/total,
            'macro_coverage':None if blocked or not supported else sum(r['coverage']['coverage'] for r in supported)/len(supported),
            'complete_cases':None if blocked else sum(r['coverage']['complete_pass'] is True for r in supported),
            'review_cases':sum(r['requires_review'] for r in rows),'uncertain_items':sum(d=='uncertain' for r in rows for d in r['decisions']),
            'flags_supported':{label:sum(r['flags'][label] for r in supported) for label in ['irrelevant','potentially_misleading','contradictory','jurisdiction_leakage']},
            'gap_results':[{'case_id':r['case_id'],'coverage':r['coverage'],'flags':r['flags']} for r in gaps],
            'eligible_for_selection':not blocked}
