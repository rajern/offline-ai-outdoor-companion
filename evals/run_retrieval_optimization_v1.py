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
import traceback
import psutil
import numpy as np

import retrieval_optimization_scoring as s
from optimization_embeddings import create, MODELS, LLAMA
from run_retrieval_eval_v1 import TOKENIZER, MODEL, context_for, section_path
from outwise.knowledge.models import KnowledgeItem,RetrievedKnowledgeItem
from outwise.services.orchestrator import _build_grounded_prompt
from outwise.services.semantic_retrieval import allowed_in_jurisdiction
from optimization_resources import Resources,RAM_RESERVE,RSS_LIMIT,input_accounting,validate_vectors

BASE=s.runtime.LOCAL/'diagnostics/retrieval-optimization-v1-2026-10-08'
RUN=BASE/'experiment'
CONFIG=s.ROOT/'evals/retrieval_optimization.v1.json'
CODE=s.CODE+[Path(__file__),s.ROOT/'evals/optimization_embeddings.py',s.ROOT/'evals/optimization_resources.py',s.ROOT/'evals/optimization_report.py',CONFIG,s.PROMPT,s.SCHEMA,s.ADJUDICATION]
EXPERIMENT_LOCK=s.runtime.LOCAL/'retrieval-optimization.lock'


