"""Portable version of the measured MiniLM full-body window index.

This module has no dependency on evaluation cases, scores or private run paths.
The original index remains available for historical reproduction.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
from threading import Lock

import numpy as np

from outwise.knowledge.embeddings import KnowledgeAssetsError, LocalEmbedder, MODEL_DIRECTORY
from outwise.knowledge.ingestion import DEFAULT_LOCAL, digest, write_json
from outwise.knowledge.loader import load_knowledge_items
from outwise.services.semantic_retrieval import SemanticRetrievalService


def normalized(values):
    values = np.asarray(values, dtype=np.float32)
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if not np.isfinite(values).all() or (norms <= 0).any():
        raise KnowledgeAssetsError("Invalid window embeddings")
    return values / norms


def embedding_views(items, tokenizer, width=96, header_tokens=24):
    inputs, groups = [], []
    for item in items:
        header = f'{item["title"]}. {item.get("section") or ""}. '
        encoding = tokenizer.encode(header, add_special_tokens=False)
        if len(encoding.ids) > header_tokens:
            header = header[:encoding.offsets[header_tokens][0]].rstrip() + '. '
        body = item['text']
        encoding = tokenizer.encode(body, add_special_tokens=False)
        boundaries = [0]
        for offset in range(width, len(encoding.ids), width):
            boundary = encoding.offsets[offset][0]
            if boundary > boundaries[-1]:
                boundaries.append(boundary)
        boundaries.append(len(body))
        windows = [(body[a:b], len(tokenizer.encode(body[a:b], add_special_tokens=False).ids) or 1)
                   for a, b in zip(boundaries, boundaries[1:])]
        for contextual in (True, False):
            indices, weights = [], []
            for text, weight in windows:
                value = header + text if contextual else text
                if len(tokenizer.encode(value).ids) > 128:
                    raise KnowledgeAssetsError("Embedding window would be truncated")
                indices.append(len(inputs)); weights.append(weight); inputs.append(value)
            groups.append({'indices': indices, 'weights': weights})
    return inputs, groups


def build_index(local: Path):
    from tokenizers import Tokenizer

    items = load_knowledge_items(local / 'knowledge.json')
    embedder = LocalEmbedder(local / MODEL_DIRECTORY)
    tokenizer = Tokenizer.from_str(embedder._model.model.tokenizer.to_str())
    tokenizer.no_truncation(); tokenizer.no_padding()
    inputs, groups = embedding_views([asdict(item) for item in items], tokenizer)
    vectors = embedder.embed(inputs)
    views = normalized([np.average(vectors[g['indices']], axis=0, weights=g['weights']) for g in groups])
    vectors = normalized((views[0::2] + views[1::2]) / 2)
    path = local / 'prototype-embeddings.npy'
    temporary = local / 'prototype-embeddings.tmp.npy'
    np.save(temporary, vectors, allow_pickle=False)
    temporary.replace(path)
    write_json(local / 'prototype-index.json', index_metadata(local, items, embedder.lock, path))
    print(f'Prototype index: {len(items)} chunks, full-body windows, no source text changed.')


def index_metadata(local, items, model_lock, vector_path):
    return {'format': 'minilm-window96-header24-v1',
            'knowledge_sha256': digest((local / 'knowledge.json').read_bytes()),
            'vectors_sha256': digest(vector_path.read_bytes()),
            'item_ids': [item.id for item in items], 'model_lock': model_lock}


class WindowRetriever:
    def __init__(self, knowledge: Path):
        self.path = knowledge
        self.service = None
        self.lock = Lock()

    def retrieve(self, query, *, top_k=16):
        with self.lock:
            if self.service is None:
                try:
                    local = self.path.parent
                    record = json.loads((local / 'prototype-index.json').read_text(encoding='utf-8'))
                    path = local / 'prototype-embeddings.npy'
                    items = load_knowledge_items(self.path)
                    if (record['format'] != 'minilm-window96-header24-v1'
                            or record['knowledge_sha256'] != digest(self.path.read_bytes())
                            or record['vectors_sha256'] != digest(path.read_bytes())
                            or record['item_ids'] != [item.id for item in items]):
                        raise KnowledgeAssetsError('Prototype index does not match local knowledge')
                    embedder = LocalEmbedder(local / MODEL_DIRECTORY)
                    if record['model_lock'] != embedder.lock:
                        raise KnowledgeAssetsError('Prototype embedding model changed')
                    self.service = SemanticRetrievalService(items, np.load(path, allow_pickle=False),
                                                           embedder, min_score=float('-inf'))
                except (OSError, KeyError, ValueError) as exc:
                    raise KnowledgeAssetsError('Prototype index missing or invalid. Run knowledge setup.') from exc
            return self.service.retrieve(query, top_k=top_k)

    @property
    def items(self):
        return self.service._items if self.service else []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local', type=Path, default=DEFAULT_LOCAL)
    build_index(parser.parse_args().local)
