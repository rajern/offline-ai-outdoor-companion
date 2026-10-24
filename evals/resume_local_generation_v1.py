"""Resume the bounded M2-06 generation comparison, preserving the October 11 stop."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import gc
import json
import os
from pathlib import Path
import re
import subprocess
import struct
import threading
import time
import urllib.request

import preflight_local_generation_v1 as p
from optimization_resources import Resources, RAM_RESERVE, RSS_LIMIT

q = p.q
RUN = p.RUN.parent / 'resume-2026-10-24/revision-02'
MODELS = {
    'qwen-2b': {'path': q.t.d.MODEL, 'repo': None},
    'qwen-4b': {'path': p.ROOT / 'models/Qwen_Qwen3.5-4B-Q4_K_M.gguf',
                'repo': 'bartowski/Qwen_Qwen3.5-4B-GGUF', 'file': 'Qwen_Qwen3.5-4B-Q4_K_M.gguf'},
    'gemma-e2b': {'path': p.ROOT / 'models/gemma-4-E2B_q4_0-it.gguf',
                  'repo': 'google/gemma-4-E2B-it-qat-q4_0-gguf', 'file': 'gemma-4-E2B_q4_0-it.gguf'},
}
SETTINGS = {'n_predict': 512, 'temperature': .2, 'top_p': .8, 'top_k': 20,
            'seed': 42, 'stream': False, 'cache_prompt': False}


def gguf_metadata(path):
    """Read only scalar identity/context metadata, skipping tokenizer arrays/tensors."""
    formats = {0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}
    with path.open('rb') as stream:
        def number(fmt):
            return struct.unpack('<'+fmt, stream.read(struct.calcsize(fmt)))[0]
        def string(keep=True):
            size = number('Q')
            if keep: return stream.read(size).decode('utf-8')
            stream.seek(size, 1)
        def value(kind, keep):
            if kind == 8: return string(keep)
            if kind == 9:
                element = number('I'); count = number('Q')
                if element in formats:
                    stream.seek(count*struct.calcsize(formats[element]), 1)
                else:
                    for _ in range(count): value(element, False)
                return None
            return number(formats[kind])
        assert stream.read(4) == b'GGUF' and number('I') in [2,3]
        number('Q'); count = number('Q'); metadata = {}
        for _ in range(count):
            key = string(); kind = number('I')
            keep = (key in ['general.architecture','general.name','general.file_type','tokenizer.chat_template',
                            'tokenizer.ggml.bos_token_id','tokenizer.ggml.eos_token_id','tokenizer.ggml.add_bos_token']
                    or key.endswith('.context_length'))
            result = value(kind, keep)
            if keep: metadata[key] = result
        return metadata


def plan():
    frozen = q.read(p.RUN / 'input-freeze.json')
    for name, expected in {**frozen['historical_freeze']['identities'], **frozen['identities']}.items():
        if q.sha(Path(name)) != expected:
            raise RuntimeError('Frozen historical/input identity mismatch: ' + name)
    for item in frozen['inputs']:
        context = Path(item['context_path']).read_text(encoding='utf-8')
        assert p.hashlib.sha256(context.encode()).hexdigest() == item['context_sha256']
        assert p.messages(item['question'], context) == item['messages']
    return frozen


def eligible_models():
    path = RUN / 'exclusions.json'
    excluded = q.read(path) if path.exists() else {}
    for name, evidence in excluded.items():
        assert name in MODELS and name != 'qwen-2b'
        assert q.sha(Path(evidence['resource_path'])) == evidence['resource_sha256']
        observed = q.read(Path(evidence['resource_path']))
        assert observed['minimum_available_ram_bytes'] >= RAM_RESERVE
        assert observed['peak_process_tree_rss_bytes'] > RSS_LIMIT
    return [name for name in MODELS if name not in excluded]


def download(name):
    model = MODELS[name]
    if not model['repo']:
        return
    folder = RUN / 'downloads' / name
    manifest = folder / 'manifest.json'
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    if manifest.exists():
        meta = q.read(manifest)
    else:
        url = 'https://huggingface.co/api/models/' + model['repo'] + '?blobs=true'
        with opener.open(url, timeout=60) as response:
            info = json.load(response)
        entry = next(s for s in info['siblings'] if s['rfilename'] == model['file'])
        assert info.get('cardData', {}).get('license') == 'apache-2.0'
        meta = {'repo': model['repo'], 'revision': info['sha'], 'file': model['file'],
                'size': entry['size'], 'sha256': entry['lfs']['sha256'], 'license': 'apache-2.0'}
        q.write_once(manifest, meta)
    target = model['path']
    if target.exists():
        assert target.stat().st_size == meta['size'] and q.sha(target) == meta['sha256']
        print(name, 'verified existing exact GGUF', flush=True)
        return
    partial = target.with_suffix('.gguf.partial')
    # Preserve incomplete downloads and support HTTP Range only when acknowledged.
    offset = partial.stat().st_size if partial.exists() else 0
    url = f'https://huggingface.co/{meta["repo"]}/resolve/{meta["revision"]}/{meta["file"]}'
    request = urllib.request.Request(url, headers={'Range': f'bytes={offset}-'} if offset else {})
    with opener.open(request, timeout=120) as response:
        if offset and response.status != 206:
            raise RuntimeError('Download resume range not honored; preserve partial file')
        total = offset
        with partial.open('ab' if offset else 'xb') as output:
            last = time.monotonic()
            while chunk := response.read(1024*1024):
                output.write(chunk); total += len(chunk)
                if time.monotonic() - last > 15:
                    print(name, f'{total/1024**2:.0f}/{meta["size"]/1024**2:.0f} MiB downloaded', flush=True)
                    last = time.monotonic()
    assert partial.stat().st_size == meta['size'] and q.sha(partial) == meta['sha256']
    partial.replace(target)
    print(name, 'downloaded, exact remote SHA-256 verified', flush=True)


def native_input(request, item, actual, training, name):
    prompt = request('/apply-template', {'messages': item['messages']})['prompt']
    assert all(turn['content'] in prompt for turn in item['messages'])
    if name.startswith('qwen'):
        assert '<|im_start|>system\n' in prompt and '<|im_start|>user\n' in prompt
        assert '<|im_start|>assistant' in prompt
        assert '</think>' in prompt.split('<|im_start|>assistant')[-1], 'Thinking-disabled Qwen prefix unverified'
    else:
        assert '<|turn>system\n' in prompt and '<|turn>user\n' in prompt
        assert '<|turn>model' in prompt and '<|think|>' not in prompt, 'Non-thinking Gemma prefix unverified'
    tokens = request('/tokenize', {'content': prompt, 'add_special': True, 'parse_special': True})['tokens']
    p.budget_check(len(tokens), actual, training)
    return {'id': item['id'], 'prompt': prompt, 'tokens': tokens,
            'input_tokens': len(tokens), 'actual_context': actual, 'training_context': training,
            'output_reservation': 512, 'context_sha256': item['context_sha256']}


@contextmanager
def server(model, folder, resources):
    """Use the frozen server flags; allow the full 120s generation deadline."""
    with p.server(model, folder, resources) as short_request:
        command = q.read(folder / 'command.json')
        port = command[command.index('--port')+1]
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        def request(endpoint, payload=None):
            if endpoint != '/completion':
                return short_request(endpoint, payload)
            req = urllib.request.Request('http://127.0.0.1:' + port + endpoint,
                data=json.dumps(payload, ensure_ascii=False).encode(),
                headers={'Content-Type': 'application/json'})
            with opener.open(req, timeout=125) as response:
                return json.load(response)
        yield request


def preflight(name):
    frozen = plan()
    folder = RUN / 'preflight' / name
    if (folder / 'complete.json').exists():
        verify_seal(folder)
        print(name, 'preflight cached', flush=True)
        return
    assert not (folder / 'command.json').exists(), 'Prior uncompleted load retained; reviewed new attempt required'
    model = MODELS[name]['path']
    with Resources() as resources:
        try:
            resources.check()
            embedder = p.LocalEmbedder(q.t.s.runtime.LOCAL / 'embedding-model')
            resources.sample(); resources.check()
            with server(model, folder, resources) as request:
                props = request('/props')
                q.write_once(folder / 'props.json', props)
                actual = props['default_generation_settings']['n_ctx']
                metadata = gguf_metadata(model)
                q.write_once(folder / 'gguf-metadata.json', metadata)
                training = metadata[metadata['general.architecture'] + '.context_length']
                assert actual == 4096
                for item in frozen['inputs']:
                    row = native_input(request, item, actual, training, name)
                    q.write_once(folder / 'inputs' / (item['id'] + '.json'), row)
                q.write_once(folder / 'complete.json', {'model': name, 'inputs': 36,
                      'model_sha256': q.sha(model), 'model_bytes': model.stat().st_size,
                      'actual_context': actual, 'training_context': training, 'inference_calls': 0})
                assert embedder is not None
        finally:
            q.write_once(folder / 'resources.json', resources.result())
    paths = [folder / f for f in ['props.json','gguf-metadata.json','complete.json','resources.json','stdout.txt','stderr.txt']]
    paths += list((folder / 'inputs').glob('*.json'))
    seal(folder, paths)
    print(name, '36 native input/token checks passed; no inference;', resources.result(), flush=True)


def seal(folder, paths):
    q.write_once(folder / 'seal.json', {str(path.relative_to(folder)): q.sha(path) for path in paths})


def verify_seal(folder):
    for name, expected in q.read(folder / 'seal.json').items():
        assert q.sha(folder / name) == expected, str(folder / name)


def freeze():
    plan()
    identities = {str(path): q.sha(path) for path in [Path(__file__).resolve(),
                  p.PROTOCOL, p.PROMPT, p.RUN / 'input-freeze.json',
                  p.ROOT / 'evals/optimization_resources.py',
                  p.ROOT / 'evals/continue_local_generation_v1.py',
                  p.ROOT / 'evals/run_eligible_local_generation_v1.py']}
    for path in [p.RUNTIME, *sorted(p.RUNTIME.parent.glob('*.dll'))]:
        identities[str(path)] = q.sha(path)
    if (RUN / 'exclusions.json').exists():
        identities[str(RUN / 'exclusions.json')] = q.sha(RUN / 'exclusions.json')
    for name in eligible_models():
        model = MODELS[name]
        folder = RUN / 'preflight' / name
        verify_seal(folder)
        identities[str(model['path'])] = q.sha(model['path'])
        identities[str(folder / 'seal.json')] = q.sha(folder / 'seal.json')
        if model['repo']:
            identities[str(RUN / 'downloads' / name / 'manifest.json')] = q.sha(RUN / 'downloads' / name / 'manifest.json')
    q.write_once(RUN / 'experiment-freeze.json', {'identities': identities, 'settings': SETTINGS,
                 'source_plan_sha256': q.sha(p.RUN / 'input-freeze.json'),
                 'eligible_models': eligible_models(),
                 'max_screen_calls': 33, 'max_finalist_calls': 25,
                 'no_prior_new_model_responses': not (RUN / 'responses').exists()})
    print('Complete eligible-model experiment frozen before responses:', eligible_models(), flush=True)


def verify():
    frozen = q.read(RUN / 'experiment-freeze.json')
    for name, expected in frozen['identities'].items():
        assert q.sha(Path(name)) == expected, 'Frozen experiment identity changed: ' + name
    assert frozen['eligible_models'] == eligible_models()
    for name in eligible_models():
        verify_seal(RUN / 'preflight' / name)
    return frozen


def guarded_completion(request, payload, resources):
    result = {}; error = []
    def worker():
        try: result.update(request('/completion', payload))
        except BaseException as exc: error.append(exc)
    thread = threading.Thread(target=worker, daemon=True)
    thread.start(); start = time.monotonic()
    while thread.is_alive():
        thread.join(.1); resources.check()
        if time.monotonic() - start > 120:
            raise RuntimeError('Generation exceeded frozen 120-second runtime timeout; do not retry')
    if error: raise error[0]
    return result


def run_responses(stage, model_name=None):
    frozen = verify()
    inputs = plan()['inputs']
    if stage == 'screen':
        keys = p.STAGE_ONE + ['diagnostic-case-03','diagnostic-case-08','diagnostic-case-17']
        names = frozen['eligible_models']
    else:
        review = q.read(RUN / 'finalist-decision.json')
        assert review['eligible'] and review['model'] == model_name
        assert review['experiment_freeze_sha256'] == q.sha(RUN / 'experiment-freeze.json')
        keys = [i['id'] for i in inputs if i['stage'] in ['finalist','paraphrase','repeat']]
        assert len(keys) == 25
        names = [model_name]
    for name in names:
        session = RUN / 'runtime' / stage / name
        # Never overwrite a previous process log. Successful response cache is independent.
        attempt = len(list(session.glob('attempt-*'))) + 1
        session = session / f'attempt-{attempt:02d}'
        with Resources() as resources:
            try:
                resources.check()
                embedder = p.LocalEmbedder(q.t.s.runtime.LOCAL / 'embedding-model')
                with server(MODELS[name]['path'], session, resources) as request:
                    for key in keys:
                        item = next(i for i in inputs if i['id'] == key)
                        native = q.read(RUN / 'preflight' / name / 'inputs' / (key + '.json'))
                        identity = q.digest({'freeze': frozen, 'native': native, 'seed': item['seed']})
                        folder = RUN / 'responses' / name / key
                        if (folder / 'seal.json').exists():
                            verify_seal(folder)
                            assert q.read(folder / 'result.json')['cache_key'] == identity
                            print(name, key, 'cached', flush=True); continue
                        assert not (folder / 'dispatched.json').exists(), 'Unsealed dispatched call; no retry'
                        # The exact preflight-verified token sequence is used directly: no retemplating/BOS ambiguity.
                        payload = {**SETTINGS, 'prompt': native['tokens'], 'seed': item['seed']}
                        q.write_once(folder / 'request.json', payload)
                        q.write_once(folder / 'dispatched.json', {'cache_key': identity})
                        start = time.monotonic()
                        answer = guarded_completion(request, payload, resources)
                        q.write_once(folder / 'response.json', answer)
                        assert not answer.get('truncated'), 'Runtime truncated context'
                        assert answer['tokens_evaluated'] == native['input_tokens'], 'Actual runtime input changed'
                        assert answer['generation_settings']['n_ctx'] == 4096
                        assert answer['tokens_predicted'] <= 512
                        assert answer.get('stop_type') in ['eos','word','limit']
                        (folder / 'answer.txt').write_text(answer['content'], encoding='utf-8')
                        q.write_once(folder / 'result.json', {'cache_key': identity, 'model': name, 'id': key,
                               'elapsed_seconds': time.monotonic()-start, 'stop_type': answer['stop_type'],
                               'input_tokens': native['input_tokens'], 'output_tokens': answer['tokens_predicted'],
                               'resources_so_far': resources.result(), 'new_inference_calls': 1})
                        seal(folder, [folder / f for f in ['request.json','dispatched.json','response.json','answer.txt','result.json']])
                        print(name, key, answer['tokens_predicted'], 'output tokens,', answer['stop_type'], flush=True)
                assert embedder is not None
            finally:
                q.write_once(session / 'resources.json', resources.result())
        del embedder; gc.collect()
    verify()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['preflight','download','freeze','screen','finalist','verify'])
    parser.add_argument('--model', choices=list(MODELS))
    args = parser.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    q.t.s.holdout_guard()
    with q.LOCK.open('x', encoding='utf-8') as lock:
        lock.write(str(os.getpid()))
    try:
        if args.command == 'download':
            assert args.model in ['qwen-4b','gemma-e2b']
            download(args.model)
        else:
            p.windows.offline()
            if args.command in ['preflight','screen','finalist']:
                assert not (RUN / 'stop.json').exists(), 'Retained stop requires reviewed technical resume'
            if args.command == 'preflight': preflight(args.model)
            elif args.command == 'freeze': freeze()
            elif args.command == 'verify': verify()
            else: run_responses(args.command, args.model)
    except BaseException as exc:
        if args.command in ['preflight','screen','finalist']:
            q.write_once(RUN / 'stop.json', {'command': args.command, 'model': args.model,
                         'error': str(exc), 'paid_api_calls': 0})
        raise
    finally:
        q.LOCK.unlink()


if __name__ == '__main__':
    main()
