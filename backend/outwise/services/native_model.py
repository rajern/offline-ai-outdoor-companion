"""Single-user local llama.cpp server with the measured native generation profile."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
from threading import RLock
import time
import urllib.error
import urllib.request

from outwise.services.model import (ModelService, ModelSettings, ModelNotFoundError,
    ModelRuntimeNotFoundError, ModelLoadError, ModelGenerationError, ModelTimeoutError)
from outwise.services.process_job import ProcessJob

SYSTEM_PROMPT = (Path(__file__).parents[1] / 'prompts/generation.txt').read_text(encoding='utf-8').strip()


def user_message(question, results):
    context = '\n\n'.join(f'[KUNNSKAPSUTDRAG {i}]\nTittel: {r.item.title}\nTema: {r.item.topic}\nInnhold: {r.item.text}'
                           for i, r in enumerate(results, 1))
    return f'[KILDEUTDRAG]\n{context}\n[/KILDEUTDRAG]\n\n[BRUKERSPØRSMÅL]\n{question}\n[/BRUKERSPØRSMÅL]'


class NativeModelService:
    def __init__(self, settings=None):
        self.settings = settings or ModelSettings.from_environment()
        self.process = None
        self.log = None
        self.url = None
        self.lock = RLock()
        self.counter_cache = {}
        self.job = None

    def runtime(self, name):
        cli = Path(ModelService(self.settings)._resolve_runtime()[0])
        path = cli.with_name(name + ('.exe' if os.name == 'nt' else ''))
        if not path.is_file():
            raise ModelRuntimeNotFoundError(f'{name} missing beside llama-cli')
        return path

    def count(self, text):
        if text not in self.counter_cache:
            if not self.settings.model_path.is_file():
                raise ModelNotFoundError('Local model missing')
            try:
                raw = subprocess.run([str(self.runtime('llama-tokenize')), '-m', str(self.settings.model_path),
                                      '--stdin', '--ids', '--offline'], input=text, encoding='utf-8',
                                     capture_output=True, timeout=30, check=True,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                self.counter_cache[text] = len(json.loads(raw.stdout))
            except (subprocess.SubprocessError, ValueError) as exc:
                raise ModelGenerationError('Local prompt tokenization failed') from exc
            # Bounded process memory; counts are a convenience, never an answer cache.
            if len(self.counter_cache) > 256:
                value = self.counter_cache[text]
                self.counter_cache = {text: value}
        return self.counter_cache[text]

    def request(self, endpoint, payload=None, timeout=120):
        request = urllib.request.Request(self.url + endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload is not None else None,
            headers={'Content-Type': 'application/json'})
        # Never inherit a proxy configuration for the numeric loopback server.
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=timeout) as response:
            return json.load(response)

    def start(self):
        if self.process and self.process.poll() is None:
            return
        self.close()
        if not self.settings.model_path.is_file():
            raise ModelNotFoundError('Local model missing')
        server = self.runtime('llama-server')
        with socket.socket() as port:
            port.bind(('127.0.0.1', 0))
            number = port.getsockname()[1]
        self.url = f'http://127.0.0.1:{number}'
        directory = self.settings.model_path.parent.parent / 'knowledge/local/app'
        directory.mkdir(parents=True, exist_ok=True)
        self.log = (directory / 'llama-server.log').open('ab')
        command = [str(server), '-m', str(self.settings.model_path), '--host', '127.0.0.1', '--port', str(number),
            '--ctx-size', '4096', '--parallel', '1', '--threads', '4', '--threads-batch', '4',
            '--n-gpu-layers', '0', '--device', 'none', '--no-op-offload', '--no-kv-offload',
            '--reasoning', 'off', '--jinja', '--chat-template-kwargs', '{"enable_thinking":false}',
            '--no-context-shift', '--no-warmup', '--no-webui', '--cache-ram', '0', '--offline']
        try:
            self.process = subprocess.Popen(command, stdout=self.log, stderr=self.log,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.job = ProcessJob(self.process)
        except OSError as exc:
            self.close()
            raise ModelRuntimeNotFoundError('Could not start local llama.cpp server') from exc
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.close()
                raise ModelLoadError('llama.cpp startup failed; inspect knowledge/local/app/llama-server.log')
            try:
                self.request('/health', timeout=1)
                return
            except (OSError, ValueError):
                time.sleep(.2)
        self.close()
        raise ModelTimeoutError('Local model startup timed out')

    def generate(self, prompt):
        with self.lock:
            self.start()
            try:
                native = self.request('/apply-template', {'messages': [
                    {'role': 'system', 'content': SYSTEM_PROMPT}, {'role': 'user', 'content': prompt}]})['prompt']
                tokens = self.request('/tokenize', {'content': native, 'add_special': False, 'parse_special': True})['tokens']
                if len(tokens) > 3200 or len(tokens) + 512 > 4096:
                    raise ModelGenerationError('Prompt exceeds the fixed input budget; no sources were truncated')
                result = self.request('/completion', {'prompt': tokens, 'n_predict': 512, 'seed': 42,
                    'temperature': .2, 'top_p': .8, 'top_k': 20, 'min_p': .05, 'repeat_penalty': 1.0,
                    'presence_penalty': 0.0, 'frequency_penalty': 0.0, 'stream': False, 'cache_prompt': False})
                if result.get('truncated'):
                    raise ModelGenerationError('Runtime truncated the prompt')
                text = result.get('content', '').strip()
                if not text:
                    raise ModelGenerationError('Local model returned no text')
                return text
            except (TimeoutError, socket.timeout) as exc:
                self.close()
                raise ModelTimeoutError('Local generation timed out') from exc
            except (OSError, KeyError, ValueError) as exc:
                self.close()
                raise ModelGenerationError('Local runtime request failed') from exc

    def close(self):
        if self.process:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill(); self.process.wait()
            self.process = None
        if self.log:
            self.log.close(); self.log = None
        if self.job:
            self.job.close(); self.job = None
