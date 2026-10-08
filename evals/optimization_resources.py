"""Small process-tree resource guard and embedding-input accounting."""
from __future__ import annotations
from contextlib import AbstractContextManager
import json
import threading
import time
import urllib.request
import numpy as np
import psutil

# Operational reserves fixed before observing any retrieval-quality result.
RAM_RESERVE=256*1024**2
RSS_LIMIT=4*1024**3


class Resources(AbstractContextManager):
    def __init__(self):
        self.stop=threading.Event();self.samples=[];self.cpu={};self.initial={}
        self.parent=psutil.Process();self.started=time.perf_counter()
        t=self.parent.cpu_times();self.initial[self.parent.pid]=t.user+t.system
    def sample(self):
        rss=0
        for process in [self.parent]+self.parent.children(recursive=True):
            try:
                rss+=process.memory_info().rss;t=process.cpu_times()
                self.cpu[process.pid]=t.user+t.system
            except (psutil.NoSuchProcess,psutil.AccessDenied):pass
        self.samples.append((rss,psutil.virtual_memory().available))
    def __enter__(self):
        self.sample()
        def monitor():
            while not self.stop.wait(.1):self.sample()
        self.thread=threading.Thread(target=monitor,daemon=True);self.thread.start();return self
    def __exit__(self,*args):
        self.sample();self.stop.set();self.thread.join(timeout=2)
    def result(self):
        return {'elapsed_seconds':time.perf_counter()-self.started,
                'peak_process_tree_rss_bytes':max(a for a,b in self.samples),
                'minimum_available_ram_bytes':min(b for a,b in self.samples),
                'cpu_seconds':sum(v-self.initial.get(p,0) for p,v in self.cpu.items()),
                'sample_interval_seconds':.1,'memory_method':'sampled simultaneous process-tree RSS'}
    def check(self):
        if max(a for a,b in self.samples)>RSS_LIMIT or min(b for a,b in self.samples)<RAM_RESERVE:
            raise RuntimeError('Resource guard: process RSS limit or available RAM reserve exceeded')


def input_texts(name,items,questions):
    contextual=[f'{p["title"]}. {p.get("section") or ""}. {p["text"]}' for p in items]
    if name=='minilm':return contextual+[p['text'] for p in items]+questions
    if name=='gemma2':return [f'title: {p["title"]} / {p.get("section") or ""} | text: {p["text"]}' for p in items]+['task: search result | query: '+q for q in questions]
    from optimization_embeddings import QWEN_INSTRUCTION
    return contextual+[f'Instruct: {QWEN_INSTRUCTION}\nQuery: {q}' for q in questions]


def input_accounting(name,model,items,questions):
    texts=input_texts(name,items,questions)
    if name=='minilm':
        tokenizer=model.model._model.model.tokenizer
        from tokenizers import Tokenizer
        full=Tokenizer.from_str(tokenizer.to_str());full.no_truncation();full.no_padding()
        original=[len(x.ids) for x in full.encode_batch(texts)]
        actual=[sum(x.attention_mask) for x in tokenizer.encode_batch(texts)]
    elif name=='gemma2':
        tokenizer=model.model.tokenizer
        original=[len(x) for x in tokenizer(texts,truncation=False,padding=False)['input_ids']]
        actual=[len(x) for x in tokenizer(texts,truncation=True,max_length=model.model.max_seq_length,padding=False)['input_ids']]
    else:
        original=[]
        for text in texts:
            request=urllib.request.Request(model.url+'/tokenize',data=json.dumps({'content':text,'add_special':True,'parse_special':True}).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(request,timeout=30) as response:original.append(len(json.load(response)['tokens']))
        if max(original)>1024:raise RuntimeError('Qwen embedding input exceeds frozen single-batch capacity; no truncation permitted')
        actual=original.copy()
    return {'input_count':len(texts),'document_inputs':len(texts)-len(questions),
        'query_inputs':len(questions),'original_token_counts':original,'actual_token_counts':actual,
        'truncated_inputs':sum(a>b for a,b in zip(original,actual)),
        'tokens_removed':sum(a-b for a,b in zip(original,actual)),
        'max_original_tokens':max(original),'max_actual_tokens':max(actual),
        'method':'model tokenizer, exact adapter strings; MiniLM uses both existing text/context views',
        'input_sha256':[__import__('hashlib').sha256(t.encode('utf-8')).hexdigest() for t in texts]}


def validate_vectors(documents,queries,item_count,case_count):
    if documents.ndim!=2 or queries.ndim!=2 or documents.shape[0]!=item_count or queries.shape[0]!=case_count or documents.shape[1]!=queries.shape[1]:raise ValueError('Embedding shape mismatch')
    for value in [documents,queries]:
        if not np.isfinite(value).all() or not np.allclose(np.linalg.norm(value,axis=1),1,atol=1e-4):raise ValueError('Embedding normalization/finiteness failure')
