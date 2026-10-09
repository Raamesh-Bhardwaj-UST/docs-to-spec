"""Paths and configuration for docs-to-spec."""
from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


def workspace_root() -> Path:
    """Repo the server works on. VS Code passes ${workspaceFolder} via DOCS_TO_SPEC_ROOT."""
    root = os.environ.get("DOCS_TO_SPEC_ROOT")
    return Path(root).resolve() if root else Path.cwd().resolve()


def cache_dir() -> Path:
    """Wiki clones live outside the repo (and outside OneDrive)."""
    env = os.environ.get("DOCS_TO_SPEC_CACHE")
    if env:
        path = Path(env)
    elif os.name == "nt":
        path = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "docs-to-spec" / "cache"
    else:
        path = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "docs-to-spec"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path() -> Path:
    return workspace_root() / ".specify" / "docs-to-spec" / "sources.yml"


def load_config() -> dict:
    path = config_path()
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run /speckit-docs-to-spec-setup first.")
    # utf-8-sig tolerates a BOM written by Windows PowerShell 5.
    with path.open(encoding="utf-8-sig") as handle:
        cfg = yaml.safe_load(handle) or {}
    cfg.setdefault("snapshot_dir", ".specify/harvest/raw")
    cfg.setdefault("redaction", {})
    cfg.setdefault("sources", [])
    for src in cfg["sources"]:
        sid = str(src.get("id", ""))
        if not _ID.match(sid):
            raise ValueError(f"Invalid source id '{sid}': use lowercase letters, digits and hyphens.")
        if "type" not in src:
            raise ValueError(f"Source '{sid}' has no type.")
    return cfg


def get_source(cfg: dict, source_id: str) -> dict:
    for src in cfg["sources"]:
        if src["id"] == source_id:
            return src
    known = ", ".join(s["id"] for s in cfg["sources"]) or "(none)"
    raise KeyError(f"Unknown source '{source_id}'. Configured: {known}")
