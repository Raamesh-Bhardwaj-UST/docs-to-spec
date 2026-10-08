"""Fetchers for each source type. All network and git output is captured,
never written to stdout (stdout belongs to the MCP protocol)."""
from __future__ import annotations

import base64
import fnmatch
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import httpx

from .config import cache_dir, workspace_root

API = "https://api.github.com"
_synced: set[str] = set()


@dataclass
class Document:
    source_id: str
    doc_id: str
    title: str
    url: str
    body: str
    revision: str = ""


def _slug(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-")
    return slug[:120] or "untitled"


def _matches(rel: str, include, exclude) -> bool:
    # fnmatch-style; '*' also matches '/', so "*.md" means every Markdown file.
    inc = include or ["*.md"]
    exc = exclude or []
    return any(fnmatch.fnmatch(rel, p) for p in inc) and not any(fnmatch.fnmatch(rel, p) for p in exc)


def _git(args: list[str], cwd: Path | None = None, extra: list[str] | None = None) -> str:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    result = subprocess.run(["git", *(extra or []), *args], cwd=cwd, capture_output=True,
                            text=True, timeout=300, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed: {result.stderr.strip()[:500]}")
    return result.stdout.strip()


# ---------- GitHub wiki ----------

def sync_wiki(src: dict, refresh: bool = False) -> tuple[Path, str]:
    repo = src["repo"]
    dest = cache_dir() / "wiki" / repo.replace("/", "__")
    extra: list[str] = []
    if src.get("auth", "gcm") == "token":
        token = os.environ.get("GH_TOKEN")
        if not token:
            raise RuntimeError(f"Source '{src['id']}' uses auth: token but GH_TOKEN is not set.")
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        extra = ["-c", f"http.https://github.com/.extraheader=AUTHORIZATION: basic {basic}"]
    if refresh or repo not in _synced:
        if (dest / ".git").exists():
            _git(["pull", "--ff-only", "--quiet"], cwd=dest, extra=extra)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            _git(["clone", "--quiet", "--depth", "1", f"https://github.com/{repo}.wiki.git", str(dest)], extra=extra)
        _synced.add(repo)
    return dest, _git(["rev-parse", "HEAD"], cwd=dest)


def wiki_documents(src: dict, refresh: bool = False) -> list[Document]:
    root, revision = sync_wiki(src, refresh)
    docs = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".git/") or not _matches(rel, src.get("include"), src.get("exclude")):
            continue
        docs.append(Document(
            source_id=src["id"],
            doc_id=_slug(rel.rsplit(".", 1)[0]),
            title=path.stem.replace("-", " "),
            url=f"https://github.com/{src['repo']}/wiki/{path.stem}",
            body=path.read_text(encoding="utf-8", errors="replace"),
            revision=revision,
        ))
    return docs


# ---------- GitHub issues ----------

def _headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "docs-to-spec-mcp",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def issue_documents(src: dict) -> list[Document]:
    repo = src["repo"]
    max_items = int(src.get("max_items", 200))
    params = {"state": src.get("state", "open"), "per_page": 100, "sort": "updated", "direction": "desc"}
    if src.get("labels"):
        params["labels"] = ",".join(src["labels"])  # GitHub treats multiple labels as AND
    docs: list[Document] = []
    with httpx.Client(headers=_headers(), timeout=30, follow_redirects=True) as client:
        page = 1
        while len(docs) < max_items:
            resp = client.get(f"{API}/repos/{repo}/issues", params={**params, "page": page})
            resp.raise_for_status()
            items = resp.json()
            if not items:
                break
            for item in items:
                if "pull_request" in item:
                    continue
                body = item.get("body") or ""
                if src.get("include_comments", True) and item.get("comments", 0):
                    cresp = client.get(item["comments_url"], params={"per_page": 100})
                    cresp.raise_for_status()
                    for comment in cresp.json():
                        # Author logins are deliberately left out.
                        date = (comment.get("created_at") or "")[:10]
                        body += f"\n\n---\n**Comment ({date}):**\n\n{comment.get('body') or ''}"
                docs.append(Document(
                    source_id=src["id"],
                    doc_id=f"issue-{item['number']}",
                    title=f"#{item['number']} {item['title']}",
                    url=item["html_url"],
                    body=body,
                    revision=item.get("updated_at", ""),
                ))
                if len(docs) >= max_items:
                    break
            page += 1
    return docs


# ---------- Local docs in the workspace ----------

def local_documents(src: dict) -> list[Document]:
    root = workspace_root()
    base = (root / src.get("path", "docs")).resolve()
    if not base.is_relative_to(root):
        raise ValueError(f"Source '{src['id']}': path must be inside the workspace.")
    try:
        revision = _git(["rev-parse", "HEAD"], cwd=root)
    except RuntimeError:
        revision = ""
    docs = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(base).as_posix()
        if not _matches(rel, src.get("include"), src.get("exclude")):
            continue
        docs.append(Document(
            source_id=src["id"],
            doc_id=_slug(rel.rsplit(".", 1)[0]),
            title=path.stem,
            url=path.relative_to(root).as_posix(),
            body=path.read_text(encoding="utf-8", errors="replace"),
            revision=revision,
        ))
    return docs


def fetch_documents(src: dict, refresh: bool = False) -> list[Document]:
    kind = src.get("type")
    if kind == "github-wiki":
        return wiki_documents(src, refresh)
    if kind == "github-issues":
        return issue_documents(src)
    if kind == "local":
        return local_documents(src)
    raise ValueError(f"Unsupported source type '{kind}' for source '{src.get('id')}'.")
