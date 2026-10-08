"""Read-only production diagnosis. Raw source/answer artifacts stay Git-ignored.

Run from backend with its venv:
python ../evals/diagnose_m2_06.py --phase retrieval
python ../evals/diagnose_m2_06.py --phase gold
No ingestion, index rebuild, model download or production mutation occurs.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import time

import numpy as np
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from outwise.knowledge.ingestion import digest, write_json
from outwise.knowledge.models import RetrievedKnowledgeItem
from outwise.services.model import ModelService, ProcessResult, SubprocessRunner
from outwise.services.orchestrator import _build_grounded_prompt
from outwise.services.semantic_retrieval import SemanticRetrievalService, allowed_in_jurisdiction


def protected_files() -> list[Path]:
    roots = [ROOT / "backend/outwise", ROOT / "frontend", ROOT / "docs", ROOT / "scripts", ROOT / "knowledge/manifests"]
    paths = [ROOT / "AGENTS.md", ROOT / "TASKS.md", ROOT / "README.md", ROOT / ".gitignore", ROOT / "backend/pyproject.toml"]
    for directory in roots:
        paths.extend(p for p in directory.rglob("*") if p.is_file()
                     and not any(part in {"node_modules", "__pycache__", ".expo", "dist"} for part in p.parts))
    paths.extend(ROOT / "knowledge/local" / name for name in ["knowledge.json", "index.json", "embeddings.npy", "build.json", "snapshots.json", "embedding-model/outwise-model.json"])
    return sorted(set(paths))


def fingerprint() -> dict[str, str]:
    return {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p.read_bytes()) for p in protected_files()}


def no_network(*args, **kwargs):
    raise AssertionError("Python network connection forbidden during diagnostic")


class RecordingRunner(SubprocessRunner):
    def __init__(self, directory: Path, seed: int):
        self.directory, self.seed = directory, seed

    def run(self, command, timeout_seconds):
        actual = [*command, "--seed", str(self.seed)]
        write_json(self.directory / "command.json", {"argv": actual, "timeout_seconds": timeout_seconds})
        started = time.monotonic()
        try:
            result = super().run(actual, timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            write_json(self.directory / "process.json", {"elapsed_seconds": time.monotonic() - started, "timeout": True})
            for name, value in [("stdout.txt", exc.stdout), ("stderr.txt", exc.stderr)]:
                data = value or b""
                (self.directory / name).write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
            raise
        (self.directory / "stdout.txt").write_text(result.stdout, encoding="utf-8")
        (self.directory / "stderr.txt").write_text(result.stderr, encoding="utf-8")
        write_json(self.directory / "process.json", {"returncode": result.returncode, "elapsed_seconds": time.monotonic() - started})
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["retrieval", "gold"], required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "knowledge/local/diagnostics/m2-06-2026-10-07")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--case", action="append", dest="selected")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    socket.socket.connect = no_network
    socket.create_connection = no_network
    config = ROOT / "evals/m2-06-diagnostic-cases.json"
    cases = json.loads(config.read_text(encoding="utf-8"))["cases"]
    if args.selected:
        unknown = set(args.selected) - {c["id"] for c in cases}
        if unknown:
            raise ValueError(f"Unknown cases: {unknown}")
        cases = [c for c in cases if c["id"] in args.selected]
    args.output.mkdir(parents=True, exist_ok=True)
    baseline_path = args.output / "protected-baseline.json"
    baseline = fingerprint()
    if baseline_path.exists():
        if json.loads(baseline_path.read_text(encoding="utf-8")) != baseline:
            raise ValueError("Protected production inputs changed since diagnostic preparation")
    else:
        write_json(baseline_path, baseline)
        for name in ["knowledge.json", "index.json", "build.json", "snapshots.json"]:
            shutil.copyfile(ROOT / "knowledge/local" / name, args.output / name)
        shutil.copyfile(ROOT / "knowledge/manifests/approved-sources.json", args.output / "approved-sources.json")
        shutil.copyfile(config, args.output / config.name)
        shutil.copyfile(Path(__file__), args.output / Path(__file__).name)
        for path in protected_files():
            if path.suffix in {".py", ".json"} and "knowledge/local" not in path.as_posix():
                target = args.output / "code-snapshot" / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        model = ModelService()
        runtime = model._resolve_runtime()
        model_hash = __import__("hashlib").file_digest(model.settings.model_path.open("rb"), "sha256").hexdigest()
        runtime_version = subprocess.run([*runtime, "--version"], capture_output=True, encoding="utf-8", errors="replace")
        write_json(args.output / "environment.json", {"utc_started": datetime.now(timezone.utc).isoformat(),
                   "python": sys.version, "platform": platform.platform(), "model_path": str(model.settings.model_path),
                   "model_sha256": model_hash, "runtime": runtime, "runtime_version_stdout": runtime_version.stdout,
                   "runtime_version_stderr": runtime_version.stderr,
                   "packages": {p: version(p) for p in ["fastembed", "onnxruntime", "numpy", "tokenizers"]},
                   "production_sampling": {"temperature": 0.2, "top_p": 0.8, "top_k": 20, "max_tokens": 256, "context_size": 4096, "reasoning": "off"},
                   "diagnostic_override": "fixed seed only; English controls replace requested answer-language clause; no model/context/runtime switch",
                   "network_check": "Python connections denied, not OS-wide network isolation"})
    service = SemanticRetrievalService.from_json(ROOT / "knowledge/local/knowledge.json")
    items = {item.id: item for item in service._items}
    if args.phase == "retrieval":
        tokenizer = Tokenizer.from_file(str(ROOT / "knowledge/local/embedding-model/tokenizer.json"))
        tokenizer.no_truncation()
        tokenizer.no_padding()
        token_limit = service._embedder._model.model.tokenizer.truncation
        token_lengths = {}
        for item in service._items:
            text = f"{item.title}. {item.section or ''}. {item.text}"
            token_lengths[item.id] = {"text_tokens": len(tokenizer.encode(item.text).ids), "context_view_tokens": len(tokenizer.encode(text).ids)}
        write_json(args.output / "embedding-token-lengths.json", {"runtime_truncation": token_limit, "items": token_lengths})
        rows = []
        for case in cases:
            results = service.retrieve(case["question"], top_k=5)
            query_vector = service._embedder.embed([case["question"]])[0]
            scores = service._vectors @ query_vector
            all_ranked = sorted(zip(service._items, scores, strict=True), key=lambda pair: (-float(pair[1]), pair[0].id))
            ranking = []
            eligible_rank = 0
            for rank, (item, score) in enumerate(all_ranked, start=1):
                allowed = allowed_in_jurisdiction(item, "NO")
                eligible_rank += int(allowed)
                ranking.append({"id": item.id, "document_id": item.document_id, "section": item.section,
                                "source_name": item.source_name, "source_url": item.source_url, "score": float(score),
                                "rank_unfiltered": rank, "eligible_rank": eligible_rank if allowed else None,
                                "allowed_in_NO": allowed, "above_threshold": bool(score >= 0.35),
                                "jurisdiction": item.metadata.get("jurisdiction")})
            actual_ids = [r.item.id for r in results]
            expected_ids = [r["id"] for r in ranking if r["allowed_in_NO"] and r["above_threshold"]][:5]
            assert actual_ids == expected_ids
            row = {**case, "top5": [{"rank": k, "score": r.score, "item": asdict(r.item)} for k, r in enumerate(results, 1)],
                   "gold": [asdict(items[i]) for i in case["gold_ids"]],
                   "gold_ranking": [r for r in ranking if r["id"] in case["gold_ids"]], "all_ranking": ranking}
            rows.append(row)
            print(case["id"], [(r.item.id, round(r.score, 4)) for r in results], "gold", [(r["id"], r["eligible_rank"], round(r["score"], 4)) for r in row["gold_ranking"]], flush=True)
        write_json(args.output / "retrieval.json", {"production_top_k": 3, "diagnostic_top_k": 5, "min_score": 0.35, "cases": rows})
    else:
        for case in cases:
            directory = args.output / "gold" / case["id"] / f"seed-{args.seed}"
            if (directory / "result.json").exists():
                print("Already recorded:", case["id"], args.seed, flush=True)
                continue
            directory.mkdir(parents=True, exist_ok=True)
            context = [RetrievedKnowledgeItem(items[i], 1.0) for i in case["gold_ids"]]
            prompt = _build_grounded_prompt(case["question"], context)
            if case["language"] == "en":
                prompt = prompt.replace("Svar på norsk bokmål", "Svar på klart engelsk", 1)
            write_json(directory / "context.json", {"case": case, "items": [asdict(r.item) for r in context], "retrieval_bypassed": True})
            (directory / "prompt.txt").write_text(prompt, encoding="utf-8")
            print("Generating:", case["id"], "seed", args.seed, flush=True)
            model = ModelService(runner=RecordingRunner(directory, args.seed))
            try:
                answer = model.generate(prompt)
                result = {"case_id": case["id"], "seed": args.seed, "answer": answer, "status": "generated", "quality": "unreviewed"}
            except Exception as exc:
                result = {"case_id": case["id"], "seed": args.seed, "status": "error", "error_type": type(exc).__name__, "error": str(exc)}
            write_json(directory / "result.json", result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    after = fingerprint()
    write_json(args.output / f"integrity-{args.phase}-seed-{args.seed}.json", {"protected_files_unchanged": after == baseline, "hashes": after})
    assert after == baseline, "Diagnostic changed protected inputs"


if __name__ == "__main__":
    main()
