#!/usr/bin/env bash
# Snapshot without the agent (fallback / CI / first-time credential sign-in).
set -euo pipefail
ROOT=""; SOURCE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --source) SOURCE="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done
ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV="${DOCS_TO_SPEC_VENV:-$EXT_ROOT/.venv}"
CLI="$VENV/bin/docs-to-spec"
[[ -x "$CLI" ]] || { echo "Not installed. Run setup-mcp.sh first." >&2; exit 1; }
[[ -n "${GH_TOKEN:-}" ]] || echo "Warning: GH_TOKEN is not set: private issues and 'auth: token' wikis will fail." >&2
ARGS=(--root "$ROOT" snapshot)
[[ -n "$SOURCE" ]] && ARGS+=(--source "$SOURCE")
set +e; "$CLI" "${ARGS[@]}"; CODE=$?; set -e
"$CLI" --root "$ROOT" status
exit "$CODE"
