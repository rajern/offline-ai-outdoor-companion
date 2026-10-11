"""Isolated, resumable application Qwen baseline; no retrieval optimization."""
from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
sys.path.insert(0, str(ROOT / 'knowledge/local/system-test-deps'))
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')

import numpy as np
import psutil
import run_targeted_retrieval_v1 as t
from optimization_resources import Resources, RAM_RESERVE, RSS_LIMIT
from outwise.knowledge.embeddings import LocalEmbedder
from outwise.services.model import ModelService, ModelSettings, ProcessResult
from outwise.services.orchestrator import Orchestrator, _build_grounded_prompt, _sources_from

RUN = ROOT / 'knowledge/local/diagnostics/qwen-rag-system-v1-2026-10-11'
PROTOCOL = ROOT / 'evals/qwen_rag_system_protocol.v1.md'
TARGET = t.RUN / 'configurations/T-ranking'
LOCK = ROOT / 'knowledge/local/qwen-rag-system.lock'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def write_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if read(path) != value:
            raise ValueError('Existing record differs: ' + str(path))
        return
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def offline():
    t.s.holdout_guard()
    def denied(*args, **kwargs):
        raise PermissionError('Network disabled in system-test Python process')
    socket.create_connection = denied
    socket.socket.connect = denied
    socket.socket.connect_ex = denied


class ReadOnlyCounter:
    """Packing equality uses only previously sealed tokenizer outputs."""
    def count(self, text):
        key = hashlib.sha256(text.encode()).hexdigest()
        for base in [t.d.RUN, t.PREVIOUS, t.RUN]:
            folder = base / 'tokenization' / key
            if (folder / 'count.json').exists():
                record = read(folder / 'count.json')
                assert (folder / 'input.txt').read_text(encoding='utf-8') == text
                assert sha(folder / 'stdout.txt') == record['stdout_sha256']
                ids = read(folder / 'stdout.txt')
                assert len(ids) == record['tokens'] and all(isinstance(v, int) for v in ids)
                return record['tokens'], key
        raise ValueError('No frozen tokenization for reconstructed candidate prompt')


class CandidateRetriever:
    def __init__(self, embedder):
        self.embedder = embedder
        self.parents = [t.d.KnowledgeItem(**p) for p in read(t.s.runtime.LOCAL / 'knowledge.json')['items']]
        self.vectors = np.load(t.RUN / 'index/documents.npy', allow_pickle=False)
        self.queries = np.load(t.RUN / 'index/queries.npy', allow_pickle=False)
        self.cases = t.s.load_development()['cases']
        self.rows = {r['case_id']: r for r in read(TARGET / 'retrieved-all.json')}
        self.active = None
        self.last = None

    def retrieve(self, query, *, top_k=16):
        assert top_k == 16 and self.active is not None
        case = self.active
        assert query == case['question']
        row = self.rows[case['id']]
        start = time.perf_counter()
        vector = self.embedder.embed([query])[0]
        index = next(i for i, c in enumerate(self.cases) if c['id'] == case['id'])
        assert np.allclose(vector, self.queries[index], atol=1e-6, rtol=1e-6)
        scores = self.vectors @ vector
        order = sorted([i for i, p in enumerate(self.parents)
                        if t.d.allowed_in_jurisdiction(p, case['jurisdiction'])],
                       key=lambda i: (-float(scores[i]), self.parents[i].id))
        seeds = [t.d.RetrievedKnowledgeItem(self.parents[i], float(scores[i])) for i in order[:16]]
        assert [r.item.id for r in seeds] == [r['item']['id'] for r in row['seeds']]
        results, packets, trace = t.d.pack(case, seeds, self.parents, 'P3', ReadOnlyCounter())
        assert [r.item.id for r in results] == [r['item']['id'] for r in row['excerpts']]
        prompt = _build_grounded_prompt(query, results)
        assert prompt == (TARGET / case['id'] / 'prompt-not-executed.txt').read_text(encoding='utf-8')
        assert ReadOnlyCounter().count(prompt)[0] == row['prompt_tokens'] <= 2000
        self.last = {'query_ranking_packing_seconds': time.perf_counter() - start,
                     'prompt_sha256': row['prompt_sha256'], 'context_sha256': row['context_sha256'],
                     'prompt_tokens': row['prompt_tokens'], 'context_tokens': row['context_tokens'],
                     'passages': len(results), 'budget_excluded_packets': row['budget_excluded_packets'],
                     'source_ids': [r.item.id for r in results]}
        return results