def file_hash(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


class TokenCounter:
    def __init__(self,directory=RUN/'tokenization'):
        self.directory=directory;self.directory.mkdir(parents=True,exist_ok=True)
    def count(self,text):
        key=s.runtime.legacy.text_sha(text);path=self.directory/key
        if (path/'count.json').exists():
            if (path/'input.txt').read_text(encoding='utf-8')!=text:raise ValueError('Token cache input differs')
            record=s.runtime.read(path/'count.json');count=record['tokens']
            if file_hash(path/'stdout.txt')!=record['stdout_sha256']:raise ValueError('Token cache output hash differs')
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
        s.runtime.write(path/'count.json',{'tokens':len(tokens),'command':command,'purpose':'tokenization only',
             'stdout_sha256':file_hash(path/'stdout.txt'),'input_sha256':key})
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
    technical=s.runtime.read(BASE/'technical-preflight/summary.json')
    if not technical['passed']:raise RuntimeError('Technical/resource preflight not passed')
    for name,expected in technical['code_hashes'].items():
        if file_hash(s.ROOT/name)!=expected:raise RuntimeError('Code differs from technical preflight: '+name)
    if RUN.exists():raise FileExistsError('Experiment already frozen; use resume')
    dev=s.load_development()
    if len(dev['cases'])!=25:raise ValueError('Expected 25 unchanged cases')
    if file_hash(TOKENIZER)!='466fa920e21d85bfc8a2977e724d5ef332074aa11839278f3ae3fe2fbf6a11af' or file_hash(MODEL)!='57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8':raise ValueError('Locked grounded tokenizer changed')
    RUN.mkdir(parents=True)
    hashes={str(p.relative_to(s.ROOT)):file_hash(p) for p in s.runtime.legacy.protected_files()+CODE+[s.CERTIFICATES,s.ROOT/'evals/retrieval_development_additions.v2.yaml',s.ROOT/'evals/retrieval_sources.v1.json',s.ROOT/'evals/run_retrieval_eval_v1.py']}
    for path in [TOKENIZER,MODEL,LLAMA]:hashes[str(path)]=file_hash(path)
    for folder in [MODELS/'embeddinggemma-2',MODELS/'Qwen3-Embedding-0.6B-GGUF',s.runtime.LOCAL/'embedding-model']:
        for path in folder.rglob('*'):
            if path.is_file():hashes[str(path.relative_to(s.ROOT))]=file_hash(path)
    # Physically separate snapshots; no holdout is copied or enumerated.
    workspace=RUN/'workspace';workspace.mkdir()
    for path in CODE+[s.ROOT/'evals/retrieval_development.v2.yaml',s.ROOT/'knowledge/local/knowledge.json']:
        (workspace/path.name).write_bytes(path.read_bytes())
    s.runtime.write(RUN/'freeze.json',{'created_at':s.runtime.now(),'identities':hashes,'config':s.runtime.read(CONFIG),
          'judge_identity':s.runtime.read(BASE/'regression/judge-identity.json'),'holdout_accessed':False,
          'resource_limits':{'available_ram_reserve_bytes':RAM_RESERVE,'process_tree_rss_limit_bytes':RSS_LIMIT},
          'technical_preflight_sha256':file_hash(BASE/'technical-preflight/summary.json'),
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
    if (target/'index.json').exists():
        checked_index(name);return
    corpus=s.runtime.read(s.ROOT/'knowledge/local/knowledge.json')['items']
    cases=s.load_development()['cases']
    started=time.perf_counter();model=None
    with Resources() as resources:
      try:
        resources.check();model=create(name,target);resources.check()
        accounting=input_accounting(name,model,corpus,[c['question'] for c in cases]);resources.check()
        if name=='minilm':
            # Keep the existing exact frozen document vectors, not a new baseline.
            if s.runtime.read(s.runtime.LOCAL/'index.json')['item_ids']!=[p['id'] for p in corpus]:raise ValueError('Production parent index order differs')
            documents=np.load(s.runtime.LOCAL/'embeddings.npy',allow_pickle=False)
        else:
            documents=[]
            for offset in range(0,len(corpus),2):
                documents.extend(model.documents(corpus[offset:offset+2]));resources.check()
                if offset%20==0:print(name,'documents',offset+2,'/',len(corpus),flush=True)
            documents=np.asarray(documents,dtype=np.float32)
        queries=model.queries([case['question'] for case in cases]);resources.check()
        validate_vectors(documents,queries,len(corpus),len(cases))
        np.save(target/'documents.npy',documents,allow_pickle=False)
        np.save(target/'queries.npy',queries,allow_pickle=False)
        if name=='minilm':model_size=(s.runtime.LOCAL/'embedding-model/model_optimized.onnx').stat().st_size
        elif name=='gemma2':model_size=sum(p.stat().st_size for p in (MODELS/'embeddinggemma-2').glob('*.safetensors'))
        else:model_size=(MODELS/'Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q4_K_M.gguf').stat().st_size
        s.runtime.write(target/'index.json',{'model_identity':model.lock,'dimensions':int(documents.shape[1]),'model_size_bytes':model_size,
               'document_ids':[p['id'] for p in corpus],'case_ids':[c['id'] for c in cases],
               'documents_sha256':s.runtime.legacy.sha(target/'documents.npy'),'queries_sha256':s.runtime.legacy.sha(target/'queries.npy'),
               'elapsed_seconds':time.perf_counter()-started,'index_size_bytes':(target/'documents.npy').stat().st_size,
               'generation_calls':0,'input_accounting':accounting,'resources':resources.result()})
      finally:
        if model:model.close()
    print(name,'embedding index complete',flush=True)


def retrieve(config):
    verify();target=RUN/'configurations'/config['id'];target.mkdir(parents=True,exist_ok=True)
    if (target/'retrieved-all.json').exists():
        verify_rows(config['id']);return
    if (target/'config.json').exists() and s.runtime.read(target/'config.json')!=config:raise ValueError('Configuration changed on resume')
    s.runtime.write(target/'config.json',config) if not (target/'config.json').exists() else None
    index=RUN/'indices'/config['model'];meta=checked_index(config['model'])
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
             'corpus_hash':file_hash(s.ROOT/'knowledge/local/knowledge.json'),'gold_hash':file_hash(s.ROOT/'evals/retrieval_cases.v1.yaml'),
             'excerpts':[asdict(p) for p in results],'seeds':[asdict(p) for p in seeds],
             'candidates_top16':[{'id':p.item.id,'score':p.score} for p in candidates],
             'context_sha256':s.runtime.legacy.text_sha(context),'context_tokens':ct,'prompt_tokens':pt,
             'prompt_tokenization_key':pk,'context_tokenization_key':ck,'context_budget':2000,'prompt_sha256':s.runtime.legacy.text_sha(prompt),
             'chunk_count':len(results),'section_count':len({(p.item.document_id,p.item.section) for p in results}),
             'packet_count':len(packets),'packets':packets,'trace':trace,
             'budget_excluded_packets':sum(t['status']=='over_budget' for t in trace),
             'ranking_seconds':ranked_seconds,'retrieval_and_packing_seconds':time.perf_counter()-started}
        folder=target/case['id'];folder.mkdir(exist_ok=True)
        if (folder/'retrieved.json').exists():
            saved=s.runtime.read(folder/'retrieved.json')
            if saved['context_sha256']!=row['context_sha256'] or saved['prompt_sha256']!=row['prompt_sha256']:raise ValueError('Resumed packing differs')
            rows.append(saved);continue
        (folder/'context.txt').write_text(context,encoding='utf-8',newline='\n')
        (folder/'prompt-not-executed.txt').write_text(prompt,encoding='utf-8',newline='\n')
        s.runtime.write(folder/'retrieved.json',row)
        rows.append(row)
    s.runtime.write(target/'retrieved-all.json',rows)
    print(config['id'],'25 delivered contexts ready',flush=True)


def score(config_id):
    frozen=verify();target=RUN/'configurations'/config_id
    rows=verify_rows(config_id);cases={c['id']:c for c in s.load_development()['cases']}
    corpus=s.runtime.read(s.ROOT/'knowledge/local/knowledge.json')['items'];certificates=s.rules()
    with s.runtime.JudgeLock():
        s.runtime.recover_active();pre=s.runtime.preflight();ident=s.identity(pre)
        if ident!=frozen['judge_identity']:raise ValueError('Judge identity differs from frozen calibrated identity')
        for row in rows:
            path=target/row['case_id']/'score.json'
            if path.exists():
                saved=s.runtime.read(path)
                if saved['requires_review']:raise RuntimeError('Recorded review blocks advancement; no automatic retry')
                if saved['context_sha256']!=row['context_sha256']:raise ValueError('Saved score context differs')
                continue
            case=cases[row['case_id']];payload=s.judge_input(case,row)
            context='\n\n'.join(b['text'] for b in payload['blocks'])
            if s.runtime.legacy.text_sha(context)!=row['context_sha256']:raise ValueError('Context serialization mismatch')
            request={'configuration':config_id,'case_id':row['case_id'],'cache_key':s.cache_key(payload,ident)}
            with (RUN/'judge-requests.jsonl').open('a',encoding='utf-8',newline='\n') as stream:
                stream.write(json.dumps(request)+'\n');stream.flush()
                __import__('os').fsync(stream.fileno())
            result=s.judge(payload,pre,ident)
            merged=s.merge(case,row,context,corpus,result['answer'],certificates)
            s.runtime.write(path,{**merged,**{k:v for k,v in result.items() if k not in ['answer','record']},'judge_result_sha256':s.digest(result['answer'])})
            print(config_id,row['case_id'],'review='+str(merged['requires_review']),'cache='+str(result['cache_hit']),flush=True)
            if merged['requires_review']:raise RuntimeError('Unresolved source/judge/meaning issue; stop before stage selection')
    scores=[s.runtime.read(target/r['case_id']/'score.json') for r in rows]
    s.runtime.write(target/'summary.json',{'configuration':s.runtime.read(target/'config.json'),'full25':s.aggregate(scores),
         'legacy15':s.aggregate(scores,legacy_only=True),'scores':scores,
         'resources':{'prompt_tokens':[r['prompt_tokens'] for r in rows],'context_tokens':[r['context_tokens'] for r in rows],
                      'passages':[r['chunk_count'] for r in rows],'budget_excluded_packets':sum(r['budget_excluded_packets'] for r in rows),
                      'ranking_seconds':sum(r['ranking_seconds'] for r in rows),'retrieval_and_packing_seconds':sum(r['retrieval_and_packing_seconds'] for r in rows)}},replace=True)


def checked_index(name):
    target=RUN/'indices'/name;meta=s.runtime.read(target/'index.json')
    for filename,key in [('documents.npy','documents_sha256'),('queries.npy','queries_sha256')]:
        if file_hash(target/filename)!=meta[key]:raise ValueError('Embedding index hash mismatch')
    corpus=s.runtime.read(s.runtime.LOCAL/'knowledge.json')['items'];cases=s.load_development()['cases']
    if meta['document_ids']!=[p['id'] for p in corpus] or meta['case_ids']!=[c['id'] for c in cases]:raise ValueError('Index IDs/order mismatch')
    validate_vectors(np.load(target/'documents.npy',allow_pickle=False),np.load(target/'queries.npy',allow_pickle=False),len(corpus),len(cases))
    return meta


def verify_rows(config_id):
    target=RUN/'configurations'/config_id;rows=s.runtime.read(target/'retrieved-all.json')
    cases=s.load_development()['cases'];parents={p['id']:asdict(KnowledgeItem(**p)) for p in s.runtime.read(s.runtime.LOCAL/'knowledge.json')['items']}
    if [r['case_id'] for r in rows]!=[c['id'] for c in cases]:raise ValueError('Incomplete or reordered case results')
    counter=TokenCounter()
    for case,row in zip(cases,rows):
        if row!=s.runtime.read(target/row['case_id']/'retrieved.json'):raise ValueError('Combined/per-case retrieval records differ')
        for excerpt in row['excerpts']:
            if parents.get(excerpt['item']['id'])!=excerpt['item']:raise ValueError('Retrieved source/provenance changed')
            if not allowed_in_jurisdiction(KnowledgeItem(**excerpt['item']),case['jurisdiction']):raise ValueError('Geography guard failed')
        results=[RetrievedKnowledgeItem(KnowledgeItem(**r['item']),r['score']) for r in row['excerpts']]
        context=context_for(results);prompt=_build_grounded_prompt(case['question'],results)
        for filename,text,key in [('context.txt',context,'context_sha256'),('prompt-not-executed.txt',prompt,'prompt_sha256')]:
            if text!=(target/row['case_id']/filename).read_text(encoding='utf-8') or s.runtime.legacy.text_sha(text)!=row[key]:raise ValueError('Delivered serialization changed')
        pt,_=counter.count(prompt);ct,_=counter.count(context)
        if pt!=row['prompt_tokens'] or ct!=row['context_tokens'] or pt>2000:raise ValueError('Saved tokens/budget differ')
    return rows


def worker(command,*,model=None,config_id=None):
    # Only the parent runner owns the experiment lock; heavy models live in
    # short-lived serial workers so imported runtimes release RAM between jobs.
    logs=BASE/'worker-logs';logs.mkdir(exist_ok=True)
    label='-'.join(v for v in [command,model,config_id] if v)
    attempts=list(logs.glob(label+'-*.log'));path=logs/f'{label}-{len(attempts)+1:03}.log'
    argv=[sys.executable,str(Path(__file__)),command,'--worker']
    if model:argv+=['--model',model]
    if config_id:argv+=['--config-id',config_id]
    with path.open('xb') as stream:
        process=subprocess.Popen(argv,stdout=stream,stderr=stream,creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        try:
            while process.poll() is None:time.sleep(1)
        finally:
            if process.poll() is None:
                process.terminate();process.wait(timeout=15)
        if process.returncode:raise RuntimeError(f'{label} failed; inspect {path.relative_to(s.ROOT)}')


def probe_model(name):
    root=BASE/'technical-preflight'/name;root.mkdir(parents=True,exist_ok=True)
    target=root/f'attempt-{len(list(root.glob("attempt-*")))+1:02}';target.mkdir()
    corpus=s.runtime.read(s.runtime.LOCAL/'knowledge.json')['items'];cases=s.load_development()['cases']
    items=[{'title':'Synthetic cold drill','section':'Protection','text':'Remove wet clothing and protect against wind.'},
           {'title':'Synthetic cooking drill','section':'Soup','text':'Stir the soup in a blue bowl.'}]
    questions=['Hvordan beskytter vi en våt person mot vind?','How do we stir soup?']
    settings={'model':name,'threads':4,'ram_reserve':RAM_RESERVE,'rss_limit':RSS_LIMIT,
        'code_hashes':{str(p.relative_to(s.ROOT)):file_hash(p) for p in CODE},
        'long_input_rule':'two longest UTF-8 document inputs and questions, chosen before inference'}
    s.runtime.write(target/'plan.json',settings);model=None;success=False;detail={}
    with Resources() as resources:
      try:
        resources.check();model=create(name,target);resources.check()
        accounting=input_accounting(name,model,corpus,[c['question'] for c in cases]);resources.check()
        docs=model.documents(items);query=model.queries(questions);repeat=model.queries(questions)
        validate_vectors(docs,query,2,2)
        if not np.allclose(query,repeat,atol=1e-5):raise RuntimeError('Original repeatability tolerance failed')
        longest=sorted(corpus,key=lambda p:len((p['title']+(p.get('section') or '')+p['text']).encode('utf-8')),reverse=True)[:2]
        longest_queries=sorted([c['question'] for c in cases],key=lambda q:len(q.encode('utf-8')),reverse=True)[:2]
        long_docs=model.documents(longest);long_queries=model.queries(longest_queries)
        validate_vectors(long_docs,long_queries,2,2);resources.check()
        detail={'model_identity':model.lock,'input_accounting':accounting,'repeatability_pass':True,
            'long_input_ids':[p['id'] for p in longest],'dimensions':int(query.shape[1]),
            'complete_source_embedding_index_created':False,'judge_calls':0}
        success=True
      except Exception as error:
        detail={'error':str(error),'error_type':type(error).__name__}
        (target/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8',newline='\n')
      finally:
        if model:model.close()
    s.runtime.write(target/'result.json',{'model':name,'success':success,'resources':resources.result(),**detail})
    print(name,'technical preflight',success,flush=True)
    if not success:raise RuntimeError('Model technical/resource preflight failed: '+name)


def technical(*,retry=False):
    import run_judge_regression_v3 as regression
    regression.verify()
    target=BASE/'technical-preflight';target.mkdir(exist_ok=True)
    code_hashes={str(p.relative_to(s.ROOT)):file_hash(p) for p in CODE}
    if (target/'summary.json').exists():
        record=s.runtime.read(target/'summary.json')
        if record['passed'] and record['code_hashes']==code_hashes:return
        if not retry:raise RuntimeError('Recorded technical blocker/code change; free RAM then explicitly use --retry-technical before freeze')
        if RUN.exists():raise RuntimeError('Cannot replace technical identities after the experiment freeze')
        history=target/'summary-history';history.mkdir(exist_ok=True)
        saved=history/(s.digest(record)+'.json')
        if not saved.exists():s.runtime.write(saved,record)
    # Check auth/identity and sealed existing results without a new judge call.
    with s.runtime.JudgeLock():
        s.runtime.recover_active();pre=s.runtime.preflight();ident=s.identity(pre)
        if ident!=s.runtime.read(BASE/'regression/judge-identity.json'):raise RuntimeError('Selected judge identity differs from validated V3 identity')
        cached=0
        for entry in s.runtime.read(BASE/'regression/plan.json'):
            key=s.cache_key(entry['input'],ident)
            if not (s.CACHE/key/'results/context-01/record.json').exists():raise RuntimeError('Expected sealed regression cache unavailable')
            result=s.judge(entry['input'],pre,ident)
            if not result['cache_hit'] or result['calls']:raise RuntimeError('Technical cache check attempted fresh inference')
            cached+=1
    results=[];failure=None
    for name in ['minilm','gemma2','qwen3-q4']:
        try:worker('probe',model=name)
        except Exception as error:failure=str(error)
        attempts=sorted((target/name).glob('attempt-*/result.json'))
        if attempts:results.append(s.runtime.read(attempts[-1]))
        if failure:break
    summary={'passed':not failure and len(results)==3 and all(r['success'] for r in results),
        'code_hashes':code_hashes,'results':results,'cached_regression_checks':cached,'actual_judge_calls':0,
        'judge_identity':ident,'resource_limits':{'ram_reserve':RAM_RESERVE,'rss_limit':RSS_LIMIT},
        'failure':failure,'holdout_accessed':False}
    s.runtime.write(target/'summary.json',summary,replace=retry)
    if not summary['passed']:raise RuntimeError('Technical preflight blocked: '+str(failure))


def threshold_values(score_rows):
    values=[candidate['score'] for row in score_rows for candidate in row['candidates_top16']]
    if not values or not np.isfinite(values).all():raise ValueError('Threshold input missing/non-finite')
    return {f'p{p}':float(np.percentile(values,p,method='linear')) for p in [10,30,50,70]}


def choose_stage(config_ids):
    summaries=[s.runtime.read(RUN/'configurations'/cid/'summary.json') for cid in config_ids]
    if any(not r['full25']['eligible_for_selection'] for r in summaries):raise RuntimeError('Unresolved reviews block stage selection')
    candidates=[]
    for candidate in summaries:
        scores={r['case_id']:r for r in candidate['scores']};regressions=[]
        for other in summaries:
            for row in other['scores']:
                current=scores[row['case_id']]
                for i,(a,b) in enumerate(zip(current['decisions'],row['decisions']),1):
                    if b=='covered' and a!='covered':regressions.append({'against':other['configuration']['id'],'case_id':row['case_id'],'item':i,'type':'coverage_loss'})
                for flag in ['potentially_misleading','contradictory','jurisdiction_leakage']:
                    if current['flags'][flag] and not row['flags'][flag]:regressions.append({'against':other['configuration']['id'],'case_id':row['case_id'],'type':flag})
        if not regressions:candidates.append(candidate)
    if not candidates:raise RuntimeError('Material per-case coverage/safety tradeoffs: no configuration dominates; owner decision required')
    def order(record):
        quality=record['full25'];meta=checked_index(record['configuration']['model'])
        return (-quality['complete_cases'],-quality['micro_coverage'],-quality['macro_coverage'],
            quality['flags_supported']['irrelevant'],meta['model_size_bytes']+meta['index_size_bytes'],meta['resources']['peak_process_tree_rss_bytes'],
            meta['resources']['cpu_seconds'],record['configuration']['id'])
    return sorted(candidates,key=order)[0]['configuration']


def stage_choice(stage,config_ids):
    path=RUN/f'choice-{stage}.json'
    chosen=choose_stage(config_ids)
    if path.exists():
        if s.runtime.read(path)['configuration']!=chosen:raise ValueError('Stage choice differs on resume')
    else:s.runtime.write(path,{'configuration':chosen,'compared':config_ids,'provisional':True,
           'rule':'frozen rule; all per-item coverage losses conservatively treated as safety-relevant'})
    return chosen


def configuration(config_id):
    plan=s.runtime.read(RUN/'plan.json')
    known=[c for stage in ['phase_a','phase_b','phase_c'] for c in plan[stage] if c['id']==config_id]
    if len(known)!=1:raise ValueError('Unplanned configuration forbidden')
    if config_id.startswith('A-'):return known[0]
    a=s.runtime.read(RUN/'choice-A.json')['configuration']
    if config_id.startswith('B-'):
        thresholds=s.runtime.read(RUN/'thresholds.json')['values']
        c=known[0];return {**c,'model':a['model'],'threshold':None if c['threshold_name']=='none' else thresholds[c['threshold_name']]}
    b=s.runtime.read(RUN/'choice-B.json')['configuration']
    return {**known[0],'model':b['model'],'k':b['k'],'threshold':b['threshold']}


def run_all(*,retry_technical=False):
    technical(retry=retry_technical)
    if not RUN.exists():freeze()
    if not (RUN/'started.json').exists():
        s.runtime.write(RUN/'started.json',{'started_at':s.runtime.now(),
            'existing_cache_keys':[p.name for p in s.CACHE.iterdir() if p.is_dir()]})
    verify();plan=s.runtime.read(RUN/'plan.json')
    for config in plan['phase_a']:
        worker('index',model=config['model']);worker('retrieve',config_id=config['id']);worker('score',config_id=config['id'])
    a=stage_choice('A',[c['id'] for c in plan['phase_a']])
    rows=verify_rows(a['id']);values=threshold_values(rows)
    threshold_record={'model':a['model'],'values':values,'method':'numpy.percentile linear pooled allowed top16',
        'score_count':sum(len(r['candidates_top16']) for r in rows),'source_sha256':file_hash(RUN/'configurations'/a['id']/'retrieved-all.json')}
    if (RUN/'thresholds.json').exists():
        if s.runtime.read(RUN/'thresholds.json')!=threshold_record:raise ValueError('Threshold freeze changed')
    else:s.runtime.write(RUN/'thresholds.json',threshold_record)
    for config in plan['phase_b']:
        worker('retrieve',config_id=config['id']);worker('score',config_id=config['id'])
    stage_choice('B',[c['id'] for c in plan['phase_b']])
    for config in plan['phase_c']:
        worker('retrieve',config_id=config['id']);worker('score',config_id=config['id'])
    stage_choice('C',[c['id'] for c in plan['phase_c']])
    print('Completed exactly 31 configurations; recommendation only, no production change',flush=True)


if __name__=='__main__':
    s.holdout_guard()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['technical','probe','run','freeze','verify','index','retrieve','score'])
    parser.add_argument('--model',choices=['minilm','gemma2','qwen3-q4'])
    parser.add_argument('--config-id')
    parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--retry-technical',action='store_true',help='Explicit resource-preflight retry before freeze; preserve all previous attempts')
    args=parser.parse_args()
    def dispatch():
        if args.command=='run':run_all(retry_technical=args.retry_technical)
        elif args.command=='technical':technical(retry=args.retry_technical)
        elif args.command=='probe':probe_model(args.model)
        elif args.command=='freeze':freeze()
        elif args.command=='verify':verify()
        elif args.command=='index':build_index(args.model)
        elif args.command=='score':score(args.config_id)
        else:retrieve(configuration(args.config_id))
    if args.worker:dispatch()
    else:
        with s.runtime.JudgeLock(EXPERIMENT_LOCK):
            try:
                dispatch()
            except Exception as error:
                s.runtime.write(BASE/'execution-status.v2.json',{'status':'blocked','error_type':type(error).__name__,'error':str(error),'at':s.runtime.now()},replace=True)
                from optimization_report import export
                export(BASE,RUN,status='blocked',error=str(error))
                raise
            else:
                if args.command in ['run','technical']:
                    status='complete' if args.command=='run' else 'technical_passed'
                    s.runtime.write(BASE/'execution-status.v2.json',{'status':status,'at':s.runtime.now()},replace=True)
                    from optimization_report import export
                    export(BASE,RUN,status=status)
