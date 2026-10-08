"""Bounded CPU embedding diagnostics. No judge, gold, holdout or optimization."""
from __future__ import annotations

import hashlib
import itertools
import json
import threading
import time
from pathlib import Path
import urllib.request

import numpy as np
import psutil
import optimization_embeddings as e

BASE=e.LOCAL/'diagnostics/qwen-stability-v1-2026-10-08-cpu'
KS=(3,5,8,16)
QUERIES=['Hvordan beskytter vi en våt person mot vind?','How do we stir soup?',
         'Hvordan kan vi rense drikkevann når kokeapparatet ikke virker?',
         'Er et klippeoverheng trygt når det tordner?']
# Synthetic isolation fixture, not medical/safety guidance or a gold benchmark.
GROUPS=[('Synthetic cold drill','Protection',[
    'Remove wet clothing and protect against wind.',
    'Protect a wet person against wind with a dry cover.',
    'Place a wind barrier around a cold person.',
    'Replace wet socks with dry socks before leaving the camp.',
    'Dry the clothing and store spare clothes in a waterproof bag.',
    'A sheltered campsite has a wind barrier and dry blankets.']),
    ('Synthetic cooking drill','Soup',[
    'Stir the soup in a blue bowl.',
    'Stir the soup slowly with a wooden spoon.',
    'Mix soup in a blue bowl before serving it.',
    'Put the spoon next to a bowl of warm soup.',
    'Carry a cooking pot and pack a clean bowl.',
    'Store the cooking utensils in a dry bag.']),
    ('Synthetic water drill','Equipment',[
    'Filter water and then disinfect it according to the product instructions.',
    'Read the water treatment tablet instructions before treating the water.',
    'A broken stove cannot boil the collected water.',
    'Carry replacement water treatment tablets and a filter.',
    'Fill the clean water bottle before setting off.',
    'Keep the water bottle separate from dirty cooking equipment.']),
    ('Synthetic thunder drill','Shelter',[
    'No outdoor location is safe during a thunderstorm.',
    'A rock overhang is an outdoor location during a thunderstorm.',
    'Seek an enclosed building when thunder is heard.',
    'Wait inside the building after the storm.',
    'A rain cover protects luggage from ordinary rain.',
    'Store the tent and rain cover before leaving the campsite.'])]
ITEMS=[{'id':f'synthetic-{i:02}-{j:02}','title':title,'section':section,'text':text}
       for i,(title,section,texts) in enumerate(GROUPS) for j,text in enumerate(texts)]
SYNTHETIC_ORIGINAL=ITEMS[0:1]+ITEMS[6:7]
DOC_TEXT=[f'{p["title"]}. {p["section"]}. {p["text"]}' for p in ITEMS]
QUERY_TEXT=[f'Instruct: {e.QWEN_INSTRUCTION}\nQuery: {q}' for q in QUERIES]
Q4_HASH='470901844f8cb73a3e0479ea1dd57ad1baba7072481f1897b2dc4b132b9051a7'
F16_HASH='421a27e58d165478cc7acb984a688c2aa41404968b0203e7cd743ece44c54340'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def post(model,path,body):
    request=urllib.request.Request(model.url+path,data=json.dumps(body).encode('utf-8'),
                                   headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=120) as response:return json.load(response)


def ranking(scores):
    # Stable ID order breaks exact ties; distinguish order from set membership.
    return np.argsort(-np.asarray(scores),axis=1,kind='stable')


def compare_scores(reference,current):
    a=ranking(reference);b=ranking(current)
    rows=[]
    for i,(old,new) in enumerate(zip(a,b)):
        row={'query_index':i,'order_changed':bool(np.any(old!=new)),
             'max_score_delta':float(np.max(np.abs(reference[i]-current[i]))),'top_k':{}}
        for k in KS:
            old_set=set(map(int,old[:k]));new_set=set(map(int,new[:k]))
            threshold=float((reference[i,old[k-1]]+reference[i,old[k]])/2)
            flips=np.flatnonzero((reference[i]>=threshold)!=(current[i]>=threshold))
            row['top_k'][str(k)]={'membership_changed':old_set!=new_set,
                'order_changed':bool(np.any(old[:k]!=new[:k])),
                'entered_indices':sorted(new_set-old_set),'left_indices':sorted(old_set-new_set),
                'reference_boundary_gap':float(reference[i,old[k-1]]-reference[i,old[k]]),
                'diagnostic_threshold':threshold,'threshold_flip_indices':flips.tolist(),
                'flip_distances_from_threshold':[float(abs(reference[i,n]-threshold)) for n in flips]}
        rows.append(row)
    return rows


