"""docs-to-spec MCP server (stdio). Never print to stdout here; logs go to stderr."""
from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from . import snapshot as snap
from .config import get_source, load_config
from .redact import redact
from .sources import fetch_documents

logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
mcp = FastMCP("docs-to-spec")


@mcp.tool()
def list_sources() -> list[dict]:
    """List the sources configured in .specify/docs-to-spec/sources.yml."""
    cfg = load_config()
    keys = ("repo", "path", "labels", "state")
    return [{"id": s["id"], "type": s["type"], **{k: s[k] for k in keys if k in s}} for s in cfg["sources"]]


@mcp.tool()
def snapshot_all() -> dict:
    """Fetch every configured source, redact sensitive data, and write the snapshot to
    .specify/harvest/raw/<source>/ plus manifest.json. Returns per-source document and redaction counts."""
    return snap.snapshot_all()


@mcp.tool()
def snapshot_source(source_id: str) -> dict:
    """Re-snapshot a single source by id."""
    return snap.snapshot_source(source_id)


@mcp.tool()
def snapshot_status() -> dict:
    """Summarise the current snapshot from manifest.json."""
    return snap.status()


@mcp.tool()
def search_snapshot(query: str, source_id: str | None = None, max_results: int = 20) -> list[dict]:
    """Case-insensitive text search over the redacted snapshot. Returns file, line and a short excerpt."""
    return snap.search(query, source_id, max_results)


@mcp.tool()
def list_documents(source_id: str) -> list[dict]:
    """Live listing (no snapshot written) of a source's documents: doc_id, title, url."""
    src = get_source(load_config(), source_id)
    return [{"doc_id": d.doc_id, "title": redact(d.title)[0], "url": d.url} for d in fetch_documents(src)]


@mcp.tool()
def read_document(source_id: str, doc_id: str) -> dict:
    """Live, redacted read of one document. Prefer the snapshot files for extraction."""
    cfg = load_config()
    src = get_source(cfg, source_id)
    emails = bool(cfg["redaction"].get("emails", False))
    for doc in fetch_documents(src):
        if doc.doc_id == doc_id:
            body, counts = redact(doc.body, emails)
            return {"doc_id": doc.doc_id, "title": redact(doc.title, emails)[0], "url": doc.url,
                    "body": body, "redactions": counts}
    raise KeyError(f"Document '{doc_id}' not found in source '{source_id}'.")


def main() -> None:
    mcp.run()  # stdio transport


if __name__ == "__main__":
    main()
