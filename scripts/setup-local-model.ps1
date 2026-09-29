[CmdletBinding()]
param(
    [string]$ModelDirectory,
    [switch]$SkipRuntimeInstall
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$llamaPackageId = "ggml.llamacpp"
$llamaVersion = "b11193"
$modelRepository = "bartowski/Qwen_Qwen3.5-2B-GGUF"
$modelRevision = "7d26695454df6de5fbcce2e58681e62dae06ce43"
$modelFileName = "Qwen_Qwen3.5-2B-Q4_K_M.gguf"
$modelSha256 = "57a1085840f497d764a7fc5d346922dbde961efb54cc792ea81d694fd846a1d8"

$repositoryRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ModelDirectory)) {
    $ModelDirectory = Join-Path $repositoryRoot "models"
}
$ModelDirectory = [System.IO.Path]::GetFullPath($ModelDirectory)
$modelPath = Join-Path $ModelDirectory $modelFileName
$partialPath = "$modelPath.partial"
$modelUrl = "https://huggingface.co/$modelRepository/resolve/$modelRevision/${modelFileName}?download=true"

function Find-WinGetLlamaCli {
    $packageRoot = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    if (-not (Test-Path -LiteralPath $packageRoot -PathType Container)) {
        return $null
    }

    $packageDirectory = Get-ChildItem -LiteralPath $packageRoot -Directory -Filter "${llamaPackageId}_*" |
        Select-Object -First 1
    if (-not $packageDirectory) {
        return $null
    }

    $cli = Get-ChildItem -LiteralPath $packageDirectory.FullName -File -Recurse -Filter "llama-cli.exe" |
        Select-Object -First 1
    if ($cli) {
        return $cli.FullName
    }

    return $null
}

function Test-PinnedLlamaCli {
    param([Parameter(Mandatory)][string]$Path)

    $versionOutput = (& $Path --version 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) {
        return $false
    }

    $expectedBuild = $llamaVersion.TrimStart("b")
    return $versionOutput -match "build\s+$([regex]::Escape($expectedBuild))\b"
}

function Test-ModelHash {
    param([Parameter(Mandatory)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $false
    }

    $actualHash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    return $actualHash -eq $modelSha256
}

if (-not $SkipRuntimeInstall) {
    $installedCli = Find-WinGetLlamaCli
    if ($installedCli -and (Test-PinnedLlamaCli -Path $installedCli)) {
        Write-Host "The expected llama.cpp build is already installed: $installedCli"
    } else {
        $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
        if (-not $winget) {
            throw "WinGet was not found. Install App Installer from Microsoft, then run this script again."
        }

        Write-Host "Installing llama.cpp $llamaVersion through WinGet..."
        & $winget.Source install `
            --id $llamaPackageId `
            --version $llamaVersion `
            --exact `
            --source winget `
            --accept-package-agreements `
            --accept-source-agreements `
            --disable-interactivity

        if ($LASTEXITCODE -ne 0) {
            throw "WinGet could not install $llamaPackageId $llamaVersion (exit code $LASTEXITCODE). If another build is installed, remove it or use -SkipRuntimeInstall intentionally."
        }

        $installedCli = Find-WinGetLlamaCli
        if (-not $installedCli -or -not (Test-PinnedLlamaCli -Path $installedCli)) {
            throw "llama.cpp was installed, but the expected build $llamaVersion could not be verified."
        }
    }
}

New-Item -ItemType Directory -Path $ModelDirectory -Force | Out-Null

if (Test-ModelHash -Path $modelPath) {
    Write-Host "The expected model is already installed: $modelPath"
    exit 0
}

if (Test-Path -LiteralPath $modelPath) {
    throw "A model exists at '$modelPath', but its SHA-256 does not match. Remove it and run the script again."
}

if (Test-Path -LiteralPath $partialPath) {
    Remove-Item -LiteralPath $partialPath -Force
}

$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
if (-not $curl) {
    throw "curl.exe was not found. It is included with supported Windows versions."
}

Write-Host "Downloading $modelRepository ($modelFileName, about 1.4 GB)..."
& $curl.Source `
    --fail `
    --location `
    --retry 3 `
    --output $partialPath `
    $modelUrl

if ($LASTEXITCODE -ne 0) {
    throw "Model download failed (curl exit code $LASTEXITCODE)."
}

if (-not (Test-ModelHash -Path $partialPath)) {
    throw "The downloaded model failed SHA-256 verification. Delete '$partialPath' before retrying."
}

Move-Item -LiteralPath $partialPath -Destination $modelPath
Write-Host "Model installed and verified: $modelPath"
Write-Host "Local model setup is complete."
