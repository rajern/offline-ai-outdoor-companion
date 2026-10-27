"""Integration parity with saved development inputs; no new scoring or generation.

Requires the original private evidence. It never accesses the holdout set.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')

from outwise.knowledge.window_index import WindowRetriever, embedding_views
from outwise.services.context import pack_context
from outwise.services.native_model import NativeModelService, SYSTEM_PROMPT, user_message
from dataclasses import asdict

LOCAL = ROOT / 'knowledge/local'
OLD = LOCAL / 'diagnostics/retrieval-targeted-v1-2026-10-10'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def count(text):
    key = hashlib.sha256(text.encode('utf-8')).hexdigest()
    for base in (LOCAL/'diagnostics/retrieval-optimization-v1-2026-10-08/experiment', OLD, OLD/'revision-02'):
        folder = base/'tokenization'/key
        if (folder/'count.json').is_file():
            record = read(folder/'count.json')
            assert (folder/'input.txt').read_text(encoding='utf-8') == text
            assert hashlib.sha256((folder/'stdout.txt').read_bytes()).hexdigest() == record['stdout_sha256']
            assert len(read(folder/'stdout.txt')) == record['tokens']
            return record['tokens']
    raise ValueError('Missing frozen token count: ' + key)


def main():
    from tokenizers import Tokenizer
    # Block outbound Python sockets while still allowing the owned localhost runtime.
    original = socket.socket.connect
    def local_only(self, address):
        if not isinstance(address, tuple) or address[0] not in ('127.0.0.1', '::1'):
            raise PermissionError('Integration check permits numeric loopback only')
        return original(self, address)
    socket.socket.connect = local_only
    rows = read(OLD/'revision-02/configurations/T-ranking/retrieved-all.json')
    retriever = WindowRetriever(LOCAL/'knowledge.json')
    checked = []
    for row in rows:
        # The application exposes the original Norway/general scope only.
        # Case22 explicitly used NZ in the experiment; do not pretend it is the same input.
        if row['case_id'] == 'case-22':
            continue
        seeds = retriever.retrieve(row['question'], top_k=16)
        assert [r.item.id for r in seeds] == [r['item']['id'] for r in row['seeds']], row['case_id']
        packed = pack_context(row['question'], seeds, retriever.items, count)
        assert [asdict(r.item) for r in packed] == [r['item'] for r in row['excerpts']], row['case_id']
        checked.append(row['case_id'])
    tokenizer = Tokenizer.from_str(retriever.service._embedder._model.model.tokenizer.to_str())
    tokenizer.no_truncation(); tokenizer.no_padding()
    inputs, groups = embedding_views([asdict(item) for item in retriever.items], tokenizer)
    old = read(OLD/'revision-02/index/window-inputs.json')
    assert inputs == old['inputs']
    assert [(g['indices'],g['weights']) for g in groups] == [(g['indices'],g['weights']) for g in old['groups']]
    assert SYSTEM_PROMPT == (ROOT/'evals/local_generation_prompt.v1.md').read_text(encoding='utf-8').strip()
    # Check exact native role serialization against the saved baseline, without generating.
    model = NativeModelService()
    try:
        model.start()
        reference = LOCAL/'diagnostics/local-generation-eligible-2026-10-24/preflight/qwen-2b/inputs/case-23.json'
        if not reference.exists():
            raise ValueError('Native reference input not found: ' + str(reference))
        row = next(r for r in rows if r['case_id'] == 'case-23')
        from outwise.knowledge.models import KnowledgeItem, RetrievedKnowledgeItem
        packed = [RetrievedKnowledgeItem(KnowledgeItem(**r['item']), r['score']) for r in row['excerpts']]
        native = model.request('/apply-template', {'messages': [
            {'role':'system','content':SYSTEM_PROMPT}, {'role':'user','content':user_message(row['question'], packed)}]})['prompt']
        tokens = model.request('/tokenize', {'content':native,'add_special':False,'parse_special':True})['tokens']
        previous = read(reference)
        assert native == previous['prompt']
        assert tokens == previous['tokens']
        assert len(tokens) <= 3200
        # Independently exercise the tokenizer used by live P3 packing once.
        from outwise.services.orchestrator import _build_grounded_prompt
        text = _build_grounded_prompt(row['question'], packed)
        assert model.count(text) == count(text)
    finally:
        model.close()
    result = {'cases':len(checked),'case_ids':checked,'seed_and_packed_context_parity':True,
              'not_compared':{'case-22':'Experiment used NZ jurisdiction; application is fixed to NO/general'},
              'window_input_parity':True,'native_template_and_token_parity':True,
              'new_generation_calls':0,'new_judge_calls':0,'python_network':'numeric loopback only',
              'physical_offline_test':'pending owner review'}
    target = LOCAL/'app/integration-parity.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
