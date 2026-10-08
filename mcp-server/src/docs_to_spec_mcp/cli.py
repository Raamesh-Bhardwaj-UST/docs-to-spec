"""Command-line entry point: snapshot without an agent, show status, write .vscode/mcp.json."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

INPUT_ID = "docs-to-spec-gh-token"


def configure_vscode(root: Path) -> Path:
    vscode = root / ".vscode"
    vscode.mkdir(exist_ok=True)
    path = vscode / "mcp.json"
    data: dict = {}
    if path.exists():
        raw = path.read_text(encoding="utf-8-sig")
        try:
            data = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            raise SystemExit(f"{path} is not plain JSON (it may contain comments). "
                             "Add the docs-to-spec entry by hand; see the README.")
    exe_name = "docs-to-spec-mcp.exe" if os.name == "nt" else "docs-to-spec-mcp"
    exe = Path(sys.executable).with_name(exe_name)
    inputs = data.setdefault("inputs", [])
    if not any(i.get("id") == INPUT_ID for i in inputs):
        inputs.append({
            "type": "promptString",
            "id": INPUT_ID,
            "description": "GitHub PAT for docs-to-spec (leave empty for public sources or gcm-only wikis)",
            "password": True,
        })
    data.setdefault("servers", {})["docs-to-spec"] = {
        "type": "stdio",
        "command": str(exe),
        "args": [],
        "env": {
            "DOCS_TO_SPEC_ROOT": "${workspaceFolder}",
            "GH_TOKEN": "${input:" + INPUT_ID + "}",
        },
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(prog="docs-to-spec")
    parser.add_argument("--root", help="Workspace root (default: current directory)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    snap_p = sub.add_parser("snapshot", help="Fetch, redact and write the snapshot")
    snap_p.add_argument("--source", help="Only this source id")
    sub.add_parser("status", help="Show snapshot status")
    sub.add_parser("configure-vscode", help="Write or merge .vscode/mcp.json")
    args = parser.parse_args()

    if args.root:
        os.environ["DOCS_TO_SPEC_ROOT"] = str(Path(args.root).resolve())
    from . import snapshot as snap
    from .config import workspace_root

    if args.cmd == "configure-vscode":
        print(f"wrote {configure_vscode(workspace_root())}")
        return
    if args.cmd == "status":
        print(json.dumps(snap.status(), indent=2))
        return
    result = {"results": [snap.snapshot_source(args.source)], "errors": {}} if args.source else snap.snapshot_all()
    print(json.dumps(result, indent=2))
    if result["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
