"""Local language-model inference behind a llama.cpp-independent interface."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


DEFAULT_MODEL_FILENAME = "Qwen_Qwen3.5-2B-Q4_K_M.gguf"


class ModelServiceError(RuntimeError):
    """Base class for model-service failures safe for callers to handle."""


class ModelNotFoundError(ModelServiceError):
    """Raised when the configured GGUF model is unavailable."""


class ModelRuntimeNotFoundError(ModelServiceError):
    """Raised when a llama.cpp command cannot be found."""


class ModelLoadError(ModelServiceError):
    """Raised when llama.cpp cannot load the configured model."""


class ModelTimeoutError(ModelServiceError):
    """Raised when generation exceeds the configured deadline."""


class ModelGenerationError(ModelServiceError):
    """Raised when llama.cpp does not produce a usable response."""


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


class ProcessRunner(Protocol):
    """Boundary around process execution, replaceable in tests."""

    def run(self, command: Sequence[str], timeout_seconds: float) -> ProcessResult: ...


class SubprocessRunner:
    def run(self, command: Sequence[str], timeout_seconds: float) -> ProcessResult:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
        return ProcessResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


@dataclass(frozen=True)
class ModelSettings:
    model_path: Path
    llama_cli_path: Path | None = None
    timeout_seconds: float = 120.0
    max_tokens: int = 256
    context_size: int = 4096

    @classmethod
    def from_environment(cls) -> ModelSettings:
        repository_root = Path(__file__).resolve().parents[3]
        model_path = Path(
            os.environ.get(
                "OUTWISE_MODEL_PATH",
                repository_root / "models" / DEFAULT_MODEL_FILENAME,
            )
        )
        configured_cli = os.environ.get("OUTWISE_LLAMA_CLI")
        return cls(
            model_path=model_path,
            llama_cli_path=Path(configured_cli) if configured_cli else None,
        )


class ModelService:
    """Generate text locally without exposing llama.cpp details to callers."""

    def __init__(
        self,
        settings: ModelSettings | None = None,
        runner: ProcessRunner | None = None,
    ) -> None:
        self.settings = settings or ModelSettings.from_environment()
        self._runner = runner or SubprocessRunner()

    def generate(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")
        if not self.settings.model_path.is_file():
            raise ModelNotFoundError(
                f"Model not found at '{self.settings.model_path}'. "
                "Run scripts/setup-local-model.ps1 or set OUTWISE_MODEL_PATH."
            )

        runtime = self._resolve_runtime()
        command = [
            *runtime,
            "--model",
            str(self.settings.model_path),
            "--prompt",
            prompt,
            "--predict",
            str(self.settings.max_tokens),
            "--ctx-size",
            str(self.settings.context_size),
            "--temp",
            "0.7",
            "--top-p",
            "0.8",
            "--top-k",
            "20",
            "--reasoning",
            "off",
            "--single-turn",
            "--no-display-prompt",
            "--no-show-timings",
            "--color",
            "off",
            "--simple-io",
        ]

        try:
            result = self._runner.run(command, self.settings.timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            raise ModelTimeoutError(
                f"Local model generation exceeded {self.settings.timeout_seconds:g} seconds."
            ) from exc
        except OSError as exc:
            raise ModelRuntimeNotFoundError(
                f"Could not start llama.cpp runtime '{runtime[0]}': {exc}"
            ) from exc

        if result.returncode != 0:
            details = _error_details(result)
            if _looks_like_load_failure(details):
                raise ModelLoadError(f"llama.cpp could not load the model: {details}")
            raise ModelGenerationError(
                f"llama.cpp generation failed with exit code {result.returncode}: {details}"
            )

        response = _extract_generated_text(result.stdout, prompt)
        if not response:
            raise ModelGenerationError("llama.cpp completed without generating text.")
        return response

    def _resolve_runtime(self) -> list[str]:
        configured = self.settings.llama_cli_path
        if configured is not None:
            if not configured.is_file():
                raise ModelRuntimeNotFoundError(
                    f"llama.cpp runtime not found at '{configured}'."
                )
            return [str(configured.resolve())]

        standalone = shutil.which("llama-cli.exe") or shutil.which("llama-cli")
        if standalone:
            return [standalone]

        unified = shutil.which("llama.exe") or shutil.which("llama")
        if unified:
            return [unified, "cli"]

        winget_cli = _find_winget_llama_cli()
        if winget_cli:
            return [str(winget_cli)]

        raise ModelRuntimeNotFoundError(
            "llama.cpp runtime was not found. Run scripts/setup-local-model.ps1 "
            "or set OUTWISE_LLAMA_CLI."
        )


def _find_winget_llama_cli() -> Path | None:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return None

    package_root = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
    if not package_root.is_dir():
        return None

    for package_directory in package_root.glob("ggml.llamacpp_*"):
        for candidate in package_directory.rglob("llama-cli.exe"):
            if candidate.is_file():
                return candidate
    return None


def _error_details(result: ProcessResult) -> str:
    output = result.stderr.strip() or result.stdout.strip()
    return output[-2000:] if output else "no error output"


def _extract_generated_text(output: str, prompt: str) -> str:
    """Remove the interactive framing emitted by supported llama.cpp CLIs."""
    normalized = output.replace("\r\n", "\n")
    normalized_prompt = prompt.replace("\r\n", "\n")

    cli_marker = f"\n> {normalized_prompt}\n"
    marker_position = normalized.rfind(cli_marker)
    if marker_position >= 0:
        generated = normalized[marker_position + len(cli_marker) :]
        for suffix in ("\n\n[ Prompt:", "\n\n\nExiting...", "\n\nExiting..."):
            generated = generated.split(suffix, maxsplit=1)[0]
        return generated.strip()

    # Current llama.cpp builds abbreviate long displayed prompts even when
    # --no-display-prompt is requested. The generated text follows this marker.
    # Handle it before the generic fallback so runtime framing is never exposed
    # as the user's answer for RAG-sized prompts.
    prompt_start = normalized.rfind("\n> ")
    if prompt_start >= 0:
        displayed_prompt = normalized[prompt_start:]
        truncated_prompt_match = re.search(
            r"(?m)^.*\.\.\. \(truncated\)\n", displayed_prompt
        )
        if truncated_prompt_match:
            generated = displayed_prompt[truncated_prompt_match.end() :]
            for suffix in ("\n\n[ Prompt:", "\n\n\nExiting...", "\n\nExiting..."):
                generated = generated.split(suffix, maxsplit=1)[0]
            return generated.strip()

    completion_marker = f"user\n{normalized_prompt}\nassistant\n"
    marker_position = normalized.rfind(completion_marker)
    if marker_position >= 0:
        generated = normalized[marker_position + len(completion_marker) :].strip()
        if generated.endswith("[end of text]"):
            generated = generated[: -len("[end of text]")].rstrip()
        if generated.startswith("<think>\n\n</think>"):
            generated = generated[len("<think>\n\n</think>") :].lstrip()
        return generated

    return normalized.strip()


def _looks_like_load_failure(details: str) -> bool:
    normalized = details.casefold()
    indicators = (
        "failed to load model",
        "error loading model",
        "unable to load model",
        "invalid model",
        "invalid gguf",
    )
    return any(indicator in normalized for indicator in indicators)
