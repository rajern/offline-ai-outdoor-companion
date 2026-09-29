from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence

import pytest

from outwise.services.model import (
    ModelGenerationError,
    ModelLoadError,
    ModelNotFoundError,
    ModelRuntimeNotFoundError,
    ModelService,
    ModelSettings,
    ModelTimeoutError,
    ProcessResult,
)


class StubRunner:
    def __init__(
        self,
        result: ProcessResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.command: list[str] | None = None
        self.timeout_seconds: float | None = None

    def run(self, command: Sequence[str], timeout_seconds: float) -> ProcessResult:
        self.command = list(command)
        self.timeout_seconds = timeout_seconds
        if self.error:
            raise self.error
        assert self.result is not None
        return self.result


def settings(model_path: Path, runtime_path: Path, **overrides: object) -> ModelSettings:
    values: dict[str, object] = {
        "model_path": model_path,
        "llama_cli_path": runtime_path,
        "timeout_seconds": 12.0,
        "max_tokens": 42,
        "context_size": 2048,
    }
    values.update(overrides)
    return ModelSettings(**values)  # type: ignore[arg-type]


def existing_test_file() -> Path:
    return Path(__file__)


def test_generate_returns_stdout_and_builds_llama_command() -> None:
    model_path = existing_test_file()
    runtime_path = existing_test_file()
    runner = StubRunner(ProcessResult(0, "  Generated locally.\n", "runtime log"))
    service = ModelService(settings(model_path, runtime_path), runner)

    response = service.generate("How do I stay warm?")

    assert response == "Generated locally."
    assert runner.timeout_seconds == 12.0
    assert runner.command is not None
    assert runner.command[0] == str(runtime_path.resolve())
    assert runner.command[runner.command.index("--model") + 1] == str(model_path)
    assert runner.command[runner.command.index("--prompt") + 1] == "How do I stay warm?"
    assert runner.command[runner.command.index("--predict") + 1] == "42"
    assert runner.command[runner.command.index("--ctx-size") + 1] == "2048"
    assert "--reasoning" in runner.command
    assert "--no-show-timings" in runner.command


def test_generate_extracts_text_from_llama_cli_output() -> None:
    model_path = existing_test_file()
    runtime_path = existing_test_file()
    prompt = "Reply with exactly: Outwise works."
    output = (
        "Loading model...\n\nbuild: b11193\n\n"
        f"> {prompt}\n"
        "Outwise works.\n\n"
        "[ Prompt: 4.4 t/s | Generation: 5.0 t/s ]\n\n\nExiting...\n"
    )
    service = ModelService(
        settings(model_path, runtime_path),
        StubRunner(ProcessResult(0, output, "")),
    )

    assert service.generate(prompt) == "Outwise works."


def test_generate_extracts_text_after_llama_truncates_a_long_displayed_prompt() -> None:
    model_path = existing_test_file()
    runtime_path = existing_test_file()
    prompt = "Long grounded prompt that llama.cpp abbreviates"
    output = (
        "Loading model...\n\n> Long grounded prompt\n"
        "Context title: synthetic fixture\n"
        "Content: Rest the ankle ... (truncated)\n"
        "Use the retrieved instructions.\n\n\nExiting...\n"
    )
    service = ModelService(
        settings(model_path, runtime_path),
        StubRunner(ProcessResult(0, output, "")),
    )

    assert service.generate(prompt) == "Use the retrieved instructions."


def test_missing_model_is_reported_before_runtime_lookup() -> None:
    runner = StubRunner(ProcessResult(0, "unused", ""))
    service = ModelService(
        settings(Path("missing-model.gguf"), Path("missing-runtime.exe")), runner
    )

    with pytest.raises(ModelNotFoundError, match="setup-local-model"):
        service.generate("Hello")

    assert runner.command is None

def test_missing_configured_runtime_has_clear_error() -> None:
    model_path = existing_test_file()
    service = ModelService(
        settings(model_path, Path("missing-runtime.exe")),
        StubRunner(ProcessResult(0, "unused", "")),
    )

    with pytest.raises(ModelRuntimeNotFoundError, match="runtime not found"):
        service.generate("Hello")


def test_timeout_is_translated_to_model_error() -> None:
    model_path = existing_test_file()
    runtime_path = existing_test_file()
    runner = StubRunner(error=subprocess.TimeoutExpired("llama-cli", timeout=12))
    service = ModelService(settings(model_path, runtime_path), runner)

    with pytest.raises(ModelTimeoutError, match="12 seconds"):
        service.generate("Hello")


def test_model_load_failure_is_distinguished() -> None:
    model_path = existing_test_file()
    runtime_path = existing_test_file()
    runner = StubRunner(ProcessResult(1, "", "error loading model: invalid GGUF"))
    service = ModelService(settings(model_path, runtime_path), runner)

    with pytest.raises(ModelLoadError, match="invalid GGUF"):
        service.generate("Hello")


def test_nonzero_exit_and_empty_output_are_generation_errors() -> None:
    model_path = existing_test_file()
    runtime_path = existing_test_file()

    failing = ModelService(
        settings(model_path, runtime_path),
        StubRunner(ProcessResult(2, "", "backend initialization failed")),
    )
    with pytest.raises(ModelGenerationError, match="exit code 2"):
        failing.generate("Hello")

    empty = ModelService(
        settings(model_path, runtime_path), StubRunner(ProcessResult(0, " \n", ""))
    )
    with pytest.raises(ModelGenerationError, match="without generating text"):
        empty.generate("Hello")


def test_empty_prompt_is_rejected_without_starting_process() -> None:
    runner = StubRunner(ProcessResult(0, "unused", ""))
    service = ModelService(
        settings(Path("missing-model.gguf"), Path("missing-runtime.exe")), runner
    )

    with pytest.raises(ValueError, match="must not be empty"):
        service.generate("   ")

    assert runner.command is None