def summarize(snapshots):
    pairs=[]
    for a,b in itertools.combinations(range(len(snapshots)),2):
        da,qa=snapshots[a];db,qb=snapshots[b]
        all_a=np.concatenate([da,qa]);all_b=np.concatenate([db,qb])
        full=compare_scores(qa@da.T,qb@db.T)
        query_only=compare_scores(qa@snapshots[0][0].T,qb@snapshots[0][0].T)
        pairs.append({'a':a,'b':b,'same_process':a//2==b//2,
            'original_tolerance_all_vectors_pass':bool(np.allclose(all_a,all_b,atol=1e-5)),
            'max_absolute_component_delta':float(np.max(np.abs(all_a-all_b))),
            'minimum_repeat_cosine':float(np.min(np.sum(all_a*all_b,axis=1))),
            'full_regeneration':full,'frozen_document_index':query_only})
    return {'pairs':pairs,'pair_count':len(pairs),'query_pair_count':len(pairs)*len(QUERIES),
        'max_absolute_component_delta':max(p['max_absolute_component_delta'] for p in pairs),
        'minimum_repeat_cosine':min(p['minimum_repeat_cosine'] for p in pairs),
        'all_pairs_original_tolerance_pass':all(p['original_tolerance_all_vectors_pass'] for p in pairs),
        'max_score_delta':max(r['max_score_delta'] for p in pairs for r in p['full_regeneration']),
        'order_changes':sum(r['order_changed'] for p in pairs for r in p['full_regeneration']),
        'top_k_membership_changes':{str(k):sum(r['top_k'][str(k)]['membership_changed']
             for p in pairs for r in p['full_regeneration']) for k in KS},
        'threshold_changes':{str(k):sum(bool(r['top_k'][str(k)]['threshold_flip_indices'])
             for p in pairs for r in p['full_regeneration']) for k in KS}}


def run_condition(name,threads,model_path):
    target=BASE/name;target.mkdir()
    started=time.perf_counter();snapshots=[];original=[];token_runs=[];raw_norms=[]
    stop=threading.Event();samples=[];cpu={};calls=0
    parent=psutil.Process();initial_cpu=parent.cpu_times()
    def monitor():
        while not stop.is_set():
            rss=0
            for process in [parent]+parent.children(recursive=True):
                try:
                    rss+=process.memory_info().rss
                    t=process.cpu_times();cpu[process.pid]=t.user+t.system
                except (psutil.NoSuchProcess,psutil.AccessDenied):pass
            samples.append((rss,psutil.virtual_memory().available));stop.wait(.1)
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    try:
        for process_index in range(2):
            logs=target/f'process-{process_index}';logs.mkdir()
            model=e.Qwen(logs,threads=threads,cpu_only=True,model_path=model_path)
            try:
                # Exactly the old input sequence and old numerical tolerance.
                docs=model.documents(SYNTHETIC_ORIGINAL)
                q=model.queries(QUERIES[:2]);repeat=model.queries(QUERIES[:2]);calls+=6
                np.savez(logs/'original-test.npz',documents=docs,query=q,repeat=repeat)
                original.append({'passed':docs.shape[1]==q.shape[1] and bool(np.allclose(q,repeat,atol=1e-5)),
                    'max_absolute_difference':float(np.max(np.abs(q-repeat)))})
                for repeat_index in range(2):
                    vectors=[];token_records=[];norms=[]
                    for text in DOC_TEXT+QUERY_TEXT:
                        tokens=post(model,'/tokenize',{'content':text,'add_special':True,'parse_special':True})['tokens']
                        post(model,'/slots/0?action=erase',{})
                        response=post(model,'/v1/embeddings',{'input':text,'encoding_format':'float','cache_prompt':False})
                        calls+=1;vector=np.asarray(response['data'][0]['embedding'],dtype=np.float32)
                        norms.append(float(np.linalg.norm(vector)))
                        token_records.append({'tokens':tokens,'reported_usage':response.get('usage')})
                        vectors.append(vector)
                    values=e.normalize(vectors)
                    if values.shape!=(28,1024):raise ValueError('Unexpected embedding dimensions')
                    snapshot=(values[:24],values[24:]);snapshots.append(snapshot)
                    np.savez(logs/f'snapshot-{repeat_index}.npz',raw=vectors,normalized=values,
                             scores=snapshot[1]@snapshot[0].T)
                    write(logs/f'tokens-{repeat_index}.json',token_records)
                    token_runs.append(token_records);raw_norms.extend(norms)
                    print(f'{name}: process {process_index+1}/2, snapshot {repeat_index+1}/2 saved',flush=True)
            finally:model.close()
    finally:stop.set();thread.join(timeout=2)
    result={'condition':name,'threads':threads,'strict_cpu':True,'model_sha256':sha(model_path),
        'snapshot_count':4,'embedding_requests':calls,'original_test_per_process':original,
        'identical_token_ids_all_runs':all([v['tokens'] for v in run]==[v['tokens'] for v in token_runs[0]] for run in token_runs),
        'token_counts':list(map(lambda t:len(t['tokens']),token_runs[0])),
        'reported_token_counts_match':all(t['reported_usage']['prompt_tokens']==len(t['tokens']) for run in token_runs for t in run),
        'raw_l2_norm_range':[min(raw_norms),max(raw_norms)],'elapsed_seconds':time.perf_counter()-started,
        'peak_simultaneous_process_tree_rss_bytes':max(a for a,b in samples),
        'minimum_machine_available_ram_bytes':min(b for a,b in samples),
        'cpu_seconds':sum(cpu.values())-initial_cpu.user-initial_cpu.system,**summarize(snapshots)}
    write(target/'result.json',result)
    return result,snapshots


