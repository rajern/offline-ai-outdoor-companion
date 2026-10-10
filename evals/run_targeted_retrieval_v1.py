"""Three frozen targeted experiments, separate durable storage and sealed cache."""
from __future__ import annotations

import argparse
import ast
from dataclasses import asdict
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

import run_retrieval_optimization_v1 as d
import retrieval_optimization_scoring as s
import continue_retrieval_phase_c_v1 as c
from optimization_embeddings import MiniLM
from optimization_resources import Resources, input_accounting, validate_vectors
from optimization_report import consumption
import targeted_retrieval_methods as methods

PREVIOUS = s.runtime.LOCAL / 'diagnostics/retrieval-targeted-v1-2026-10-10'
RUN = PREVIOUS / 'revision-02'
CONFIG = s.ROOT / 'evals/retrieval_targeted.v2.json'
CODE = [Path(__file__), Path(methods.__file__), CONFIG,
        s.ROOT / 'evals/retrieval_targeted_plan.v2.md',
        s.ROOT / 'evals/test_targeted_retrieval_v1.py',
        s.ROOT / 'evals/test_targeted_headers_v1.py']


def write_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if s.runtime.read(path) != value:
            raise ValueError('Immutable record differs: ' + str(path))
    else:
        s.runtime.write(path, value)


def protected_prior():
    # Enumerate only the explicit old experiment, never the evals directory.
    return {str(p.relative_to(d.RUN)): d.file_hash(p)
            for p in (d.RUN / 'configurations').rglob('*') if p.is_file()}


def superseded_files():
    paths = [p for folder in ['configurations', 'index', 'tokenization', 'source-snapshot']
             for p in (PREVIOUS / folder).rglob('*') if p.is_file()]
    paths += [PREVIOUS / name for name in ['freeze.json', 'started.json', 'technical-correction.v1.json', 'quota-before.json']]
    return {str(p.relative_to(PREVIOUS)): d.file_hash(p) for p in paths}


def reuse_packing():
    old_text = (PREVIOUS / 'source-snapshot/evals/targeted_retrieval_methods.py').read_text(encoding='utf-8')
    new_text = Path(methods.__file__).read_text(encoding='utf-8')
    def functions(text):
        return {node.name: ast.get_source_segment(text, node) for node in ast.parse(text).body
                if isinstance(node, ast.FunctionDef)}
    old, new = functions(old_text), functions(new_text)
    for name in ['scope_key', 'instruction_unit', 'diverse_pack']:
        assert old[name] == new[name]
    source = PREVIOUS / 'configurations/T-packing'; target = RUN / 'configurations/T-packing'
    if not target.exists():
        target.parent.mkdir(exist_ok=True); shutil.copytree(source, target)
    hashes = {str(p.relative_to(source)): d.file_hash(p) for p in source.rglob('*') if p.is_file()}
    assert all(d.file_hash(target / name) == value for name, value in hashes.items())
    write_once(RUN / 'packing-reuse.json', {'source': str(source.relative_to(s.ROOT)),
        'files': hashes, 'method_sha256': {name: s.runtime.legacy.text_sha(new[name])
        for name in ['scope_key', 'instruction_unit', 'diverse_pack']},
        'judge_calls_repeated': 0, 'contexts_reused': 25})


class LoggedResources(Resources):
    """Retain samples even when a worker exits on a quota/review/RAM failure."""
    def __init__(self, directory):
        super().__init__(); self.directory = directory
    def __exit__(self, *args):
        try:
            super().__exit__(*args)
        finally:
            self.directory.mkdir(parents=True, exist_ok=True)
            number = len(list(self.directory.glob('attempt-*.json'))) + 1
            write_once(self.directory / f'attempt-{number:03}.json',
                {**self.result(), 'exception_type': args[0].__name__ if args[0] else None})


