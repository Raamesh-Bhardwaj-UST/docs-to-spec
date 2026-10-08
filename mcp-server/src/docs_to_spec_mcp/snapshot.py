"""Writes the redacted snapshot and manifest that later steps read and reviewers approve."""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import get_source, load_config, workspace_root
from .redact import redact
from .sources import fetch_documents


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def snapshot_dir(cfg: dict) -> Path:
    root = workspace_root()
    path = (root / cfg["snapshot_dir"]).resolve()
    if not path.is_relative_to(root):
        raise ValueError("snapshot_dir must be inside the workspace.")
    return path


def _manifest_path(cfg: dict) -> Path:
    return snapshot_dir(cfg) / "manifest.json"


def _update_manifest(cfg: dict, source_id: str, entry: dict) -> None:
    path = _manifest_path(cfg)
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"version": 1, "sources": {}}
    manifest["sources"][source_id] = entry
    manifest["generated_at"] = _now()
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def snapshot_source(source_id: str, cfg: dict | None = None) -> dict:
    cfg = cfg or load_config()
    src = get_source(cfg, source_id)
    emails = bool(cfg["redaction"].get("emails", False))
    docs = fetch_documents(src, refresh=True)

    root = workspace_root()
    out = snapshot_dir(cfg) / source_id
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    fetched = _now()
    totals: dict[str, int] = {}
    entries = []
    for doc in docs:
        title, c1 = redact(doc.title, emails)
        body, c2 = redact(doc.body, emails)
        counts = {k: c1.get(k, 0) + c2.get(k, 0) for k in sorted(set(c1) | set(c2))}
        for key, value in counts.items():
            totals[key] = totals.get(key, 0) + value
        front = {
            "source_id": source_id,
            "doc_id": doc.doc_id,
            "title": title,
            "url": doc.url,
            "revision": doc.revision,
            "fetched_at": fetched,
            "redactions": counts,
        }
        text = "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---\n\n" + body.strip() + "\n"
        file = out / f"{doc.doc_id}.md"
        file.write_text(text, encoding="utf-8", newline="\n")
        entries.append({
            "doc_id": doc.doc_id,
            "file": file.relative_to(root).as_posix(),
            "url": doc.url,
            "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        })

    _update_manifest(cfg, source_id, {
        "type": src["type"],
        "fetched_at": fetched,
        "documents": entries,
        "redactions": totals,
    })
    return {
        "source_id": source_id,
        "documents": len(entries),
        "redactions": totals,
        "folder": out.relative_to(root).as_posix(),
    }


def snapshot_all() -> dict:
    cfg = load_config()
    results, errors = [], {}
    for src in cfg["sources"]:
        try:
            results.append(snapshot_source(src["id"], cfg))
        except Exception as exc:  # report per source, keep going
            errors[src["id"]] = str(exc)
    return {"results": results, "errors": errors}


def status() -> dict:
    cfg = load_config()
    path = _manifest_path(cfg)
    if not path.exists():
        return {"snapshot": None, "message": "No snapshot yet. Run snapshot_all."}
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return {
        "generated_at": manifest.get("generated_at"),
        "manifest": path.relative_to(workspace_root()).as_posix(),
        "sources": {
            sid: {
                "type": entry["type"],
                "fetched_at": entry["fetched_at"],
                "documents": len(entry["documents"]),
                "redactions": sum(entry["redactions"].values()),
            }
            for sid, entry in manifest["sources"].items()
        },
    }


def search(query: str, source_id: str | None = None, max_results: int = 20) -> list[dict]:
    cfg = load_config()
    base = snapshot_dir(cfg)
    if not base.exists():
        return []
    if source_id:
        folders = [base / source_id]
    else:
        folders = sorted(p for p in base.iterdir() if p.is_dir())
    needle = query.lower()
    hits = []
    for folder in folders:
        for file in sorted(folder.glob("*.md")):
            for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
                if needle in line.lower():
                    hits.append({
                        "file": file.relative_to(workspace_root()).as_posix(),
                        "line": number,
                        "text": line.strip()[:200],
                    })
                    if len(hits) >= max_results:
                        return hits
    return hits
