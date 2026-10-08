"""Offline semantic search with provenance integrity and jurisdiction filtering."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Protocol

import numpy as np

from outwise.knowledge.embeddings import KnowledgeAssetsError, LocalEmbedder, MODEL_NAME, MODEL_DIRECTORY
from outwise.knowledge.ingestion import digest
from outwise.knowledge.loader import load_knowledge_items
from outwise.knowledge.models import KnowledgeItem, RetrievedKnowledgeItem


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray: ...


def allowed_in_jurisdiction(item: KnowledgeItem, jurisdiction: str) -> bool:
    metadata = item.metadata
    if metadata.get("validity_type") == "dynamic_do_not_cache":
        return False
    if metadata.get("is_location_specific") is False:
        return metadata.get("jurisdiction") == "general"
    return metadata.get("is_location_specific") is True and metadata.get("jurisdiction") == jurisdiction


class SemanticRetrievalService:
    def __init__(self, items: list[KnowledgeItem], vectors: np.ndarray, embedder: Embedder,
                 *, jurisdiction: str = "NO", min_score: float = 0.35):
        vectors = np.asarray(vectors, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[0] != len(items) or not np.isfinite(vectors).all():
            raise KnowledgeAssetsError("Invalid embedding index")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        if (norms <= 0).any():
            raise KnowledgeAssetsError("Zero embedding vector")
        self._items, self._vectors = items, vectors / norms
        self._embedder, self._jurisdiction, self._min_score = embedder, jurisdiction, min_score

    @classmethod
    def from_json(cls, knowledge: Path) -> SemanticRetrievalService:
        directory = knowledge.parent
        try:
            index = json.loads((directory / "index.json").read_text(encoding="utf-8"))
            if (index["schema_version"] != 1 or index["model_name"] != MODEL_NAME
                    or index["embedding_format"] != "text-context-mean-v1"):
                raise KnowledgeAssetsError("Unexpected embedding index version/model")
            if digest(knowledge.read_bytes()) != index["knowledge_sha256"]:
                raise KnowledgeAssetsError("Knowledge changed; rebuild its embeddings")
            vector_path = directory / "embeddings.npy"
            if digest(vector_path.read_bytes()) != index["embeddings_sha256"]:
                raise KnowledgeAssetsError("Embedding index hash mismatch")
            items = load_knowledge_items(knowledge)
            if [item.id for item in items] != index["item_ids"]:
                raise KnowledgeAssetsError("Embedding index does not match knowledge IDs")
            vectors = np.load(vector_path, allow_pickle=False)
            if vectors.shape != (len(items), index["dimensions"]):
                raise KnowledgeAssetsError("Embedding dimensions mismatch")
            embedder = LocalEmbedder(directory / MODEL_DIRECTORY)
            if embedder.lock["revision"] != index["model_revision"] or embedder.lock["files"] != index["model_files"]:
                raise KnowledgeAssetsError("Embedding model changed; rebuild index")
            return cls(items, vectors, embedder)
        except (OSError, KeyError, ValueError) as exc:
            raise KnowledgeAssetsError("Den lokale kunnskapsbasen mangler eller er ugyldig. Kjør scripts/setup-knowledge.ps1.") from exc

    def retrieve(self, query: str, *, top_k: int = 3) -> list[RetrievedKnowledgeItem]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        query_vector = self._embedder.embed([query])[0]
        scores = self._vectors @ query_vector
        ranked = [RetrievedKnowledgeItem(item=item, score=float(score))
                  for item, score in zip(self._items, scores, strict=True)
                  if score >= self._min_score and allowed_in_jurisdiction(item, self._jurisdiction)]
        ranked.sort(key=lambda result: (-result.score, result.item.id))
        return ranked[:top_k]


class LocalKnowledgeRetriever:
    """Load local assets on first request; missing assets never fall back to fixtures."""

    def __init__(self, path: Path):
        self._path = path
        self._service: SemanticRetrievalService | None = None
        self._lock = Lock()

    def retrieve(self, query: str, *, top_k: int = 3) -> list[RetrievedKnowledgeItem]:
        with self._lock:
            if self._service is None:
                self._service = SemanticRetrievalService.from_json(self._path)
            return self._service.retrieve(query, top_k=top_k)
