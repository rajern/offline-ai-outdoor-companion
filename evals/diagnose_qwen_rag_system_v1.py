"""Three bounded sufficient-context diagnoses after the unchanged baseline."""
import asyncio
from dataclasses import asdict
from pathlib import Path
import time

import qwen_system_windows_adapter_v1 as adapter
import run_qwen_rag_system_v1 as q
from optimization_resources import Resources
from outwise.knowledge.embeddings import LocalEmbedder
from outwise.services.model import ModelService, ModelSettings
from outwise.services.orchestrator import Orchestrator, _build_grounded_prompt

SELECTION = {
    'case-03': ['source-21-005', 'source-21-009', 'source-21-010'],
    'case-08': ['source-07-001', 'source-01-004', 'source-07-005', 'source-07-006', 'source-07-007'],
    'case-17': ['source-08-001', 'source-08-003', 'source-08-004'],
}


class SufficientRetriever:
    def __init__(self, question, results):
        self.question, self.results = question, results
    def retrieve(self, question, *, top_k=16):
        assert question == self.question and top_k == 16
        return self.results


def main():
    adapter.install(); adapter.offline()
    assert (q.RUN / 'complete.json').is_file(), 'Complete baseline first'
    frozen = q.verify()
    directory = q.RUN / 'diagnostic-sufficient-context'
    assert not (directory / 'stop.json').exists(), 'Retained diagnostic stop requires review'
    cases = {c['id']: c for c in q.t.s.load_development()['cases']}
    parents = {p['id']: q.t.d.KnowledgeItem(**p)
               for p in q.read(q.t.s.runtime.LOCAL / 'knowledge.json')['items']}
    counter = q.t.d.TokenCounter(directory / 'tokenization')
    prompts = {}; inputs = {}
    for cid, ids in SELECTION.items():
        results = [q.t.d.RetrievedKnowledgeItem(parents[i], 1.0) for i in ids]
        assert all(q.t.d.allowed_in_jurisdiction(r.item, cases[cid]['jurisdiction']) for r in results)
        prompt = _build_grounded_prompt(cases[cid]['question'], results)
        tokens, key = counter.count(prompt)
        assert tokens <= 2000
        prompts[cid] = prompt
        inputs[cid] = {'source_ids': ids, 'prompt_tokens': tokens, 'prompt_sha256': key,
                       'passage_hashes': {r.item.id: q.digest(asdict(r.item)) for r in results},
                       'manual_review': 'Sufficient for all unchanged must-have requirements; sources reviewed before inference',
                       'diagnostic_only': True}
    binding = {'baseline_freeze_sha256': q.sha(q.RUN / 'freeze.json'), 'inputs': inputs,
               'diagnostic_code_sha256': q.sha(Path(__file__).resolve()),
               'protocol_sha256': q.sha(q.PROTOCOL), 'limits_unchanged': True}
    q.write_once(directory / 'freeze.json', binding)
    # Keep retrieval model resident for the same simultaneous-RAM condition.
    with Resources() as startup:
        startup.check(); embedder = LocalEmbedder(q.t.s.runtime.LOCAL / 'embedding-model')
    q.write_once(directory / 'startup-resources.json', startup.result()); startup.check()
    from outwise.main import create_app
    settings = ModelSettings(model_path=Path(frozen['settings']['model_path']),
                             llama_cli_path=Path(frozen['settings']['llama_cli_path']))
    for cid, ids in SELECTION.items():
        folder = directory / cid
        key = q.digest({'system': frozen, 'diagnostic': binding, 'prompt': prompts[cid]})
        if (folder / 'result.json').exists():
            assert q.read(folder / 'result.json')['cache_key'] == key
            for name, expected in q.read(folder / 'seal.json').items():
                assert q.sha(folder / name) == expected
            print(cid, 'diagnostic cached', flush=True); continue
        assert not (folder / 'command.json').exists(), 'No automatic repetition of an unsealed call'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'prompt.txt').write_text(prompts[cid], encoding='utf-8')
        selected = [q.t.d.RetrievedKnowledgeItem(parents[i], 1.0) for i in ids]
        retriever = SufficientRetriever(cases[cid]['question'], selected)
        with Resources() as resources:
            resources.check()
            model = ModelService(settings, q.GuardedRunner(folder, resources))
            app = create_app(model, retriever)
            app.state.orchestrator = Orchestrator(retriever, model, top_k=16)
            start = time.perf_counter()
            status, body = asyncio.run(q.api_answer(app, cases[cid]['question']))
            elapsed = time.perf_counter() - start
        q.write_once(folder / 'api-response.json', {'status': status, 'body': body})
        resources.check(); assert status == 200
        (folder / 'answer.txt').write_text(body['answer'], encoding='utf-8')
        tokens, _ = counter.count(body['answer'])
        q.write_once(folder / 'result.json', {'case_id': cid, 'cache_key': key,
                    'diagnostic_only': True, 'input': inputs[cid], 'elapsed_seconds': elapsed,
                    'resources': resources.result(), 'answer_tokens_locked_tokenizer': tokens})
        names = ['prompt.txt', 'command.json', 'stdout.txt', 'stderr.txt', 'process.json',
                 'api-response.json', 'answer.txt', 'result.json']
        q.write_once(folder / 'seal.json', {name: q.sha(folder / name) for name in names})
        print(cid, f'diagnostic {elapsed:.2f}s / {tokens} answer tokens', flush=True)
    q.verify()
    q.write_once(directory / 'complete.json', {'diagnostic_calls': 3, 'new_judge_calls': 0})


if __name__ == '__main__':
    # Share the application-run lock; diagnostics cannot overlap a baseline.
    adapter.install()
    with q.LOCK.open('x', encoding='utf-8') as handle:
        handle.write('sufficient-context diagnostics')
    try:
        main()
    except BaseException as exc:
        q.write_once(q.RUN / 'diagnostic-sufficient-context/stop.json', {'error': str(exc)})
        raise
    finally:
        q.LOCK.unlink()
