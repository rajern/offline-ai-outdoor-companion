"""Product boundaries: exact excerpts, failure visibility and native input limits."""
from dataclasses import replace
import asyncio

import httpx
import pytest

from outwise.knowledge.models import KnowledgeItem, RetrievedKnowledgeItem
from outwise.services.orchestrator import Orchestrator, _sources_from
from outwise.services.model import ModelGenerationError
from outwise.services.native_model import NativeModelService, SYSTEM_PROMPT
from outwise.main import create_app


def items():
    first = KnowledgeItem(id='a', text='Do this only if the condition holds.', title='Manual', source_name='Author',
        source_url='https://example.org/manual', license='CC0', language='en', document_id='doc', section='A / B',
        topic='B', metadata={'is_location_specific': False, 'jurisdiction': 'general'})
    return [first, replace(first, id='b', text='Keep the original warning and order.')]


def test_multiple_excerpts_from_one_source_survive_without_rewriting():
    rows = [RetrievedKnowledgeItem(item, 1.0) for item in items()]
    sources = _sources_from(rows)
    assert len(sources) == 1
    assert [(e.id, e.text) for e in sources[0].excerpts] == [(r.item.id, r.item.text) for r in rows]


def test_prototype_returns_sources_when_generation_fails():
    class Retriever:
        items = items()
        def retrieve(self, query, *, top_k):
            return [RetrievedKnowledgeItem(self.items[0], 1)]
    class Model:
        def count(self, text): return 100
        def generate(self, prompt): raise ModelGenerationError('failed')
    answer = Orchestrator(Retriever(), Model(), top_k=16, prototype=True).answer('Test')
    assert answer.generation_error
    assert [e.text for e in answer.sources[0].excerpts] == [item.text for item in items()]


def test_native_template_has_fixed_roles_and_rejects_over_budget_before_generation():
    model = NativeModelService()
    model.start = lambda: None
    requests = []
    def request(endpoint, payload=None, **kwargs):
        requests.append((endpoint, payload))
        if endpoint == '/apply-template': return {'prompt': 'native template'}
        if endpoint == '/tokenize': return {'tokens': list(range(3201))}
        raise AssertionError('Must not generate or truncate')
    model.request = request
    with pytest.raises(ModelGenerationError, match='budget'):
        model.generate('Exact user source blocks')
    assert requests[0][1]['messages'] == [{'role': 'system', 'content': SYSTEM_PROMPT},
                                        {'role': 'user', 'content': 'Exact user source blocks'}]
    assert len(requests) == 2


@pytest.mark.parametrize('missing', [True, False])
def test_packing_failure_is_not_mislabeled_as_missing_knowledge(missing):
    from outwise.services.model import ModelNotFoundError
    class Retriever:
        items = items()
        def retrieve(self, query, *, top_k):
            return [RetrievedKnowledgeItem(self.items[0], 1)]
    class Model:
        def count(self, text):
            if missing: raise ModelNotFoundError('missing')
            return 2001
        def generate(self, prompt): raise AssertionError('Must not generate')
    answer = Orchestrator(Retriever(), Model(), prototype=True).answer('Test')
    assert answer.context_notice and answer.generation_error
    assert answer.sources[0].excerpts[0].text == items()[0].text
    assert 'ingen relevant informasjon' not in answer.answer


def test_status_reports_missing_assets_without_loading_or_downloading(monkeypatch, tmp_path):
    monkeypatch.setenv('OUTWISE_KNOWLEDGE_PATH', str(tmp_path/'knowledge.json'))
    monkeypatch.setenv('OUTWISE_MODEL_PATH', str(tmp_path/'missing.gguf'))
    async def status():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app()), base_url='http://test') as client:
            return await client.get('/api/status')
    response = asyncio.run(status())
    assert response.status_code == 200
    assert not response.json()['assets_present']
    assert not response.json()['knowledge_present']
    assert not response.json()['model_present']
