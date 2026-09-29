# Local model setup (Windows)

Outwise uses Qwen3.5-2B in GGUF `Q4_K_M` format through llama.cpp. The setup below installs all runtime assets locally. No prompt or generated text is sent to a cloud service.

## Requirements

- Windows 10 or 11 on x64
- PowerShell 7 recommended (Windows PowerShell 5.1 also works)
- WinGet (`winget.exe`)
- about 2 GB of free disk space for the model and download staging, plus space for llama.cpp
- internet access during setup only

## Install

From the repository root:

```powershell
.\scripts\setup-local-model.ps1
```

The script is safe to run again. It:

1. installs or verifies the pinned `ggml.llamacpp` WinGet package (`b11193`)
2. downloads the pinned `Qwen_Qwen3.5-2B-Q4_K_M.gguf` artifact to `models/`
3. verifies the model's SHA-256 before making it available

The GGUF is a community quantization of the official `Qwen/Qwen3.5-2B` weights. Both the original model and the selected quantization are marked Apache-2.0. The downloaded revision and checksum are pinned in the script so setup does not silently switch artifacts.

If llama.cpp is already installed, skip its installation:

```powershell
.\scripts\setup-local-model.ps1 -SkipRuntimeInstall
```

`models/` and all `*.gguf` files are ignored by Git. Do not commit the downloaded model or llama.cpp binaries.

## Run a local prompt

Run:

```powershell
.\scripts\run-local-model.ps1 -Prompt "Reply with exactly: Outwise is offline."
```

The command uses only the local model file. Once setup is complete, disconnecting the computer from the network does not affect this prompt flow.

The default context is deliberately limited to 4096 tokens to keep memory use reasonable for the PC MVP. Override it only when needed:

```powershell
.\scripts\run-local-model.ps1 -Prompt "Summarize how to stay warm." -ContextSize 8192 -MaxTokens 384
```

## Non-default paths

Pass paths directly:

```powershell
.\scripts\run-local-model.ps1 `
  -Prompt "Hello" `
  -ModelPath "D:\models\Qwen_Qwen3.5-2B-Q4_K_M.gguf" `
  -LlamaCliPath "C:\tools\llama-cli.exe"
```

Alternatively, set `OUTWISE_MODEL_PATH` and `OUTWISE_LLAMA_CLI` for the current shell. Explicit parameters take precedence over environment variables.

## Troubleshooting

- **`winget.exe` not found:** install Microsoft App Installer, then retry.
- **`llama.cpp was not found`:** rerun setup without `-SkipRuntimeInstall`, open a new terminal so the updated `PATH` is loaded, or pass `-LlamaCliPath`.
- **hash mismatch:** remove the named model or `.partial` file and retry. Do not use an unverified artifact.
- **out of memory:** close other large applications and keep `-ContextSize` at 4096 or lower.
- **slow generation:** CPU-only inference can be slow. This is not an internet call; speed depends on local hardware and the llama.cpp build selected by WinGet.

## Upstream references

- Original model: <https://huggingface.co/Qwen/Qwen3.5-2B>
- Pinned GGUF repository: <https://huggingface.co/bartowski/Qwen_Qwen3.5-2B-GGUF>
- llama.cpp: <https://github.com/ggml-org/llama.cpp>
- llama.cpp CLI documentation: <https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md>