class GuardedRunner:
    """Capture raw inference before any later guard/parse failure; never auto-retry."""
    def __init__(self, directory, resources):
        self.directory, self.resources = directory, resources

    def run(self, command, timeout_seconds):
        self.resources.check()
        write_once(self.directory / 'command.json', list(command))
        start = time.perf_counter()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   encoding='utf-8', errors='replace')
        error = None
        output = stderr = ''
        try:
            while True:
                try:
                    output, stderr = process.communicate(timeout=.1)
                    break
                except subprocess.TimeoutExpired:
                    self.resources.sample()
                    self.resources.check()
                    if time.perf_counter() - start > timeout_seconds:
                        raise subprocess.TimeoutExpired(command, timeout_seconds)
        except BaseException as exc:
            error = exc
            process.kill()
            output, stderr = process.communicate()
        (self.directory / 'stdout.txt').write_text(output, encoding='utf-8')
        (self.directory / 'stderr.txt').write_text(stderr, encoding='utf-8')
        self.resources.sample()
        write_once(self.directory / 'process.json', {
            'returncode': process.returncode, 'elapsed_seconds': time.perf_counter() - start,
            'error': str(error) if error else None, 'resources': self.resources.result()})
        if error:
            raise error
        self.resources.check()
        return ProcessResult(process.returncode, output, stderr)


def freeze():
    t.verify()
    t.checked_index()
    rows = t.verify_rows('T-ranking')
    settings = ModelSettings.from_environment()
    assert settings.model_path.resolve() == t.d.MODEL.resolve()
    service = ModelService(settings)
    runtime = Path(service._resolve_runtime()[0])
    assert sha(settings.model_path) == '57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8'
    paths = [Path(__file__), PROTOCOL, settings.model_path, runtime, t.d.TOKENIZER,
             t.RUN / 'freeze.json', t.RUN / 'index/index.json', t.RUN / 'index/documents.npy',
             t.RUN / 'index/queries.npy', t.s.runtime.LOCAL / 'knowledge.json',
             ROOT / 'evals/retrieval_cases.v1.yaml', ROOT / 'evals/retrieval_development.v2.yaml',
             ROOT / 'evals/retrieval_development_additions.v2.yaml',
             ROOT / 'evals/retrieval_targeted_review_required.v1.json',
             ROOT / 'evals/optimization_resources.py', ROOT / 'evals/run_retrieval_optimization_v1.py']
    paths += list((ROOT / 'backend/outwise').rglob('*.py'))
    paths += [p for p in (t.s.runtime.LOCAL / 'embedding-model').rglob('*') if p.is_file()]
    for row in rows:
        paths += [TARGET / row['case_id'] / name for name in
                  ['retrieved.json', 'context.txt', 'prompt-not-executed.txt', 'score.json']]
    identities = {str(p): sha(p) for p in sorted(set(paths))}
    runtime_version = subprocess.run([str(runtime), '--version'], capture_output=True,
                                     encoding='utf-8', errors='replace', timeout=30)
    value = {'version': 1, 'candidate': 'MiniLM T-ranking/k16/no-threshold/original-P3',
             'settings': {**asdict(settings), 'model_path': str(settings.model_path),
                          'llama_cli_path': str(runtime)},
             'identities': identities, 'case_ids': [r['case_id'] for r in rows],
             'runtime_version': runtime_version.stdout + runtime_version.stderr,
             'protocol_sha256': sha(PROTOCOL), 'ram_reserve_bytes': RAM_RESERVE,
             'rss_limit_bytes': RSS_LIMIT, 'paid_api_calls': 0, 'judge_calls': 0,
             'case16': 'requires_review; non-blocking isolated testing, owner quality gate',
             'offline_evidence': 'Python sockets denied; explicit local GGUF; OS network not disconnected'}
    # Version/help text may vary only before freeze; resumes verify immutable identities.
    write_once(RUN / 'freeze.json', value)
    return value


def verify():
    value = read(RUN / 'freeze.json')
    for name, expected in value['identities'].items():
        if sha(Path(name)) != expected:
            raise ValueError('Frozen system input changed: ' + name)
    return value


def cache_key(frozen, prompt):
    return digest({'prompt': prompt, 'settings': frozen['settings'],
                   'identities': frozen['identities'], 'protocol': frozen['protocol_sha256']})


async def api_answer(app, message):
    import httpx
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                base_url='http://127.0.0.1') as client:
        response = await client.post('/api/chat', json={'message': message})
        return response.status_code, response.json()


