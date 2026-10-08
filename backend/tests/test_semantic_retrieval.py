from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pytest

from outwise.knowledge.embeddings import KnowledgeAssetsError, MODEL_NAME
from outwise.knowledge.ingestion import digest, write_json
from outwise.knowledge.models import KnowledgeItem
from outwise.services.semantic_retrieval import SemanticRetrievalService


class FakeEmbedder:
    def embed(self, texts):
        return np.array([[1.0, 0.0]], dtype=np.float32)


def item(identifier, jurisdiction="general", location_specific=False):
    return KnowledgeItem(id=identifier, text="Synthetic test", title="Test", source_name="Stored source",
                         source_url="fixture://test/" + identifier, license="CC0-1.0", language="en", topic="test",
                         metadata={"jurisdiction": jurisdiction, "is_location_specific": location_specific,
                                   "validity_type": "evergreen"})


def test_norwegian_runtime_filters_nz_rules_and_us_numbers_before_ranking():
    items = [item("nz", "NZ", True), item("us", "US", True), item("no", "NO", True), item("general")]
    vectors = np.array([[1, 0], [1, 0], [0.95, 0.1], [0.9, 0.1]])
    results = SemanticRetrievalService(items, vectors, FakeEmbedder()).retrieve("Norwegian question")
    assert {r.item.id for r in results} == {"no", "general"}
    assert all(r.item.source_url.startswith("fixture://test/") for r in results)


def test_dynamic_or_unclassified_material_cannot_enter_runtime_context():
    dynamic = replace(item("dynamic"), metadata={"validity_type": "dynamic_do_not_cache"})
    unknown = replace(item("unknown"), metadata={})
    service = SemanticRetrievalService([dynamic, unknown], np.array([[1, 0], [1, 0]]), FakeEmbedder())
    assert service.retrieve("question") == []


def test_semantic_service_abstains_on_low_similarity():
    service = SemanticRetrievalService([item("unrelated")], np.array([[0, 1]]), FakeEmbedder())
    assert service.retrieve("unsupported question") == []


def test_semantic_index_rejects_missing_assets(tmp_path: Path):
    with pytest.raises(KnowledgeAssetsError, match="kunnskapsbasen"):
        SemanticRetrievalService.from_json(tmp_path / "knowledge.json")


def test_semantic_index_rejects_nan_vectors():
    with pytest.raises(KnowledgeAssetsError, match="Invalid embedding"):
        SemanticRetrievalService([item("invalid")], np.array([[float('nan'), 1]]), FakeEmbedder())


@pytest.mark.parametrize("changed_asset", ["knowledge", "vectors", "item_ids", "format"])
def test_prepared_index_rejects_changed_or_incompatible_assets(tmp_path, changed_asset):
    knowledge = tmp_path / "knowledge.json"
    write_json(knowledge, {"schema_version": 1, "items": [asdict(item("test"))]})
    vector_path = tmp_path / "embeddings.npy"
    np.save(vector_path, np.array([[1, 0]], dtype=np.float32), allow_pickle=False)
    index = {"schema_version": 1, "model_name": MODEL_NAME,
             "embedding_format": "text-context-mean-v1",
             "knowledge_sha256": digest(knowledge.read_bytes()),
             "embeddings_sha256": digest(vector_path.read_bytes()),
             "item_ids": ["test"], "dimensions": 2}
    if changed_asset == "knowledge":
        write_json(knowledge, {"schema_version": 1, "items": []})
    elif changed_asset == "vectors":
        np.save(vector_path, np.array([[0, 1]], dtype=np.float32), allow_pickle=False)
    elif changed_asset == "item_ids":
        index["item_ids"] = ["other"]
    else:
        index["embedding_format"] = "unknown-format"
    write_json(tmp_path / "index.json", index)
    with pytest.raises(KnowledgeAssetsError, match="kunnskapsbasen"):
        SemanticRetrievalService.from_json(knowledge)
