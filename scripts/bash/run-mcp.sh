#!/usr/bin/env bash
# Runs the docs-to-spec MCP server by hand for testing. --inspect opens the MCP Inspector.
set -euo pipefail
INSPECT=0; ROOT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --inspect) INSPECT=1; shift ;;
    --root) ROOT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done
ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV="${DOCS_TO_SPEC_VENV:-$EXT_ROOT/.venv}"
SRV="$VENV/bin/docs-to-spec-mcp"
[[ -x "$SRV" ]] || { echo "Not installed. Run setup-mcp.sh first." >&2; exit 1; }
export DOCS_TO_SPEC_ROOT="$(cd "$ROOT" && pwd)"
[[ -n "${GH_TOKEN:-}" ]] || echo "Note: GH_TOKEN is not set for this session." >&2
if [[ "$INSPECT" -eq 1 ]]; then exec npx -y @modelcontextprotocol/inspector "$SRV"; fi
echo "docs-to-spec MCP server on stdio for $DOCS_TO_SPEC_ROOT (Ctrl+C to stop)" >&2
exec "$SRV"
