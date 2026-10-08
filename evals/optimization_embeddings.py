"""Frozen local embedding adapters. No generation or remote embedding service."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
LOCAL=ROOT/'knowledge/local'
MODELS=LOCAL/'optimization-models'
LLAMA=Path(r'C:\Users\rajvi\AppData\Local\Microsoft\WinGet\Packages\ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe\llama-server.exe')
QWEN_INSTRUCTION='Given a query, retrieve relevant passages that answer the query'


def normalize(vectors):
    values=np.asarray(vectors,dtype=np.float32)
    norms=np.linalg.norm(values,axis=1,keepdims=True)
    if values.ndim!=2 or not np.isfinite(values).all() or (norms<=0).any():raise ValueError('Invalid local embeddings')
    return values/norms


class MiniLM:
    def __init__(self):
        from outwise.knowledge.embeddings import LocalEmbedder
        self.model=LocalEmbedder(LOCAL/'embedding-model')
        self.lock=self.model.lock
    def documents(self,items):
        a=self.model.embed([f'{p["title"]}. {p.get("section") or ""}. {p["text"]}' for p in items])
        b=self.model.embed([p['text'] for p in items])
        return normalize((a+b)/2)
    def queries(self,texts):return self.model.embed(texts)
    def close(self):pass


class Gemma:
    def __init__(self):
        import torch
        from sentence_transformers import SentenceTransformer
        torch.set_num_threads(4)
        os.environ['HF_HUB_OFFLINE']='1'
        self.model=SentenceTransformer(str(MODELS/'embeddinggemma-2'),device='cpu',local_files_only=True,
                 model_kwargs={'dtype':torch.float32},config_kwargs={'vision_config':None,'audio_config':None})
        self.model.max_seq_length=8192
        self.lock={'repository':'google/embeddinggemma-2','revision':'914f7f89142e33e77833254d9c9b90c3cef7303b',
                   'dimensions':768,'dtype':'float32','modalities':'text only','parameters':sum(p.numel() for p in self.model.parameters())}
    def documents(self,items):
        text=[f'title: {p["title"]} / {p.get("section") or ""} | text: {p["text"]}' for p in items]
        return self.model.encode(text,batch_size=2,prompt='',normalize_embeddings=True,show_progress_bar=False)
    def queries(self,texts):
        return self.model.encode(texts,batch_size=2,prompt='task: search result | query: ',normalize_embeddings=True,show_progress_bar=False)
    def close(self):pass


class Qwen:
    def __init__(self,logs):
        self.url='http://127.0.0.1:8137'
        self.log=(logs/'qwen-embedding-server.log').open('ab')
        (logs/'slots').mkdir(exist_ok=True)
        # Fail rather than attach to an unrelated existing service on the port.
        import socket
        with socket.socket() as check:
            check.bind(('127.0.0.1',8137))
        command=[str(LLAMA),'-m',str(MODELS/'Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q4_K_M.gguf'),
                 '--embedding','--pooling','last','--ctx-size','8192','--batch-size','8192','--ubatch-size','8192',
                 '--parallel','1','--threads','4','--threads-batch','4','--n-gpu-layers','0','--host','127.0.0.1','--port','8137',
                 '--flash-attn','off','--cache-type-k','f32','--cache-type-v','f32',
                 '--no-webui','--no-cache-prompt','--cache-ram','0','--slots','--slot-save-path',str(logs/'slots')]
        (logs/'server-command.json').write_text(json.dumps(command,indent=2)+'\n',encoding='utf-8',newline='\n')
        self.process=subprocess.Popen(command,stdout=self.log,stderr=self.log,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        for _ in range(120):
            if self.process.poll() is not None:raise RuntimeError('Qwen embedding server failed; inspect local log')
            try:
                with urllib.request.urlopen(self.url+'/health',timeout=1) as response:
                    if response.status==200:break
            except Exception:time.sleep(.5)
        else:
            self.close();raise RuntimeError('Qwen embedding startup timeout')
        self.lock=json.loads((MODELS/'Qwen3-Embedding-0.6B-GGUF/quantization.json').read_text())
    def _encode(self,texts):
        vectors=[]
        for text in texts:
            erase=urllib.request.Request(self.url+'/slots/0?action=erase',data=b'{}',headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(erase,timeout=30) as response:json.load(response)
            body=json.dumps({'input':text,'encoding_format':'float','cache_prompt':False}).encode('utf-8')
            request=urllib.request.Request(self.url+'/v1/embeddings',data=body,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(request,timeout=120) as response:result=json.load(response)
            vectors.append(result['data'][0]['embedding'])
        return normalize(vectors)
    def documents(self,items):return self._encode([f'{p["title"]}. {p.get("section") or ""}. {p["text"]}' for p in items])
    def queries(self,texts):return self._encode([f'Instruct: {QWEN_INSTRUCTION}\nQuery: {q}' for q in texts])
    def close(self):
        self.process.terminate()
        try:self.process.wait(timeout=15)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
        self.log.close()


def create(name,logs):
    return {'minilm':MiniLM,'gemma2':Gemma,'qwen3-q4':lambda:Qwen(logs)}[name]()
