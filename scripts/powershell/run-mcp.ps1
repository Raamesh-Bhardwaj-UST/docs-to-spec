#Requires -Version 7.0
<#
.SYNOPSIS
  Runs the docs-to-spec MCP server by hand for testing.
.DESCRIPTION
  VS Code does not use this script; it starts the server exe directly from .vscode/mcp.json.
  Use -Inspect to open the MCP Inspector (needs Node.js / npx).
#>
[CmdletBinding()]
param([string]$WorkspaceRoot, [switch]$Inspect)
$ErrorActionPreference = 'Stop'

if (-not $WorkspaceRoot) {
  $WorkspaceRoot = git rev-parse --show-toplevel 2>$null
  if (-not $WorkspaceRoot) { $WorkspaceRoot = (Get-Location).Path }
}
$WorkspaceRoot = (Resolve-Path $WorkspaceRoot).Path
$ExtRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Venv = if ($env:DOCS_TO_SPEC_VENV) { $env:DOCS_TO_SPEC_VENV } else { Join-Path $ExtRoot '.venv' }
$Srv = Join-Path $Venv 'Scripts\docs-to-spec-mcp.exe'
if (-not (Test-Path $Srv)) { [Console]::Error.WriteLine("Not installed. Run setup-mcp.ps1 first."); exit 1 }

$env:DOCS_TO_SPEC_ROOT = $WorkspaceRoot
if (-not $env:GH_TOKEN) { [Console]::Error.WriteLine("Note: GH_TOKEN is not set for this session.") }

if ($Inspect) {
  npx -y @modelcontextprotocol/inspector $Srv
  exit $LASTEXITCODE
}
[Console]::Error.WriteLine("docs-to-spec MCP server on stdio for $WorkspaceRoot (Ctrl+C to stop)")
& $Srv
exit $LASTEXITCODE
