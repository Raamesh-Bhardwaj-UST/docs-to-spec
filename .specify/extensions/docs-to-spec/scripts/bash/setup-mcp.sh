#!/usr/bin/env bash
# Installs the docs-to-spec MCP server and wires it into a repo (Linux/macOS).
set -euo pipefail

FORCE=0; ROOT=""; SERVER_DIR=""; PY="3.12"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=1; shift ;;
    --root) ROOT="$2"; shift 2 ;;
    --server-dir) SERVER_DIR="$2"; shift 2 ;;
    --python) PY="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

need() { command -v "$1" >/dev/null 2>&1 || { echo "$1 was not found on PATH" >&2; exit 1; }; }
need git; need uv

ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
ROOT="$(cd "$ROOT" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SERVER_DIR="${SERVER_DIR:-$EXT_ROOT/mcp-server}"
[[ -f "$SERVER_DIR/pyproject.toml" ]] || { echo "MCP server not found at $SERVER_DIR (use --server-dir)" >&2; exit 1; }
VENV="${DOCS_TO_SPEC_VENV:-$EXT_ROOT/.venv}"

echo "Workspace : $ROOT"
echo "Server    : $SERVER_DIR"
echo "Venv      : $VENV"

export UV_PROJECT_ENVIRONMENT="$VENV"
SYNC=(sync --project "$SERVER_DIR" --no-dev --python "$PY")
if [[ -f "$SERVER_DIR/uv.lock" ]]; then SYNC+=(--locked); fi
uv "${SYNC[@]}"

CLI="$VENV/bin/docs-to-spec"
SRV="$VENV/bin/docs-to-spec-mcp"
[[ -x "$SRV" ]] || { echo "Server executable not found at $SRV" >&2; exit 1; }

copy_asset() {  # from to allow_overwrite(0|1)
  local from="$EXT_ROOT/$1" to="$ROOT/$2" allow="$3"
  if [[ -e "$to" && ( "$allow" -eq 0 || "$FORCE" -eq 0 ) ]]; then echo "skip  $2 (exists)"; return; fi
  mkdir -p "$(dirname "$to")"; cp "$from" "$to"; echo "wrote $2"
}
copy_asset assets/sources.template.yml           .specify/docs-to-spec/sources.yml             0
copy_asset assets/requirements-rubric.md         .specify/docs-to-spec/requirements-rubric.md  1
copy_asset assets/requirements-reviewer.agent.md .github/agents/requirements-reviewer.agent.md 1

"$CLI" --root "$ROOT" configure-vscode

GI="$ROOT/.gitignore"
ENTRIES=('.vscode/mcp.json')
VENV_ABS="$(mkdir -p "$VENV" && cd "$VENV" && pwd)"
if [[ "$VENV_ABS" == "$ROOT"/* ]]; then ENTRIES+=("${VENV_ABS#"$ROOT"/}/"); fi
for entry in "${ENTRIES[@]}"; do
  if ! grep -qxF "$entry" "$GI" 2>/dev/null; then
    if [[ -s "$GI" && -n "$(tail -c1 "$GI")" ]]; then echo >> "$GI"; fi
    echo "$entry" >> "$GI"
    echo "added $entry to .gitignore"
  fi
done

cat <<'EOF'

Next:
  1. Edit .specify/docs-to-spec/sources.yml
  2. In VS Code open .vscode/mcp.json and click Start above 'docs-to-spec' (or run 'MCP: List Servers')
  3. In Copilot Chat (agent mode) enable the docs-to-spec tools, then run /speckit-docs-to-spec-harvest
EOF
