#Requires -Version 7.0
<#
.SYNOPSIS
  Installs the docs-to-spec MCP server and wires it into a repo.
.DESCRIPTION
  - Creates the server venv inside the extension folder (default <extension>\.venv; override with DOCS_TO_SPEC_VENV)
  - Creates .specify/docs-to-spec/sources.yml from the template (never overwritten)
  - Copies the rubric and the Requirements Reviewer agent (overwritten only with -Force)
  - Writes or merges .vscode/mcp.json and git-ignores it
.EXAMPLE
  pwsh -NoProfile -File .specify/extensions/docs-to-spec/scripts/powershell/setup-mcp.ps1
#>
[CmdletBinding()]
param(
  [string]$WorkspaceRoot,
  [string]$ServerDir,
  [string]$Python = "3.12",
  [switch]$Force
)
$ErrorActionPreference = 'Stop'

function Assert-Command([string]$Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { throw "$Name was not found on PATH." }
}
Assert-Command git
Assert-Command uv

if (-not $WorkspaceRoot) {
  $WorkspaceRoot = git rev-parse --show-toplevel 2>$null
  if (-not $WorkspaceRoot) { $WorkspaceRoot = (Get-Location).Path }
}
$WorkspaceRoot = (Resolve-Path $WorkspaceRoot).Path
$ExtRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not $ServerDir) { $ServerDir = Join-Path $ExtRoot 'mcp-server' }
if (-not (Test-Path (Join-Path $ServerDir 'pyproject.toml'))) {
  throw "MCP server not found at $ServerDir. Pass -ServerDir pointing at docs-to-spec\mcp-server."
}
$Venv = if ($env:DOCS_TO_SPEC_VENV) { $env:DOCS_TO_SPEC_VENV } else { Join-Path $ExtRoot '.venv' }

Write-Host "Workspace : $WorkspaceRoot"
Write-Host "Server    : $ServerDir"
Write-Host "Venv      : $Venv"

# 1. Install the server. Stop a running server first: Windows locks the .exe.
$env:UV_PROJECT_ENVIRONMENT = $Venv
$syncArgs = @('sync', '--project', $ServerDir, '--no-dev', '--python', $Python)
if (Test-Path (Join-Path $ServerDir 'uv.lock')) { $syncArgs += '--locked' }
& uv @syncArgs
if ($LASTEXITCODE -ne 0) { throw "uv sync failed (exit $LASTEXITCODE). If the server is running in VS Code, stop it and retry." }

$Cli = Join-Path $Venv 'Scripts\docs-to-spec.exe'
$Srv = Join-Path $Venv 'Scripts\docs-to-spec-mcp.exe'
if (-not (Test-Path $Srv)) { throw "Server executable not found at $Srv" }

# 2. Copy assets (UTF-8, no BOM).
function Copy-Asset([string]$From, [string]$To, [bool]$AllowOverwrite) {
  $dst = Join-Path $WorkspaceRoot $To
  if ((Test-Path $dst) -and (-not $AllowOverwrite -or -not $Force)) {
    Write-Host "skip  $To (exists)"
    return
  }
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  $text = Get-Content -Raw -Encoding utf8 (Join-Path $ExtRoot $From)
  [IO.File]::WriteAllText($dst, $text, [Text.UTF8Encoding]::new($false))
  Write-Host "wrote $To"
}
Copy-Asset 'assets/sources.template.yml'            '.specify/docs-to-spec/sources.yml'            $false
Copy-Asset 'assets/requirements-rubric.md'          '.specify/docs-to-spec/requirements-rubric.md' $true
Copy-Asset 'assets/requirements-reviewer.agent.md'  '.github/agents/requirements-reviewer.agent.md' $true

# 3. VS Code MCP config.
& $Cli --root $WorkspaceRoot configure-vscode
if ($LASTEXITCODE -ne 0) { throw "configure-vscode failed." }

# 4. Keep the per-machine mcp.json, and the venv if it is inside the workspace, out of git.
$gi = Join-Path $WorkspaceRoot '.gitignore'
$entries = @('.vscode/mcp.json')
$venvRel = [IO.Path]::GetRelativePath($WorkspaceRoot, [IO.Path]::GetFullPath($Venv))
if (-not $venvRel.StartsWith('..') -and -not [IO.Path]::IsPathRooted($venvRel) -and $venvRel -ne '.') {
  $entries += (($venvRel -replace '\\', '/').TrimEnd('/') + '/')
}
foreach ($entry in $entries) {
  $existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
  if ($existing -notcontains $entry) {
    $prefix = ''
    if ((Test-Path $gi) -and -not (Get-Content -Raw $gi).EndsWith("`n")) { $prefix = "`n" }
    [IO.File]::AppendAllText($gi, "$prefix$entry`n", [Text.UTF8Encoding]::new($false))
    Write-Host "added $entry to .gitignore"
  }
}

Write-Host ""
Write-Host "Next:"
Write-Host "  1. Edit .specify/docs-to-spec/sources.yml"
Write-Host "  2. In VS Code open .vscode/mcp.json and click Start above 'docs-to-spec' (or run 'MCP: List Servers')"
Write-Host "  3. In Copilot Chat (agent mode) enable the docs-to-spec tools, then run /speckit-docs-to-spec-harvest"
