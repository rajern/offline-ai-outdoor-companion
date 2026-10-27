[CmdletBinding()]
param([ValidateRange(1, 65535)][int]$Port = 8080)
$ErrorActionPreference = 'Stop'
& node (Join-Path $PSScriptRoot 'serve-demo.mjs') --port $Port
if ($LASTEXITCODE -ne 0) { throw 'Demo failed to start. See the message above and README.md.' }
