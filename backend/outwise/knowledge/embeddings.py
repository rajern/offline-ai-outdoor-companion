"""CPU embeddings and a small NumPy index; model downloads are setup-only."""

from __future__ import annotations

import argparse
from importlib.metadata import version
import json
from pathlib import Path

import numpy as np

from outwise.knowledge.ingestion import DEFAULT_LOCAL, digest, write_json
from outwise.knowledge.loader import load_knowledge_items


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_REPOSITORY = "qdrant/paraphrase-multilingual-MiniLM-L12-v2-onnx-Q"
MODEL_REVISION = "faf4aa4225822f3bc6376869cb1164e8e3feedd0"
MODEL_DIRECTORY = "embedding-model"
MODEL_FILES = ["model_optimized.onnx", "config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"]


class KnowledgeAssetsError(ValueError):
    """Missing or mismatched offline knowledge assets."""


def setup_embedding_model(local: Path) -> None:
    from huggingface_hub import snapshot_download

    directory = local / MODEL_DIRECTORY
    lock = directory / "outwise-model.json"
    if lock.exists():
        LocalEmbedder(directory)  # Validate existing frozen model, never refresh implicitly.
        return
    revision = MODEL_REVISION
    snapshot_download(MODEL_REPOSITORY, revision=revision, local_dir=directory,
                      allow_patterns=MODEL_FILES + ["README.md", "LICENSE*"])
    hashes = {name: digest((directory / name).read_bytes()) for name in MODEL_FILES}
    write_json(lock, {"model_name": MODEL_NAME, "repository": MODEL_REPOSITORY,
                     "revision": revision, "license": "Apache-2.0", "files": hashes})


class LocalEmbedder:
    def __init__(self, directory: Path):
        from fastembed import TextEmbedding

        try:
            self.lock = json.loads((directory / "outwise-model.json").read_text(encoding="utf-8"))
            if self.lock["model_name"] != MODEL_NAME or self.lock["revision"] != MODEL_REVISION:
                raise KnowledgeAssetsError("Unexpected embedding model")
            for name in MODEL_FILES:
                if digest((directory / name).read_bytes()) != self.lock["files"][name]:
                    raise KnowledgeAssetsError(f"Corrupt embedding asset: {name}")
            self._model = TextEmbedding(model_name=MODEL_NAME, specific_model_path=str(directory),
                                        local_files_only=True, threads=4, providers=["CPUExecutionProvider"])
        except (OSError, KeyError, ValueError) as exc:
            raise KnowledgeAssetsError("Den lokale søkemodellen mangler eller er ugyldig. Kjør kunnskapsoppsettet.") from exc

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.asarray(list(self._model.embed(texts, batch_size=16)), dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        if not np.isfinite(vectors).all() or (norms <= 0).any():
            raise KnowledgeAssetsError("Invalid embedding vectors")
        return vectors / norms


def build_index(knowledge: Path, local: Path) -> None:
    items = load_knowledge_items(knowledge)
    if not items:
        raise KnowledgeAssetsError("Cannot index empty knowledge")
    embedder = LocalEmbedder(local / MODEL_DIRECTORY)
    # Titles provide context, but must not dominate cross-language content matches.
    context_vectors = embedder.embed([f"{item.title}. {item.section or ''}. {item.text}" for item in items])
    text_vectors = embedder.embed([item.text for item in items])
    vectors = (context_vectors + text_vectors) / 2
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    index_path = local / "embeddings.npy"
    temp_path = local / "embeddings.candidate.npy"
    np.save(temp_path, vectors, allow_pickle=False)
    temp_path.replace(index_path)
    write_json(local / "index.json", {"schema_version": 1, "model_name": MODEL_NAME,
               "model_revision": embedder.lock["revision"], "model_files": embedder.lock["files"],
               "fastembed_version": version("fastembed"), "knowledge_sha256": digest(knowledge.read_bytes()),
               "embeddings_sha256": digest(index_path.read_bytes()), "item_ids": [item.id for item in items],
               "dimensions": int(vectors.shape[1]), "embedding_format": "text-context-mean-v1"})
    print(f"Indexed {len(items)} chunks ({vectors.shape[1]} dimensions)", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path, default=DEFAULT_LOCAL)
    parser.add_argument("--setup-model", action="store_true", help="Download the embedding model once")
    args = parser.parse_args()
    if args.setup_model:
        setup_embedding_model(args.local)
    build_index(args.local / "knowledge.json", args.local)


if __name__ == "__main__":
    main()
