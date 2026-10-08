"""31-stage retrieval-only experiment with frozen delivered-context judging."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from importlib.metadata import version
import json
import hashlib
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

import retrieval_optimization_scoring as s
from optimization_embeddings import create, MODELS, LLAMA
from run_retrieval_eval_v1 import TOKENIZER, MODEL, context_for, section_path
from outwise.knowledge.models import KnowledgeItem,RetrievedKnowledgeItem
from outwise.services.orchestrator import _build_grounded_prompt
from outwise.services.semantic_retrieval import allowed_in_jurisdiction

BASE=s.runtime.LOCAL/'diagnostics/retrieval-optimization-v1-2026-10-08'
RUN=BASE/'experiment'
CONFIG=s.ROOT/'evals/retrieval_optimization.v1.json'
CODE=s.CODE+[Path(__file__),s.ROOT/'evals/optimization_embeddings.py',CONFIG,s.PROMPT,s.SCHEMA,s.ADJUDICATION]


def file_hash(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


class TokenCounter:
    def __init__(self,directory=RUN/'tokenization'):
        self.directory=directory;self.directory.mkdir(parents=True,exist_ok=True)
    def count(self,text):
        key=s.runtime.legacy.text_sha(text);path=self.directory/key
        if (path/'count.json').exists():
            if (path/'input.txt').read_text(encoding='utf-8')!=text:raise ValueError('Token cache input differs')
            count=s.runtime.read(path/'count.json')['tokens']
            tokens=json.loads((path/'stdout.txt').read_text(encoding='utf-8'))
            if not isinstance(tokens,list) or not all(isinstance(t,int) for t in tokens) or len(tokens)!=count:raise ValueError('Recorded token count differs from tokenizer output')
            return count,key
        path.mkdir(exist_ok=True)
        command=[str(TOKENIZER),'-m',str(MODEL),'--stdin','--ids','--offline']
        result=subprocess.run(command,input=text,capture_output=True,text=True,encoding='utf-8',timeout=60)
        (path/'input.txt').write_text(text,encoding='utf-8',newline='\n')
        (path/'stdout.txt').write_text(result.stdout,encoding='utf-8')
        (path/'stderr.txt').write_text(result.stderr,encoding='utf-8')
        if result.returncode:raise RuntimeError('Locked tokenizer failed')
        tokens=json.loads(result.stdout)
        if not isinstance(tokens,list) or not all(isinstance(t,int) for t in tokens):raise ValueError('Tokenizer output invalid')
        s.runtime.write(path/'count.json',{'tokens':len(tokens),'command':command,'purpose':'tokenization only'})
        return len(tokens),key


def narrow_members(seed,parents,jurisdiction):
    eligible=[p for p in parents if p.document_id==seed.document_id and allowed_in_jurisdiction(p,jurisdiction)]
    heading=section_path(seed)
    descendants=[p for p in eligible if len(section_path(p))>len(heading) and section_path(p)[:len(heading)]==heading]
    anchor=heading
    if not descendants and len(heading)>1:
        ancestor=heading[:-1]
        branches={section_path(p)[len(ancestor)] for p in eligible if len(section_path(p))>len(ancestor) and section_path(p)[:len(ancestor)]==ancestor}
        if len(ancestor)>1 or len(branches)<=1:anchor=ancestor
    branches={section_path(p)[len(anchor)] for p in eligible if len(section_path(p))>len(anchor) and section_path(p)[:len(anchor)]==anchor}
    exact_only=len(anchor)==1 and len(branches)>1
    members=[p for p in eligible if section_path(p)==anchor or not exact_only and len(section_path(p))>len(anchor) and section_path(p)[:len(anchor)]==anchor]
    if seed.id not in {p.id for p in members}:raise ValueError('Expansion lost seed')
    return (seed.document_id,anchor,exact_only),members


def pack(case,seeds,parents,packing,counter,budget=2000):
    results=[];trace=[];packets=[];seen=set();groups=set();texts=set()
    positions={p.id:i for i,p in enumerate(parents)}
    for rank,seed in enumerate(seeds,1):
        if seed.item.id in seen:continue
        members=[seed.item];group=(seed.item.document_id,(seed.item.id,),True)
        if packing in ['P1','P3']:
            group,expanded=narrow_members(seed.item,parents,case['jurisdiction'])
            consecutive=max(positions[p.id] for p in expanded)-min(positions[p.id] for p in expanded)+1==len(expanded)
            same_heading=len({section_path(p) for p in expanded})==1
            if packing=='P1' or len(expanded)<=3 and consecutive and (len(group[1])>1 or same_heading):members=expanded
            else:group=(seed.item.document_id,(seed.item.id,),True)
        if group in groups:continue
        if packing=='P3' and s.runtime.legacy.text_sha(' '.join(seed.item.text.split())) in texts:continue
        groups.add(group)
        added=[RetrievedKnowledgeItem(p,seed.score) for p in members if p.id not in seen]
        prompt_tokens,key=counter.count(_build_grounded_prompt(case['question'],results+added))
        entry={'seed_rank':rank,'seed_id':seed.item.id,'score':seed.score,'would_add':[p.item.id for p in added],
               'prompt_tokens':prompt_tokens,'tokenization_key':key}
        if prompt_tokens>budget:
            trace.append({**entry,'status':'over_budget'});continue
        results+=added;seen.update(p.item.id for p in added)
        texts.update(s.runtime.legacy.text_sha(' '.join(p.item.text.split())) for p in added)
        trace.append({**entry,'status':'accepted'});packets.append(entry)
    return results,packets,trace


def freeze():
    regression=s.runtime.read(BASE/'regression/summary.json')
    if not regression['passed']:raise RuntimeError('Regression incomplete/failed')
    for name in ['minilm','gemma2','qwen3-q4']:
        attempts=sorted((BASE/'model-preflight'/name).glob('attempt-*/result.json'))
        if not attempts or not s.runtime.read(attempts[-1])['success']:raise RuntimeError('Local model preflight not passed: '+name)
    if RUN.exists():raise FileExistsError('Experiment already frozen; use resume')
    dev=s.load_development()
    if len(dev['cases'])!=25:raise ValueError('Expected 25 unchanged cases')
    if file_hash(TOKENIZER)!='466fa920e21d85bfc8a2977e724d5ef332074aa11839278f3ae3fe2fbf6a11af' or file_hash(MODEL)!='57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8':raise ValueError('Locked grounded tokenizer changed')
    RUN.mkdir(parents=True)
    hashes={str(p.relative_to(s.ROOT)):file_hash(p) for p in s.runtime.legacy.protected_files()+CODE+[s.CERTIFICATES,s.ROOT/'evals/retrieval_development_additions.v2.yaml']}
    for path in [TOKENIZER,MODEL,LLAMA]:hashes[str(path)]=file_hash(path)
    for folder in [MODELS/'embeddinggemma-2',MODELS/'Qwen3-Embedding-0.6B-GGUF']:
        for path in folder.rglob('*'):
            if path.is_file():hashes[str(path.relative_to(s.ROOT))]=file_hash(path)
    # Physically separate snapshots; no holdout is copied or enumerated.
    workspace=RUN/'workspace';workspace.mkdir()
    for path in CODE+[s.ROOT/'evals/retrieval_development.v2.yaml',s.ROOT/'knowledge/local/knowledge.json']:
        (workspace/path.name).write_bytes(path.read_bytes())
    s.runtime.write(RUN/'freeze.json',{'created_at':s.runtime.now(),'identities':hashes,'config':s.runtime.read(CONFIG),
          'judge_identity':s.runtime.read(BASE/'regression/judge-identity.json'),'holdout_accessed':False,
          'versions':{name:version(name) for name in ['numpy','fastembed','onnxruntime','torch','transformers','sentence-transformers']}})
    s.runtime.write(RUN/'plan.json',{'phase_a':[{'id':'A-'+m,'model':m,'k':8,'threshold':None,'packing':'P2'} for m in ['minilm','gemma2','qwen3-q4']],
          'phase_b':[{'id':f'B-k{k}-{t}','k':k,'threshold_name':t,'packing':'P2'} for k in [3,5,8,12,16] for t in ['none','p10','p30','p50','p70']],
          'phase_c':[{'id':'C-'+p,'packing':p} for p in ['P1','P2','P3']]})
    print('Frozen 31 configuration plan, 25 cases and unchanged production assets')


def verify():
    frozen=s.runtime.read(RUN/'freeze.json')
    for name,value in frozen['identities'].items():
        path=Path(name) if Path(name).is_absolute() else s.ROOT/name
        if file_hash(path)!=value:raise ValueError('Frozen experiment identity changed: '+name)
    return frozen


def build_index(name):
    verify();target=RUN/'indices'/name;target.mkdir(parents=True,exist_ok=True)
    if (target/'index.json').exists():return
    corpus=s.runtime.read(s.ROOT/'knowledge/local/knowledge.json')['items']
    cases=s.load_development()['cases']
    started=time.perf_counter();model=create(name,target)
    try:
        if name=='minilm':
            # Keep the existing exact frozen document vectors, not a new baseline.
            if s.runtime.read(s.runtime.LOCAL/'index.json')['item_ids']!=[p['id'] for p in corpus]:raise ValueError('Production parent index order differs')
            documents=np.load(s.runtime.LOCAL/'embeddings.npy',allow_pickle=False)
        else:documents=model.documents(corpus)
        queries=model.queries([case['question'] for case in cases])
        np.save(target/'documents.npy',documents,allow_pickle=False)
        np.save(target/'queries.npy',queries,allow_pickle=False)
        s.runtime.write(target/'index.json',{'model_identity':model.lock,'dimensions':int(documents.shape[1]),
               'document_ids':[p['id'] for p in corpus],'case_ids':[c['id'] for c in cases],
               'documents_sha256':s.runtime.legacy.sha(target/'documents.npy'),'queries_sha256':s.runtime.legacy.sha(target/'queries.npy'),
               'elapsed_seconds':time.perf_counter()-started,'index_size_bytes':(target/'documents.npy').stat().st_size,
               'generation_calls':0})
    finally:model.close()
    print(name,'embedding index complete',flush=True)


def retrieve(config):
    verify();target=RUN/'configurations'/config['id'];target.mkdir(parents=True,exist_ok=True)
    if (target/'retrieved-all.json').exists():return
    s.runtime.write(target/'config.json',config) if not (target/'config.json').exists() else None
    index=RUN/'indices'/config['model'];meta=s.runtime.read(index/'index.json')
    for name,key in [('documents.npy','documents_sha256'),('queries.npy','queries_sha256')]:
        if s.runtime.legacy.sha(index/name)!=meta[key]:raise ValueError('Embedding index changed')
    vectors=np.load(index/'documents.npy',allow_pickle=False);queries=np.load(index/'queries.npy',allow_pickle=False)
    parents=[KnowledgeItem(**p) for p in s.runtime.read(s.ROOT/'knowledge/local/knowledge.json')['items']]
    cases=s.load_development()['cases'];counter=TokenCounter();rows=[]
    for number,case in enumerate(cases):
        started=time.perf_counter();scores=vectors@queries[number]
        order=sorted([i for i,p in enumerate(parents) if allowed_in_jurisdiction(p,case['jurisdiction'])],key=lambda i:(-float(scores[i]),parents[i].id))
        candidates=[RetrievedKnowledgeItem(parents[i],float(scores[i])) for i in order[:16]]
        seeds=[p for p in candidates[:config['k']] if config['threshold'] is None or p.score>=config['threshold']]
        ranked_seconds=time.perf_counter()-started
        results,packets,trace=pack(case,seeds,parents,config['packing'],counter)
        context=context_for(results);prompt=_build_grounded_prompt(case['question'],results)
        pt,pk=counter.count(prompt);ct,ck=counter.count(context)
        if pt>2000:raise ValueError('Grounded prompt budget exceeded')
        row={'configuration':config['id'],'case_id':case['id'],'question':case['question'],
             'excerpts':[asdict(p) for p in results],'seeds':[asdict(p) for p in seeds],
             'candidates_top16':[{'id':p.item.id,'score':p.score} for p in candidates],
             'context_sha256':s.runtime.legacy.text_sha(context),'context_tokens':ct,'prompt_tokens':pt,
             'prompt_tokenization_key':pk,'context_tokenization_key':ck,'context_budget':2000,
             'chunk_count':len(results),'section_count':len({(p.item.document_id,p.item.section) for p in results}),
             'packet_count':len(packets),'packets':packets,'trace':trace,
             'budget_excluded_packets':sum(t['status']=='over_budget' for t in trace),
             'ranking_seconds':ranked_seconds,'retrieval_and_packing_seconds':time.perf_counter()-started}
        folder=target/case['id'];folder.mkdir(exist_ok=True)
        (folder/'context.txt').write_text(context,encoding='utf-8',newline='\n')
        (folder/'prompt-not-executed.txt').write_text(prompt,encoding='utf-8',newline='\n')
        s.runtime.write(folder/'retrieved.json',row)
        rows.append(row)
    s.runtime.write(target/'retrieved-all.json',rows)
    print(config['id'],'25 delivered contexts ready',flush=True)


def score(config_id):
    frozen=verify();target=RUN/'configurations'/config_id
    rows=s.runtime.read(target/'retrieved-all.json');cases={c['id']:c for c in s.load_development()['cases']}
    corpus=s.runtime.read(s.ROOT/'knowledge/local/knowledge.json')['items'];certificates=s.rules()
    with s.runtime.JudgeLock():
        s.runtime.recover_active();pre=s.runtime.preflight();ident=s.identity(pre)
        if ident!=frozen['judge_identity']:raise ValueError('Judge identity differs from frozen calibrated identity')
        for row in rows:
            path=target/row['case_id']/'score.json'
            if path.exists():continue
            case=cases[row['case_id']];payload=s.judge_input(case,row)
            context='\n\n'.join(b['text'] for b in payload['blocks'])
            if s.runtime.legacy.text_sha(context)!=row['context_sha256']:raise ValueError('Context serialization mismatch')
            result=s.judge(payload,pre,ident)
            merged=s.merge(case,row,context,corpus,result['answer'],certificates)
            s.runtime.write(path,{**merged,**{k:v for k,v in result.items() if k not in ['answer','record']}})
            print(config_id,row['case_id'],'review='+str(merged['requires_review']),'cache='+str(result['cache_hit']),flush=True)
            if merged['requires_review']:raise RuntimeError('Unresolved source/judge/meaning issue; stop before stage selection')
    scores=[s.runtime.read(target/r['case_id']/'score.json') for r in rows]
    s.runtime.write(target/'summary.json',{'configuration':s.runtime.read(target/'config.json'),'full25':s.aggregate(scores),
         'legacy15':s.aggregate(scores,legacy_only=True),'scores':scores,
         'resources':{'prompt_tokens':[r['prompt_tokens'] for r in rows],'context_tokens':[r['context_tokens'] for r in rows],
                      'passages':[r['chunk_count'] for r in rows],'budget_excluded_packets':sum(r['budget_excluded_packets'] for r in rows),
                      'ranking_seconds':sum(r['ranking_seconds'] for r in rows),'retrieval_and_packing_seconds':sum(r['retrieval_and_packing_seconds'] for r in rows)}})


if __name__=='__main__':
    s.holdout_guard()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['freeze','verify','index','retrieve','score'])
    parser.add_argument('--model',choices=['minilm','gemma2','qwen3-q4'])
    parser.add_argument('--config-id')
    args=parser.parse_args()
    if args.command=='freeze':freeze()
    elif args.command=='verify':verify()
    elif args.command=='index':build_index(args.model)
    elif args.command=='score':score(args.config_id)
    else:
        config=next(c for c in s.runtime.read(RUN/'plan.json')['phase_a'] if c['id']==args.config_id)
        retrieve(config)