def execute():
    offline()
    RUN.mkdir(parents=True, exist_ok=True)
    if (RUN / 'stop.json').exists():
        raise RuntimeError('Prior stop retained; explicit reviewed resume required')
    frozen = verify() if (RUN / 'freeze.json').exists() else freeze()
    with Resources() as startup:
        startup.check()
        embedder = LocalEmbedder(t.s.runtime.LOCAL / 'embedding-model')
        retriever = CandidateRetriever(embedder)
    write_once(RUN / 'startup-resources.json', startup.result())
    startup.check()
    from outwise.main import create_app
    settings = ModelSettings(model_path=Path(frozen['settings']['model_path']),
                             llama_cli_path=Path(frozen['settings']['llama_cli_path']))
    for case in retriever.cases:
        cid = case['id']; directory = RUN / 'baseline' / cid
        prompt = (TARGET / cid / 'prompt-not-executed.txt').read_text(encoding='utf-8')
        key = cache_key(frozen, prompt)
        if (directory / 'result.json').exists():
            result = read(directory / 'result.json')
            assert result['cache_key'] == key
            for name, expected in read(directory / 'seal.json').items():
                assert sha(directory / name) == expected
            print(cid, 'cached', flush=True)
            continue
        if (directory / 'command.json').exists():
            raise RuntimeError('Unsealed prior inference requires review, no automatic repeat: ' + cid)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'prompt.txt').write_text(prompt, encoding='utf-8')
        retriever.active = case
        with Resources() as resources:
            resources.check()
            service = ModelService(settings, GuardedRunner(directory, resources))
            app = create_app(service, retriever)
            app.state.orchestrator = Orchestrator(retriever, service, top_k=16)
            started = time.perf_counter()
            status, body = asyncio.run(api_answer(app, case['question']))
            elapsed = time.perf_counter() - started
        write_once(directory / 'api-response.json', {'status': status, 'body': body})
        resources.check()
        if status != 200:
            raise RuntimeError('Application inference failed: ' + cid + ' HTTP ' + str(status))
        stored = [t.d.RetrievedKnowledgeItem(t.d.KnowledgeItem(**r['item']), r['score'])
                  for r in retriever.rows[cid]['excerpts']]
        expected_sources = [{('name' if k == 'source_name' else 'url' if k == 'source_url' else k): v
                             for k, v in asdict(source).items() if v is not None}
                            for source in _sources_from(stored)]
        assert body['sources'] == expected_sources
        answer = body['answer']
        (directory / 'answer.txt').write_text(answer, encoding='utf-8')
        output_tokens, _ = t.d.TokenCounter(RUN / 'tokenization').count(answer)
        result = {'case_id': cid, 'cache_key': key, 'retrieval': retriever.last,
                  'end_to_end_seconds': elapsed, 'resources': resources.result(),
                  'answer_tokens_locked_tokenizer': output_tokens,
                  'source_metadata_matches': True, 'http_status': status,
                  'corpus_gap': bool(case.get('insufficient_coverage')),
                  'actual_calls': 1, 'codex_calls': 0, 'paid_api_calls': 0}
        write_once(directory / 'result.json', result)
        names = ['prompt.txt', 'command.json', 'stdout.txt', 'stderr.txt', 'process.json',
                 'api-response.json', 'answer.txt', 'result.json']
        write_once(directory / 'seal.json', {name: sha(directory / name) for name in names})
        print(cid, f'{elapsed:.2f}s', f'{output_tokens} answer tokens',
              f'RSS {resources.result()["peak_process_tree_rss_bytes"]/1048576:.1f} MiB', flush=True)
    verify()
    t.verify()
    write_once(RUN / 'complete.json', {'baseline_rows': 25, 'new_judge_calls': 0,
                                      'historical_retrieval_preserved': True})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['freeze', 'run', 'verify'])
    args = parser.parse_args()
    offline()
    RUN.mkdir(parents=True, exist_ok=True)
    with LOCK.open('x', encoding='utf-8') as handle:
        handle.write(str(os.getpid()))
    try:
        if args.command == 'freeze':
            freeze(); print('Inputs and answer protocol frozen; no inference')
        elif args.command == 'verify':
            verify(); print('Frozen inputs verified')
        else:
            execute()
    except BaseException as exc:
        if args.command == 'run':
            write_once(RUN / 'stop.json', {'error': str(exc), 'time': t.s.runtime.now(),
                       'completed_rows': len(list((RUN / 'baseline').glob('case-*/result.json'))),
                       'available_ram_bytes': psutil.virtual_memory().available})
        raise
    finally:
        LOCK.unlink()


if __name__ == '__main__':
    main()