def main():
    # Refuse accidental holdout access even if a dependency later introduces it.
    import sys
    protected=e.ROOT/'evals/holdout'
    def guard(event,args):
        if event in ('open','os.listdir','os.scandir') and args and isinstance(args[0],(str,bytes,Path)):
            candidate=Path(args[0].decode() if isinstance(args[0],bytes) else args[0]).resolve()
            if candidate==protected or protected in candidate.parents:raise PermissionError('Holdout excluded')
    sys.addaudithook(guard)
    BASE.mkdir(parents=True,exist_ok=False)
    folder=e.MODELS/'Qwen3-Embedding-0.6B-GGUF'
    q4=folder/'Qwen3-Embedding-0.6B-Q4_K_M.gguf';f16=folder/'Qwen3-Embedding-0.6B-f16.gguf'
    if sha(q4)!=Q4_HASH or sha(f16)!=F16_HASH:raise ValueError('Model identity mismatch')
    plan={'baseline_commit':'7854769','dataset':'24 synthetic passages / four fixed queries',
        'items':ITEMS,'queries':QUERIES,'serialized_document_inputs':DOC_TEXT,'serialized_query_inputs':QUERY_TEXT,
        'conditions_maximum':['q4-strict-cpu-4threads','q4-strict-cpu-1thread','f16-strict-cpu-1thread'],
        'condition_rule':'Stop after first Q4 condition passing original checks AND all snapshot pairs; F16 only if both Q4 fail.',
        'repetitions':'two snapshots in each of two fresh processes; six pairwise comparisons per condition',
        'top_k':KS,'original_check':'np.allclose(query, repeated, atol=1e-5); default rtol=1e-5 unchanged',
        'threshold_rule':'Per pair, midpoint of reference kth and (k+1)th scores; diagnostic only, not optimization thresholds.',
        'hypotheses':['Explicit CPU device/operation/KV isolation (ngl=0 alone allows operation offload).',
                      'Single thread eliminates reduction/order races.','F16 distinguishes Q4-specific failure from broader runtime.'],
        'maximum_embedding_requests':372,'judge_calls':0,'generation_calls':0,'optimization_configurations':0,
        'code_hashes':{p.name:sha(p) for p in [Path(__file__),Path(e.__file__)]},
        'models':{'q4':Q4_HASH,'f16':F16_HASH},'server_sha256':sha(e.LLAMA)}
    write(BASE/'plan.json',plan)
    conditions=[];first_query=None
    for name,threads,path in [('q4-strict-cpu-4threads',4,q4),('q4-strict-cpu-1thread',1,q4),('f16-strict-cpu-1thread',1,f16)]:
        result,snapshots=run_condition(name,threads,path)
        if first_query is None:first_query=snapshots[0][1]
        result['vs_first_condition_query_max_delta']=float(np.max(np.abs(first_query-snapshots[0][1])))
        conditions.append(result);write(BASE/'summary.json',{'plan_sha256':sha(BASE/'plan.json'),'conditions':conditions})
        if path==q4 and result['all_pairs_original_tolerance_pass'] and all(r['passed'] for r in result['original_test_per_process']):break
    print(json.dumps({r['condition']:{k:r[k] for k in ['all_pairs_original_tolerance_pass','max_absolute_component_delta',
        'minimum_repeat_cosine','max_score_delta','order_changes','top_k_membership_changes','elapsed_seconds']} for r in conditions},indent=2),flush=True)


if __name__=='__main__':main()
