[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Prompt,

    [string]$ModelPath,

    [string]$LlamaCliPath,

    [ValidateRange(1, 4096)]
    [int]$MaxTokens = 256,

    [ValidateRange(512, 32768)]
    [int]$ContextSize = 4096
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$defaultModelPath = Join-Path $repositoryRoot "models\Qwen_Qwen3.5-2B-Q4_K_M.gguf"

if ([string]::IsNullOrWhiteSpace($ModelPath)) {
    if (-not [string]::IsNullOrWhiteSpace($env:OUTWISE_MODEL_PATH)) {
        $ModelPath = $env:OUTWISE_MODEL_PATH
    } else {
        $ModelPath = $defaultModelPath
    }
}
$ModelPath = [System.IO.Path]::GetFullPath($ModelPath)

if (-not (Test-Path -LiteralPath $ModelPath -PathType Leaf)) {
    throw "Model not found at '$ModelPath'. Run scripts\setup-local-model.ps1 first or pass -ModelPath."
}

$llamaCommand = $null
$llamaArguments = @()

if (-not [string]::IsNullOrWhiteSpace($LlamaCliPath)) {
    if (-not (Test-Path -LiteralPath $LlamaCliPath -PathType Leaf)) {
        throw "llama.cpp executable not found at '$LlamaCliPath'."
    }
    $llamaCommand = (Resolve-Path -LiteralPath $LlamaCliPath).Path
} elseif (-not [string]::IsNullOrWhiteSpace($env:OUTWISE_LLAMA_CLI)) {
    if (-not (Test-Path -LiteralPath $env:OUTWISE_LLAMA_CLI -PathType Leaf)) {
        throw "OUTWISE_LLAMA_CLI points to a missing file: '$env:OUTWISE_LLAMA_CLI'."
    }
    $llamaCommand = (Resolve-Path -LiteralPath $env:OUTWISE_LLAMA_CLI).Path
} else {
    $standaloneCli = Get-Command llama-cli.exe -ErrorAction SilentlyContinue
    if ($standaloneCli) {
        $llamaCommand = $standaloneCli.Source
    } else {
        $unifiedCli = Get-Command llama.exe -ErrorAction SilentlyContinue
        if ($unifiedCli) {
            $llamaCommand = $unifiedCli.Source
            $llamaArguments += "cli"
        } else {
            # WinGet updates PATH for future processes, not the shell that ran setup.
            $packageRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
            if (Test-Path -LiteralPath $packageRoot -PathType Container) {
                $packageDirectory = Get-ChildItem -LiteralPath $packageRoot -Directory -Filter "ggml.llamacpp_*" |
                    Select-Object -First 1
                if ($packageDirectory) {
                    $wingetCli = Get-ChildItem -LiteralPath $packageDirectory.FullName -File -Recurse -Filter "llama-cli.exe" |
                        Select-Object -First 1
                    if ($wingetCli) {
                        $llamaCommand = $wingetCli.FullName
                    }
                }
            }
        }
    }
}

if (-not $llamaCommand) {
    throw "llama.cpp was not found. Run scripts\setup-local-model.ps1, open a new PowerShell window, and retry."
}

$llamaArguments += @(
    "--model", $ModelPath,
    "--prompt", $Prompt,
    "--predict", $MaxTokens,
    "--ctx-size", $ContextSize,
    "--temp", "0.7",
    "--top-p", "0.8",
    "--top-k", "20",
    "--reasoning", "off",
    "--single-turn",
    "--no-display-prompt",
    "--simple-io"
)

& $llamaCommand @llamaArguments
if ($LASTEXITCODE -ne 0) {
    throw "llama.cpp exited with code $LASTEXITCODE."
}
