#Requires -Version 7.0
[CmdletBinding()]
param([string]$WorkspaceRoot, [string]$Source)
$ErrorActionPreference = 'Stop'

if (-not $WorkspaceRoot) {
  $WorkspaceRoot = git rev-parse --show-toplevel 2>$null
  if (-not $WorkspaceRoot) { $WorkspaceRoot = (Get-Location).Path }
}
$WorkspaceRoot = (Resolve-Path $WorkspaceRoot).Path
$ExtRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Venv = if ($env:DOCS_TO_SPEC_VENV) { $env:DOCS_TO_SPEC_VENV } else { Join-Path $ExtRoot '.venv' }
$Cli = Join-Path $Venv 'Scripts\docs-to-spec.exe'
if (-not (Test-Path $Cli)) { throw "Not installed. Run setup-mcp.ps1 first." }
if (-not $env:GH_TOKEN) { Write-Warning "GH_TOKEN is not set: private issues and 'auth: token' wikis will fail." }

$cliArgs = @('--root', $WorkspaceRoot, 'snapshot')
if ($Source) { $cliArgs += @('--source', $Source) }
& $Cli @cliArgs
$code = $LASTEXITCODE
& $Cli --root $WorkspaceRoot status
exit $code
