"""No-inference preflight of the owner-approved local generation comparison."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import run_qwen_rag_system_v1 as q
import qwen_system_windows_adapter_v1 as windows
from optimization_resources import Resources
from outwise.knowledge.embeddings import LocalEmbedder

ROOT = q.ROOT
RUN = ROOT / 'knowledge/local/diagnostics/local-generation-comparison-v1-2026-10-11/revision-02'
OLD = q.RUN / 'revision-02'
RUNTIME = Path(os.environ['LOCALAPPDATA']) / 'Microsoft/WinGet/Packages/ggml.llamacpp_Microsoft.Winget.Source_8wekyb3d8bbwe/llama-server.exe'
PROTOCOL = ROOT / 'evals/local_generation_comparison_protocol.v1.md'
PROMPT = ROOT / 'evals/local_generation_prompt.v1.md'
STAGE_ONE = ['case-19', 'case-05', 'case-08', 'case-17', 'case-21', 'case-23', 'case-15', 'case-25']
PARAPHRASES = {
    'case-03': 'På tur er drikkevannet brukt opp. Vi har stormkjøkken og kan hente vann fra en bekk som ser ren ut. Er vannet trygt, og hvordan bør vi behandle det før vi drikker?',
    'case-08': 'En voksen turkamerat falt plutselig sammen på rasteplassen. Hun reagerer ikke på tiltale, og brystkassen beveger seg regelmessig. Vi vet ikke hvordan vi skal hjelpe henne. Hva gjør vi?',
    'case-17': 'Turkameraten ble stukket av en veps. Kort etter fikk han utslett flere steder og hovne lepper, og han sier det er trangt i halsen. Kan vi vente til vi har kommet ned fra fjellet?',
    'case-21': 'Vi kan ikke koke bekkevannet fordi stormkjøkkenet er ødelagt. Utstyret vårt er et absolutt 0,3-mikronfilter og desinfiseringstabletter. Beskytter bare filteret mot alt, og hva skal brukes først?',
}
REPEATS = ['case-08', 'case-17', 'case-21', 'case-23']


def messages(question, context):
    return [{'role': 'system', 'content': PROMPT.read_text(encoding='utf-8').strip()},
            {'role': 'user', 'content': f'[KILDEUTDRAG]\n{context}\n[/KILDEUTDRAG]\n\n[BRUKERSPØRSMÅL]\n{question}\n[/BRUKERSPØRSMÅL]'}]


def budget_check(count, actual_context, training_context):
    if count > 3200:
        raise RuntimeError(f'Actual template-inclusive input {count} exceeds 3200; no truncation')
    if count + 512 > min(actual_context, training_context):
        raise RuntimeError('Input plus reserved output exceeds actual context; no limit change')


def prepare():
    q.t.s.holdout_guard()
    frozen = q.read(OLD / 'freeze.json')
    for name, expected in frozen['identities'].items():
        if q.sha(Path(name)) != expected:
            raise RuntimeError('Historical frozen input changed: ' + name)
    cases = q.t.s.load_development()['cases']
    inputs = []
    bindings = {}
    def add(key, cid, question, context_path, stage, seed=42):
        context = context_path.read_text(encoding='utf-8')
        payload = messages(question, context)
        inputs.append({'id': key, 'case_id': cid, 'question': question, 'stage': stage,
                       'seed': seed, 'context_path': str(context_path),
                       'context_sha256': hashlib.sha256(context.encode()).hexdigest(),
                       'messages': payload})
        bindings[str(context_path)] = q.sha(context_path)
    for case in cases:
        cid = case['id']
        # This is the exact source-block serialization the old model received.
        context_path = q.TARGET / cid / 'context.txt'
        context = context_path.read_text(encoding='utf-8')
        old_prompt = (OLD / 'baseline' / cid / 'prompt.txt').read_text(encoding='utf-8')
        assert context in old_prompt
        seal = q.read(OLD / 'baseline' / cid / 'seal.json')
        for name, expected in seal.items():
            assert q.sha(OLD / 'baseline' / cid / name) == expected
        add(cid, cid, case['question'], context_path, 'screen' if cid in STAGE_ONE else 'finalist')
    diag = q.read(OLD / 'diagnostic-sufficient-context/freeze.json')
    for cid in ['case-03', 'case-08', 'case-17']:
        path = OLD / 'diagnostic-sufficient-context' / cid / 'prompt.txt'
        text = path.read_text(encoding='utf-8')
        # Historical prompt identity hashes the actual logical CLI input (LF),
        # while the separately sealed Windows text file has CRLF bytes.
        assert hashlib.sha256(text.encode()).hexdigest() == diag['inputs'][cid]['prompt_sha256']
        for name, expected in q.read(path.parent / 'seal.json').items():
            assert q.sha(path.parent / name) == expected
        context = text[text.index('[KUNNSKAPSUTDRAG 1]'):text.index('\n\n[BRUKERSPØRSMÅL]')]
        own = RUN / 'inputs' / f'diagnostic-{cid}-context.txt'
        if own.exists():
            assert own.read_text(encoding='utf-8') == context
        else:
            own.parent.mkdir(parents=True, exist_ok=True)
            own.write_text(context, encoding='utf-8')
        case = next(c for c in cases if c['id'] == cid)
        add('diagnostic-' + cid, cid, case['question'], own, 'diagnostic')
        bindings[str(path)] = q.sha(path)
    for cid, question in PARAPHRASES.items():
        add('paraphrase-' + cid, cid, question, q.TARGET / cid / 'context.txt', 'paraphrase')
    for cid in REPEATS:
        case = next(c for c in cases if c['id'] == cid)
        add('repeat-' + cid, cid, case['question'], q.TARGET / cid / 'context.txt', 'repeat', 43)
    assert len(inputs) == 36
    binding_paths = [Path(__file__).resolve(), PROTOCOL, PROMPT,
                     OLD / 'freeze.json', OLD / 'complete.json',
                     OLD / 'diagnostic-sufficient-context/freeze.json',
                     ROOT / 'evals/qwen_rag_system_protocol.v1.md',
                     ROOT / 'evals/optimization_resources.py',
                     ROOT / 'evals/qwen_rag_answer_review.v1.json']
    bindings.update({str(p): q.sha(p) for p in binding_paths})
    plan = {'version': 1, 'stage_one': STAGE_ONE, 'inputs': inputs,
            'historical_freeze': frozen, 'identities': bindings,
            'limits': {'input_tokens': 3200, 'output_tokens': 512, 'runtime_context': 4096,
                       'ram_reserve_bytes': 256*1024**2, 'rss_limit_bytes': 4*1024**3},
            'max_initial_calls': 33, 'max_finalist_calls': 25,
            'paid_api_calls': 0, 'inference_calls': 0}
    q.write_once(RUN / 'input-freeze.json', plan)
    return plan


@contextmanager
def server(model, folder, resources):
    folder.mkdir(parents=True, exist_ok=True)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0)); port = reservation.getsockname()[1]
    command = [str(RUNTIME), '--model', str(model), '--host', '127.0.0.1', '--port', str(port),
               '--ctx-size', '4096', '--parallel', '1', '--reasoning', 'off',
               '--chat-template-kwargs', '{"enable_thinking":false}', '--no-warmup',
               '--device', 'none', '--gpu-layers', '0', '--no-op-offload', '--fit', 'off',
               '--no-context-shift', '--no-cache-prompt', '--cache-ram', '0',
               '--no-webui', '--jinja']
    q.write_once(folder / 'command.json', command)
    out = (folder / 'stdout.txt').open('w', encoding='utf-8')
    err = (folder / 'stderr.txt').open('w', encoding='utf-8')
    proc = subprocess.Popen(command, stdout=out, stderr=err)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def request(endpoint, payload=None):
        resources.check()
        req = urllib.request.Request(f'http://127.0.0.1:{port}{endpoint}',
              data=None if payload is None else json.dumps(payload, ensure_ascii=False).encode(),
              headers={'Content-Type': 'application/json'})
        with opener.open(req, timeout=10) as response:
            data = json.load(response)
        resources.check()
        return data
    try:
        start = time.monotonic()
        while True:
            resources.sample(); resources.check()
            if proc.poll() is not None:
                raise RuntimeError('Local server exited before ready; inspect retained stderr')
            try:
                request('/health'); break
            except (urllib.error.URLError, TimeoutError):
                if time.monotonic() - start > 120:
                    raise RuntimeError('Local model loading exceeded 120s; no inference')
                time.sleep(.1)
        yield request
    finally:
        if proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=10)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=10)
        out.close(); err.close()
        resources.sample()


def preflight():
    plan = prepare()
    if (RUN / 'stop.json').exists():
        raise RuntimeError('Existing preflight stop retained; explicit reviewed resume required')
    # Use the existing control before downloading the larger candidates.
    folder = RUN / 'preflight/qwen-2b'
    with Resources() as resources:
        try:
            resources.check()
            embedder = LocalEmbedder(q.t.s.runtime.LOCAL / 'embedding-model')
            resources.sample(); resources.check()
            model = q.t.d.MODEL
            with server(model, folder, resources) as request:
                props = request('/props')
                q.write_once(folder / 'props.json', props)
                actual = props['default_generation_settings']['n_ctx']
                metadata = props.get('model_meta', {})
                training = metadata.get('n_ctx_train')
                if training is None:
                    # Metadata logging is from this actual model load, not documentation.
                    import re
                    log = (folder / 'stderr.txt').read_text(encoding='utf-8')
                    match = re.search(r'n_ctx_train\s*=\s*(\d+)', log)
                    if not match: raise RuntimeError('Actual model training context is unverified')
                    training = int(match.group(1))
                assert actual == 4096
                model_hash = q.sha(model)
                runtime_hash = q.sha(RUNTIME)
                rows = []
                for item in plan['inputs']:
                    prompt = request('/apply-template', {'messages': item['messages']})['prompt']
                    assert '<|im_start|>system\n' in prompt and '<|im_start|>user\n' in prompt
                    assert item['messages'][0]['content'] in prompt and item['messages'][1]['content'] in prompt
                    assert prompt.endswith('<think>\n\n</think>\n\n'), 'Non-thinking assistant prefix unverified'
                    tokens = request('/tokenize', {'content': prompt, 'add_special': True, 'parse_special': True})['tokens']
                    budget_check(len(tokens), actual, training)
                    row = {'id': item['id'], 'prompt': prompt, 'tokens': tokens,
                           'input_tokens': len(tokens), 'actual_context': actual,
                           'training_context': training, 'output_reservation': 512,
                           'unused_context_capacity': actual-len(tokens)-512,
                           'model_sha256': model_hash, 'runtime_sha256': runtime_hash}
                    q.write_once(folder / 'inputs' / (item['id'] + '.json'), row)
                    rows.append({k:v for k,v in row.items() if k not in ['tokens', 'prompt']})
                    print(item['id'], len(tokens), 'actual input tokens; no inference', flush=True)
                q.write_once(folder / 'complete.json', {'rows': rows, 'inference_calls': 0})
                # Keep the embedding object alive until after server shutdown.
                assert embedder is not None
        finally:
            q.write_once(folder / 'resources.json', resources.result())
    return {'status': 'control_preflight_passed', 'inference_calls': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'preflight'])
    args = parser.parse_args()
    windows.offline()
    RUN.mkdir(parents=True, exist_ok=True)
    with q.LOCK.open('x', encoding='utf-8') as handle:
        handle.write(str(os.getpid()))
    try:
        result = prepare() if args.command == 'prepare' else preflight()
        print(json.dumps({k:v for k,v in result.items() if k not in ['inputs','identities','historical_freeze']}, ensure_ascii=False), flush=True)
    except BaseException as exc:
        if args.command == 'preflight':
            q.write_once(RUN / 'stop.json', {'status': 'preflight_blocked', 'error': str(exc),
                         'inference_calls': 0, 'paid_api_calls': 0})
        raise
    finally:
        q.LOCK.unlink()


if __name__ == '__main__':
    main()
