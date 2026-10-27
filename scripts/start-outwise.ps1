[CmdletBinding()]
param([string]$Python = '', [int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
if (-not $Python) { $Python = Join-Path $taskRoot 'backend/.venv/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'Set up backend Python first; see README.md.' }
$Python = (Resolve-Path -LiteralPath $Python).Path
if (-not (Test-Path -LiteralPath (Join-Path $taskRoot 'frontend/dist/index.html'))) {
    Push-Location (Join-Path $taskRoot 'frontend')
    try {
        & pnpm build:web
        if ($LASTEXITCODE -ne 0) { throw 'Build failed. Install frontend dependencies first; see README.md.' }
    } finally { Pop-Location }
}
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
Write-Host "Outwise: http://127.0.0.1:$Port   Demo: http://127.0.0.1:$Port/?demo=1"
Write-Host 'Local learning prototype. Press Ctrl+C to stop.'
Push-Location (Join-Path $taskRoot 'backend')
try { & $Python -m uvicorn outwise.main:app --host 127.0.0.1 --port $Port }
finally { Pop-Location }
