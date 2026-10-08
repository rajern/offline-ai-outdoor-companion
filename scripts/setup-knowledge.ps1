param(
    [switch]$Offline,
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$repositoryPath = Split-Path -Parent $PSScriptRoot
if (-not $Python) {
    $Python = Join-Path $repositoryPath "backend\.venv\Scripts\python.exe"
}
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Backend Python not found. Follow backend/README.md first."
}

Push-Location (Join-Path $repositoryPath "backend")
try {
    $ingestionArgs = @("-m", "outwise.knowledge.ingestion")
    $embeddingArgs = @("-m", "outwise.knowledge.embeddings")
    if (-not $Offline) {
        $ingestionArgs += "--fetch"
        $embeddingArgs += "--setup-model"
    }
    & $Python @ingestionArgs
    if ($LASTEXITCODE -ne 0) { throw "Knowledge ingestion failed." }
    & $Python @embeddingArgs
    if ($LASTEXITCODE -ne 0) { throw "Embedding build failed." }
    & $Python -m outwise.knowledge.evaluate
    if ($LASTEXITCODE -ne 0) { throw "Retrieval evaluation failed; inspect knowledge/local/retrieval-report.json." }
}
finally {
    Pop-Location
}
