"""Small, fully local lexical retrieval service for normalized knowledge."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from math import log
from pathlib import Path
import re

from outwise.knowledge.loader import load_knowledge_items
from outwise.knowledge.models import KnowledgeItem, RetrievedKnowledgeItem


_TOKEN_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)
_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "by",
    "can",
    "do",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "outdoor",
    "outdoors",
    "should",
    "the",
    "to",
    "what",
    "when",
    "with",
    "without",
}


class RetrievalService:
    """Rank normalized knowledge with a deterministic BM25-style score.

    The service intentionally knows nothing about source file formats, the LLM,
    or the UI. Each result wraps the original immutable ``KnowledgeItem``, so no
    provenance or source metadata is reconstructed during retrieval.
    """

    def __init__(self, items: Iterable[KnowledgeItem]) -> None:
        self._items = tuple(items)
        self._term_frequencies = tuple(
            Counter(_searchable_tokens(item)) for item in self._items
        )
        self._document_lengths = tuple(
            sum(term_frequencies.values())
            for term_frequencies in self._term_frequencies
        )
        self._average_document_length = (
            sum(self._document_lengths) / len(self._document_lengths)
            if self._document_lengths
            else 0.0
        )
        self._document_frequencies = Counter(
            token
            for term_frequencies in self._term_frequencies
            for token in term_frequencies
        )

    @classmethod
    def from_json(cls, path: str | Path) -> RetrievalService:
        """Build a retriever from the normalized versioned JSON contract."""

        return cls(load_knowledge_items(path))

    def retrieve(self, query: str, *, top_k: int = 3) -> list[RetrievedKnowledgeItem]:
        """Return up to ``top_k`` positive-scoring results in stable rank order.

        Blank queries and non-positive ``top_k`` values are caller errors. A
        valid query with no term overlap returns an empty list rather than
        pretending that an unrelated item is relevant.
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")

        query_terms = Counter(_tokenize(query))
        if not query_terms or not self._items:
            return []

        ranked: list[RetrievedKnowledgeItem] = []
        for item, frequencies, document_length in zip(
            self._items, self._term_frequencies, self._document_lengths, strict=True
        ):
            score = self._score(query_terms, frequencies, document_length)
            if score > 0:
                ranked.append(RetrievedKnowledgeItem(item=item, score=score))

        ranked.sort(key=lambda result: (-result.score, result.item.id))
        return ranked[:top_k]

    def _score(
        self,
        query_terms: Counter[str],
        document_terms: Counter[str],
        document_length: int,
    ) -> float:
        if self._average_document_length == 0:
            return 0.0

        score = 0.0
        document_count = len(self._items)
        k1 = 1.2
        length_normalization = 0.75
        for term, query_frequency in query_terms.items():
            term_frequency = document_terms.get(term, 0)
            if term_frequency == 0:
                continue
            document_frequency = self._document_frequencies[term]
            inverse_document_frequency = log(
                1 + (document_count - document_frequency + 0.5)
                / (document_frequency + 0.5)
            )
            denominator = term_frequency + k1 * (
                1
                - length_normalization
                + length_normalization
                * document_length
                / self._average_document_length
            )
            score += (
                inverse_document_frequency
                * term_frequency
                * (k1 + 1)
                / denominator
                * query_frequency
            )
        return score


def _searchable_tokens(item: KnowledgeItem) -> list[str]:
    return _tokenize(
        " ".join(
            value
            for value in (item.title, item.topic, item.section, item.text)
            if value
        )
    )


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in _TOKEN_PATTERN.findall(text.casefold())
        if token not in _STOP_WORDS
    ]
