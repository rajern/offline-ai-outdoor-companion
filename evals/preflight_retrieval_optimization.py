"""Small synthetic local runtime/resource probe, not development retrieval."""
import argparse
from importlib.metadata import version
import json
import threading
import time
import traceback
from pathlib import Path
import psutil
import numpy as np
import optimization_embeddings as e
import retrieval_optimization_scoring as s

BASE=s.runtime.LOCAL/'diagnostics/retrieval-optimization-v1-2026-10-08'


def probe(name,attempt):
    target=BASE/'model-preflight'/name/f'attempt-{attempt:02}'
    target.mkdir(parents=True,exist_ok=True)
    if (target/'result.json').exists():raise FileExistsError('Never overwrite a recorded probe')
    started=time.perf_counter()
    s.runtime.write(target/'probe-settings.json',{'threads':4,'synthetic_inputs_only':True,
             'float32_repeat_tolerance':1e-5,
             'code_hashes':{str(p.relative_to(s.ROOT)):s.runtime.legacy.sha(p) for p in [Path(__file__),Path(e.__file__)]}})
    stop=threading.Event();samples=[];cpu={}
    def monitor():
        parent=psutil.Process()
        while not stop.is_set():
            rss=0
            for process in [parent]+parent.children(recursive=True):
                try:
                    memory=process.memory_info()
                    rss+=memory.rss
                    values=process.cpu_times();cpu[process.pid]=values.user+values.system
                except (psutil.NoSuchProcess,psutil.AccessDenied):pass
            samples.append((rss,psutil.virtual_memory().available));stop.wait(.1)
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    model=None;success=False;detail={}
    try:
        model=e.create(name,target)
        items=[{'title':'Synthetic cold drill','section':'Protection','text':'Remove wet clothing and protect against wind.'},
               {'title':'Synthetic cooking drill','section':'Soup','text':'Stir the soup in a blue bowl.'}]
        queries=['Hvordan beskytter vi en våt person mot vind?','How do we stir soup?']
        documents=model.documents(items)
        vectors=model.queries(queries)
        repeated=model.queries(queries)
        if documents.shape[1]!=vectors.shape[1] or not np.allclose(vectors,repeated,atol=1e-5):raise ValueError('Embedding dimensions or repeatability inconsistent')
        for value in [documents,vectors]:
            if not np.isfinite(value).all() or not np.allclose(np.linalg.norm(value,axis=1),1,atol=1e-4):raise ValueError('Embedding normalization/finiteness error')
        detail={'model_identity':model.lock,'dimensions':int(vectors.shape[1]),'repeatability_verified':True,
                'synthetic_probe_only':True,'model_size_bytes':sum(p.stat().st_size for p in (e.MODELS/('embeddinggemma-2' if name=='gemma2' else 'Qwen3-Embedding-0.6B-GGUF')).glob('*.safetensors')) if name=='gemma2' else None}
        success=True
    except Exception as error:
        detail={'error_type':type(error).__name__,'error':str(error)[:1000]}
        (target/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
    finally:
        if model:model.close()
        stop.set();thread.join(timeout=2)
    result={'model':name,'success':success,'elapsed_seconds':time.perf_counter()-started,
            'peak_process_tree_rss_bytes':max((a for a,b in samples),default=None),
            'min_machine_available_ram_bytes':min((b for a,b in samples),default=None),
            'cpu_seconds':sum(cpu.values()),'machine_ram_bytes':psutil.virtual_memory().total,
            'cpu_logical':psutil.cpu_count(),'cpu_physical':psutil.cpu_count(logical=False),
            'memory_measurement':'maximum sampled simultaneous process-tree RSS, 100 ms; earlier attempts used sum of per-process peak working sets',
            'versions':{n:version(n) for n in ['numpy','fastembed','onnxruntime','torch','transformers','sentence-transformers','psutil']},
            'generation_calls':0,'development_retrieval_calls':0,**detail}
    s.runtime.write(target/'result.json',result)
    print(json.dumps(result,indent=2),flush=True)
    return success


if __name__=='__main__':
    s.holdout_guard()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model',choices=['minilm','gemma2','qwen3-q4'])
    parser.add_argument('--attempt',type=int,default=1)
    args=parser.parse_args()
    raise SystemExit(0 if probe(args.model,args.attempt) else 1)
