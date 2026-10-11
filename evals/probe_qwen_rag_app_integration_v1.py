"""Four current-app integration probes; record prompts without Qwen inference."""
import asyncio
from pathlib import Path
from dataclasses import asdict
import qwen_system_windows_adapter_v1 as adapter
import run_qwen_rag_system_v1 as q
from optimization_resources import Resources
from outwise.services.orchestrator import knowledge_path_from_environment
from outwise.services.semantic_retrieval import LocalKnowledgeRetriever


class RecordingModel:
    def __init__(self):
        self.prompts = []
    def generate(self, prompt):
        self.prompts.append(prompt)
        return 'Integration probe only; no Qwen answer generated.'


class TraceRetriever:
    def __init__(self):
        self.real = LocalKnowledgeRetriever(knowledge_path_from_environment())
        self.results = []
    def retrieve(self, message, *, top_k=3):
        assert top_k == 3
        self.results = self.real.retrieve(message, top_k=top_k)
        return self.results


def main():
    adapter.install(); adapter.offline(); q.verify()
    from outwise.main import create_app
    target = q.RUN / 'current-app-integration-probe'
    model = RecordingModel(); retriever = TraceRetriever()
    app = create_app(model, retriever)
    counter = q.t.d.TokenCounter(target / 'tokenization')
    cases = {c['id']: c for c in q.t.s.load_development()['cases']}
    records = []
    with Resources() as resources:
        resources.check()
        for cid in ['case-01', 'case-15', 'case-22', 'case-25']:
            before = len(model.prompts)
            status, body = asyncio.run(q.api_answer(app, cases[cid]['question']))
            assert status == 200
            prompt = model.prompts[-1] if len(model.prompts) > before else None
            folder = target / cid; folder.mkdir(parents=True, exist_ok=True)
            if prompt:
                (folder / 'prompt-not-executed.txt').write_text(prompt, encoding='utf-8')
                token_count, key = counter.count(prompt)
            else:
                token_count, key = 0, None
            q.write_once(folder / 'retrieved.json', [asdict(r) for r in retriever.results])
            records.append({'case_id': cid, 'status':status,
                'stored_source_metadata': body['sources'],
                'passage_ids': [r.item.id for r in retriever.results],
                'generation_would_be_called': prompt is not None,
                'generation_calls_executed': 0, 'prompt_tokens_locked': token_count,
                'prompt_sha256':key,'current_top_k':3,'threshold':.35,
                'jurisdiction':retriever.real._service._jurisdiction,
                'expected_question_jurisdiction':cases[cid]['jurisdiction'],
                'corpus_gap':cases[cid]['expected_result']=='insufficient_coverage'})
            resources.check()
    q.write_once(target / 'results.json', {'records':records,'resources':resources.result()})
    resources.check(); q.verify()
    public = {'scope':'Current production defaults via API; no Qwen inference; not a retrieval optimization configuration',
              'code_sha256':q.sha(Path(__file__).resolve()),'records':records,
              'production_changed':False,'qwen_calls':0,'paid_api_calls':0}
    q.write_once(q.ROOT / 'evals/qwen_rag_app_integration.v1.json',public)
    for row in records:
        print(row['case_id'],row['passage_ids'],'would generate',row['generation_would_be_called'],
              'prompt tokens',row['prompt_tokens_locked'])


if __name__ == '__main__':
    adapter.install()
    with q.LOCK.open('x', encoding='utf-8') as handle:
        handle.write('Current-app probes, no generation')
    try:
        main()
    finally:
        q.LOCK.unlink()