def freeze():
    d.verify(); c.check_frozen(); d.verify_rows('C-P3')
    if (RUN / 'freeze.json').exists():
        return verify()
    with Resources() as resource:
        resource.check()
    with s.runtime.JudgeLock():
        s.runtime.recover_active(); pre = s.runtime.preflight(); ident = s.identity(pre)
        if ident != s.runtime.read(d.RUN / 'freeze.json')['judge_identity']:
            raise ValueError('Validated subscription judge identity changed')
        row = d.verify_rows('C-P3')[0]
        case = s.load_development()['cases'][0]
        key = s.cache_key(s.judge_input(case, row), ident)
        if not (s.CACHE / key / 'result-seal.json').exists():
            raise ValueError('Expected sealed baseline input missing')
        cached = s.judge(s.judge_input(case, row), pre, ident)
        assert cached['cache_hit'] and cached['calls'] == 0
    config = s.runtime.read(CONFIG)
    assert [v['id'] for v in config['variants']] == ['T-ranking', 'T-packing', 'T-combined']
    superseded = s.runtime.read(PREVIOUS / 'freeze.json')
    assert superseded['config']['variants'] == config['variants']
    assert not list((PREVIOUS / 'configurations').glob('*/case-*/score.json'))
    for path, expected in superseded['code'].items():
        assert d.file_hash(PREVIOUS / 'source-snapshot' / path) == expected
    write_once(RUN / 'freeze.json', {
        'code': {str(p.relative_to(s.ROOT)): d.file_hash(p) for p in CODE},
        'original_freeze_sha256': d.file_hash(d.RUN / 'freeze.json'),
        'prior_files': protected_prior(), 'config': config, 'judge_identity': ident,
        'superseded_pre_scoring_files': superseded_files(),
        'baseline_summary_sha256': d.file_hash(d.RUN / 'configurations/C-P3/summary.json'),
        'resource_limits': {'ram_reserve': d.RAM_RESERVE, 'rss_limit': d.RSS_LIMIT},
        'preflight_new_judge_calls': 0, 'preflight_cache_checks': 1})
    write_once(RUN / 'started.json', {'at': s.runtime.now(),
        'existing_cache_keys': [p.name for p in s.CACHE.iterdir() if p.is_dir()]})
    reuse_packing()
    return verify()


def verify():
    d.verify(); c.check_frozen()
    value = s.runtime.read(RUN / 'freeze.json')
    for path, expected in value['code'].items():
        if d.file_hash(s.ROOT / path) != expected:
            raise ValueError('Targeted frozen code/config changed: ' + path)
    if d.file_hash(d.RUN / 'freeze.json') != value['original_freeze_sha256']:
        raise ValueError('Original freeze changed')
    if protected_prior() != value['prior_files']:
        raise ValueError('Original 31 experiment files changed')
    if superseded_files() != value['superseded_pre_scoring_files']:
        raise ValueError('Unjudged technical revision was not preserved')
    return value


def build_index():
    frozen = verify(); target = RUN / 'index'; target.mkdir(exist_ok=True)
    if (target / 'index.json').exists():
        return checked_index()
    items = s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']
    cases = s.load_development()['cases']; model = None
    started = time.perf_counter()
    with LoggedResources(target / 'resource-attempts') as resource:
        try:
            resource.check(); model = MiniLM(); resource.check()
            from tokenizers import Tokenizer
            tokenizer = Tokenizer.from_str(model.model._model.model.tokenizer.to_str())
            tokenizer.no_truncation(); tokenizer.no_padding()
            settings = frozen['config']['ranking']
            inputs, groups = methods.embedding_views(items, tokenizer,
                settings['window_body_tokens'], settings['header_tokens'])
            original = [len(tokenizer.encode(t).ids) for t in inputs]
            actual = [sum(e.attention_mask) for e in model.model._model.model.tokenizer.encode_batch(inputs)]
            if original != actual or max(original) > 128:
                raise ValueError('Window embedding inputs truncated')
            before = time.perf_counter(); chunks = []
            for i in range(0, len(inputs), 16):
                resource.check(); chunks.append(model.model.embed(inputs[i:i + 16])); resource.check()
            windows = np.concatenate(chunks); vectors = methods.parent_vectors(windows, groups)
            build_seconds = time.perf_counter() - before
            queries, latency = [], []
            accounting = input_accounting('minilm', model, [], [case['question'] for case in cases])
            if accounting['truncated_inputs']:
                raise ValueError('Query embedding truncated')
            for case in cases:
                resource.check(); before = time.perf_counter()
                queries.append(model.queries([case['question']])[0]); latency.append(time.perf_counter() - before)
                resource.check()
            queries = np.asarray(queries, dtype=np.float32)
            validate_vectors(vectors, queries, len(items), len(cases))
            old_queries = np.load(d.RUN / 'indices/minilm/queries.npy', allow_pickle=False)
            if not np.allclose(queries, old_queries, atol=1e-6, rtol=1e-6):
                raise ValueError('Fresh query embedding not comparable with frozen MiniLM')
            for name, array in [('documents', vectors), ('queries', queries), ('windows', windows)]:
                np.save(target / (name + '.npy'), array, allow_pickle=False)
            write_once(target / 'window-inputs.json', {'inputs': inputs, 'groups': groups})
            resource.check()
        finally:
            if model:
                model.close()
    resource.check()
    write_once(target / 'index.json', {
        'document_ids': [p['id'] for p in items], 'case_ids': [case['id'] for case in cases],
        'files': {name: d.file_hash(target / name) for name in
                  ['documents.npy', 'queries.npy', 'windows.npy', 'window-inputs.json']},
        'window_inputs': len(inputs), 'body_truncation': 0,
        'header_truncated_parents': sum(len(tokenizer.encode(f'{p["title"]}. {p.get("section") or ""}. ', add_special_tokens=False).ids) > 24 for p in items),
        'original_input_tokens': original, 'actual_input_tokens': actual,
        'query_accounting': accounting, 'query_embedding_seconds': latency,
        'query_vector_match': 'allclose atol=rtol=1e-6; original frozen ranking uses original query bytes',
        'build_seconds_warm': build_seconds, 'total_build_seconds': time.perf_counter() - started,
        'resources': resource.result(), 'model_identity': d.checked_index('minilm')['model_identity'],
        'model_size_bytes': d.checked_index('minilm')['model_size_bytes'],
        'parent_index_size_bytes': (target / 'documents.npy').stat().st_size,
        'window_index_size_bytes': (target / 'windows.npy').stat().st_size})
    print('Full-body window index and fresh query resource preflight passed', flush=True)


def checked_index():
    target = RUN / 'index'; meta = s.runtime.read(target / 'index.json')
    for name, expected in meta['files'].items():
        if d.file_hash(target / name) != expected:
            raise ValueError('New index changed')
    items = s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']
    cases = s.load_development()['cases']
    assert meta['document_ids'] == [p['id'] for p in items]
    assert meta['case_ids'] == [case['id'] for case in cases]
    validate_vectors(np.load(target / 'documents.npy'), np.load(target / 'queries.npy'), len(items), len(cases))
    return meta


def variant(cid):
    return next(v for v in verify()['config']['variants'] if v['id'] == cid)


def counter():
    # Read original cache where available; new inputs never write to original run.
    class Counter(d.TokenCounter):
        def count(self, text):
            key = s.runtime.legacy.text_sha(text)
            for cache in [d.RUN / 'tokenization', PREVIOUS / 'tokenization']:
                if (cache / key / 'count.json').exists():
                    return d.TokenCounter(cache).count(text)
            return super().count(text)
    return Counter(RUN / 'tokenization')


def retrieve(cid):
    config = variant(cid); checked_index(); target = RUN / 'configurations' / cid
    if (target / 'retrieved-all.json').exists():
        return verify_rows(cid)
    write_once(target / 'config.json', config)
    index = RUN / 'index' if config['ranking'] == 'window-mean' else d.RUN / 'indices/minilm'
    vectors = np.load(index / 'documents.npy'); queries = np.load(index / 'queries.npy')
    parents = [d.KnowledgeItem(**p) for p in s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']]
    rows = []; tokens = counter()
    with LoggedResources(target / 'retrieval-resource-attempts') as resource:
        resource.check()
        for i, case in enumerate(s.load_development()['cases']):
            folder = target / case['id']
            if (folder / 'retrieved.json').exists():
                rows.append(s.runtime.read(folder / 'retrieved.json')); continue
            started = time.perf_counter(); similarities = vectors @ queries[i]
            order = sorted([n for n, p in enumerate(parents) if d.allowed_in_jurisdiction(p, case['jurisdiction'])],
                           key=lambda n: (-float(similarities[n]), parents[n].id))
            seeds = [d.RetrievedKnowledgeItem(parents[n], float(similarities[n])) for n in order[:16]]
            assert len({r.item.id for r in seeds}) == 16
            ranking_seconds = time.perf_counter() - started
            if config['packing'] == 'P3':
                results, packets, trace = d.pack(case, seeds, parents, 'P3', tokens)
            else:
                results, packets, trace = methods.diverse_pack(case, seeds, parents, tokens)
            context = d.context_for(results); prompt = d._build_grounded_prompt(case['question'], results)
            pt, pk = tokens.count(prompt); ct, ck = tokens.count(context)
            if pt > 2000:
                raise ValueError('Complete prompt exceeds budget')
            row = {'configuration': cid, 'case_id': case['id'], 'question': case['question'],
                'corpus_hash': d.file_hash(s.runtime.LOCAL / 'knowledge.json'),
                'gold_hash': d.file_hash(s.ROOT / 'evals/retrieval_cases.v1.yaml'),
                'excerpts': [asdict(r) for r in results], 'seeds': [asdict(r) for r in seeds],
                'candidates_top16': [{'id': r.item.id, 'score': r.score} for r in seeds],
                'context_sha256': s.runtime.legacy.text_sha(context), 'prompt_sha256': s.runtime.legacy.text_sha(prompt),
                'context_tokens': ct, 'prompt_tokens': pt, 'context_budget': 2000,
                'prompt_tokenization_key': pk, 'context_tokenization_key': ck,
                'chunk_count': len(results), 'packet_count': len(packets), 'packets': packets, 'trace': trace,
                'budget_excluded_packets': sum(t['status'] == 'over_budget' for t in trace),
                'ranking_seconds': ranking_seconds, 'retrieval_and_packing_seconds': time.perf_counter() - started}
            folder.mkdir(exist_ok=True)
            (folder / 'context.txt').write_text(context, encoding='utf-8', newline='\n')
            (folder / 'prompt-not-executed.txt').write_text(prompt, encoding='utf-8', newline='\n')
            write_once(folder / 'retrieved.json', row); rows.append(row); resource.check()
    write_once(target / 'retrieval-resources.json', resource.result())
    resource.check(); write_once(target / 'retrieved-all.json', rows)
    verify_rows(cid); print(cid, '25 contexts verified', flush=True)


def verify_rows(cid):
    target = RUN / 'configurations' / cid; rows = s.runtime.read(target / 'retrieved-all.json')
    cases = s.load_development()['cases']
    parents = {p['id']: asdict(d.KnowledgeItem(**p)) for p in s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']}
    tokens = counter()
    assert [r['case_id'] for r in rows] == [case['id'] for case in cases]
    for case, row in zip(cases, rows):
        assert row == s.runtime.read(target / row['case_id'] / 'retrieved.json')
        results = []
        for excerpt in row['excerpts']:
            if parents.get(excerpt['item']['id']) != excerpt['item']:
                raise ValueError('Provenance/source changed')
            item = d.KnowledgeItem(**excerpt['item'])
            assert d.allowed_in_jurisdiction(item, case['jurisdiction'])
            results.append(d.RetrievedKnowledgeItem(item, excerpt['score']))
        for name, text, prefix in [('context.txt', d.context_for(results), 'context'),
                                  ('prompt-not-executed.txt', d._build_grounded_prompt(case['question'], results), 'prompt')]:
            assert text == (target / row['case_id'] / name).read_text(encoding='utf-8')
            assert s.runtime.legacy.text_sha(text) == row[prefix + '_sha256']
            assert tokens.count(text)[0] == row[prefix + '_tokens']
        assert row['prompt_tokens'] <= 2000
    return rows


def score(cid):
    frozen = verify(); target = RUN / 'configurations' / cid; rows = verify_rows(cid)
    cases = {case['id']: case for case in s.load_development()['cases']}
    corpus = s.runtime.read(s.runtime.LOCAL / 'knowledge.json')['items']
    with LoggedResources(target / 'judge-resource-attempts') as resource, s.runtime.JudgeLock():
        resource.check(); s.runtime.recover_active(); pre = s.runtime.preflight(); ident = s.identity(pre)
        assert ident == frozen['judge_identity']
        for row in rows:
            path = target / row['case_id'] / 'score.json'
            if path.exists():
                saved = s.runtime.read(path)
                assert saved['context_sha256'] == row['context_sha256']
                if saved['requires_review']:
                    raise RuntimeError('Saved review blocks automatic continuation')
                continue
            resource.check(); case = cases[row['case_id']]; payload = s.judge_input(case, row)
            context = '\n\n'.join(b['text'] for b in payload['blocks'])
            assert s.runtime.legacy.text_sha(context) == row['context_sha256']
            request = {'configuration': cid, 'case_id': row['case_id'], 'cache_key': s.cache_key(payload, ident)}
            with (RUN / 'judge-requests.jsonl').open('a', encoding='utf-8', newline='\n') as stream:
                stream.write(json.dumps(request) + '\n'); stream.flush(); os.fsync(stream.fileno())
            result = s.judge(payload, pre, ident)
            merged = s.merge(case, row, context, corpus, result['answer'], s.rules())
            write_once(path, {**merged, **{k: v for k, v in result.items() if k not in ['answer', 'record']},
                             'judge_result_sha256': s.digest(result['answer'])})
            print(cid, row['case_id'], 'cache=' + str(result['cache_hit']), 'review=' + str(merged['requires_review']), flush=True)
            if merged['requires_review']:
                raise RuntimeError('Source/judge/uncertain review stops inference')
            resource.check()
    write_once(target / 'judge-resources.json', resource.result()); resource.check()
    raw = [s.runtime.read(target / row['case_id'] / 'score.json') for row in rows]
    adjusted = [c.adjusted(r, s.runtime.read(c.LAYER))[0] for r in raw]
    write_once(target / 'summary.json', {'configuration': variant(cid), 'raw_scores': raw, 'scores': adjusted,
        'raw_full25': s.aggregate(raw), 'raw_legacy15': s.aggregate(raw, legacy_only=True),
        'full25': s.aggregate(adjusted), 'legacy15': s.aggregate(adjusted, legacy_only=True)})


def export(status, error=None):
    RUN.mkdir(parents=True, exist_ok=True)
    records = []
    for config in s.runtime.read(CONFIG)['variants']:
        target = RUN / 'configurations' / config['id']
        rows = [s.runtime.read(p) for p in sorted(target.glob('case-*/score.json'))]
        summary = s.runtime.read(target / 'summary.json') if (target / 'summary.json').exists() else None
        records.append({'configuration': config, 'judged_cases': len(rows), 'summary': summary,
            'partial_scores': rows, 'retrieved_cases': len(list(target.glob('case-*/retrieved.json')))})
    value = {'status': status, 'error': error, 'at': s.runtime.now(), 'configurations': records,
             'consumption': consumption(RUN), 'holdout_accessed': False,
             'production_changed': False, 'generation_calls': 0, 'paid_api_calls': 0}
    s.runtime.write(RUN / 'progress.json', value, replace=True)
    # Source-free public output: raw quoted judge/source text stays local.
    public = {**value, 'configurations': [{k: v for k, v in record.items() if k not in ['summary', 'partial_scores']}
              | ({'full25': record['summary']['full25'], 'legacy15': record['summary']['legacy15']} if record['summary'] else {})
              | {'decisions': [{k: row[k] for k in ['case_id', 'decisions', 'flags', 'requires_review', 'context_sha256', 'cache_key']}
                               for row in record['partial_scores']]} for record in records]}
    s.runtime.write(s.ROOT / 'evals/retrieval_targeted_results.v1.json', public, replace=True)


def worker(command, cid=None):
    logs = RUN / 'worker-logs'; logs.mkdir(exist_ok=True)
    label = command + ('-' + cid if cid else '')
    path = logs / (label + f'-{len(list(logs.glob(label + "-*.log"))) + 1:03}.log')
    argv = [sys.executable, str(Path(__file__)), command, '--worker']
    if cid:
        argv += ['--config-id', cid]
    with path.open('xb') as stream:
        result = subprocess.run(argv, stdout=stream, stderr=stream,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
    if result.returncode:
        raise RuntimeError('Worker failed; retained log: ' + str(path.relative_to(s.ROOT)))


def run():
    freeze(); worker('index')
    # Every technical retrieval check finishes before the first fresh judge call.
    for config in s.runtime.read(CONFIG)['variants']:
        worker('retrieve', config['id'])
    for config in s.runtime.read(CONFIG)['variants']:
        worker('score', config['id']); export('running')
    verify(); export('comparison_complete')


if __name__ == '__main__':
    s.holdout_guard()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'freeze', 'index', 'retrieve', 'score', 'verify'])
    parser.add_argument('--config-id', choices=['T-ranking', 'T-packing', 'T-combined'])
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    def dispatch():
        if args.command == 'run': run()
        elif args.command == 'freeze': freeze()
        elif args.command == 'index': build_index()
        elif args.command == 'retrieve': retrieve(args.config_id)
        elif args.command == 'score': score(args.config_id)
        else: verify()
    if args.worker:
        dispatch()
    else:
        with s.runtime.JudgeLock(d.EXPERIMENT_LOCK):
            try:
                dispatch()
            except Exception as error:
                export('blocked', str(error)); raise
