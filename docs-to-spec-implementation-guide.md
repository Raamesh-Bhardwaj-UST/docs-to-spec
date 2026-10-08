# docs-to-spec: step-by-step implementation guide

This guide builds a Spec Kit extension, `docs-to-spec`, in a new repo of the same name. The extension does five things:

1. Harvests GitHub wikis, GitHub issues and local docs through a local MCP server. The server redacts sensitive data before anything reaches the agent or the disk.
2. Extracts EARS requirements, each with a citation and a ranked open-questions list. Gaps are never filled by guessing.
3. Reviews the requirements against a written rubric, using a separate Requirements Reviewer agent and test-first, round-trip and grounding checks.
4. Clarifies gaps with you, at most five questions per round, and writes your answers back.
5. Proposes candidate features as ready-to-run `/speckit-assess-intake` and `/speckit-specify` prompts.

The flow is:

```text
harvest (MCP, redacted snapshot) → [gate: commit snapshot] → extract → review → clarify (≤5/round)
  → [gate: human approval] → propose → /speckit-assess-* → /speckit-specify → /speckit-clarify → /speckit-checklist
```

Commands are PowerShell 7 on Windows unless marked **bash** or **Copilot Chat**. Every file is listed with its full content, so you can create them by hand in the order given.

---

## Phase 0: Prerequisites and decisions

### Variables

```powershell
$WORK = Join-Path $HOME "OneDrive - UST\Desktop\Work"
$D2S  = Join-Path $WORK "docs-to-spec"                  # the new repo
$TMP  = Join-Path $WORK "throwaway-angular-repo-v2"     # test consumer repo
$env:GH_TOKEN = "<fine-grained PAT: Contents Read + Issues Read on the source repos>"
```

### Tools to check

```powershell
pwsh --version          # 7.x
git --version
uv --version            # already present (you use it for specify-cli)
specify --version       # 1.0.12
specify extension add --help    # confirm the local-install flag name (expected: --dev)
node --version          # optional, only for the MCP Inspector smoke test
```

### Ask your admin first

Copilot Business and Enterprise orgs have a policy for **MCP servers in Copilot**. If it is disabled, VS Code will list the server but Copilot won't call its tools. Check this before you start.

### Design decisions behind the scripts

- **The venv lives outside OneDrive.** It goes in `%LOCALAPPDATA%\docs-to-spec\venv` on Windows and `~/.local/share/docs-to-spec/venv` on Linux/macOS. A Python venv inside a OneDrive-synced folder syncs thousands of files and gets file locks. The wiki clone cache also lives outside OneDrive, in `%LOCALAPPDATA%\docs-to-spec\cache`.
- **VS Code launches the server `.exe` directly** from `.vscode/mcp.json`, not through a PowerShell wrapper. MCP uses stdio, and a `pwsh` wrapper can re-encode or buffer stdout and corrupt the protocol. The `run-mcp` scripts are only for manual testing.
- **Redaction happens inside the server.** The agent only ever sees redacted text, and the snapshot on disk is redacted too. The server reports counts of redactions, never the values.
- **`.vscode/mcp.json` is generated per machine and git-ignored**, because it contains the absolute path to your venv.
- **The GitHub token is never stored on disk.** VS Code prompts for it when the server starts (a password-type input). Scripts read `$env:GH_TOKEN` for the session.

---

## Phase 1: Create the repo and its layout

1. Create an empty private repo `docs-to-spec` in the GitHub web UI under your account, with no README. Then clone it:

   ```powershell
   cd $WORK
   git clone https://github.com/Raamesh-Bhardwaj-UST/docs-to-spec.git
   cd $D2S
   ```

2. Create the folders:

   ```powershell
   $dirs = "commands","scripts\powershell","scripts\bash","assets",
           "mcp-server\src\docs_to_spec_mcp","mcp-server\tests","evals"
   $dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }
   ```

3. Target layout:

   ```text
   docs-to-spec/
     extension.yml
     README.md
     LICENSE
     .gitignore
     commands/
       speckit.docs-to-spec.setup.md
       speckit.docs-to-spec.harvest.md
       speckit.docs-to-spec.extract.md
       speckit.docs-to-spec.review.md
       speckit.docs-to-spec.clarify.md
       speckit.docs-to-spec.propose.md
     scripts/
       powershell/  setup-mcp.ps1  run-mcp.ps1  harvest.ps1
       bash/        setup-mcp.sh   run-mcp.sh   harvest.sh
     assets/
       sources.template.yml
       requirements-rubric.md
       requirements-reviewer.agent.md
     mcp-server/
       pyproject.toml
       src/docs_to_spec_mcp/  __init__.py config.py redact.py sources.py snapshot.py server.py cli.py
       tests/test_redact.py
     evals/README.md
   ```

4. Create **`.gitignore`**:

   ```gitignore
   .venv/
   __pycache__/
   *.egg-info/
   dist/
   .pytest_cache/
   ```

---

## Phase 2: The MCP server (Python)

### `mcp-server/pyproject.toml`

```toml
[project]
name = "docs-to-spec-mcp"
version = "0.1.0"
description = "Local MCP server that harvests wikis, issues and docs into a redacted snapshot for Spec Kit"
requires-python = ">=3.11"
dependencies = [
  "mcp>=1.2",
  "httpx>=0.27",
  "pyyaml>=6",
]

[project.scripts]
docs-to-spec-mcp = "docs_to_spec_mcp.server:main"
docs-to-spec = "docs_to_spec_mcp.cli:main"

[dependency-groups]
dev = ["pytest>=8"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/docs_to_spec_mcp"]
```

### `mcp-server/src/docs_to_spec_mcp/__init__.py`

```python
__version__ = "0.1.0"
```

### `mcp-server/src/docs_to_spec_mcp/config.py`

```python
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
```

### `mcp-server/src/docs_to_spec_mcp/redact.py`

```python
"""Best-effort redaction of credentials and personal identifiers.

Runs on every document before it is returned to the agent or written to disk.
Patterns are deliberately broad: a false positive costs a look at the source,
a false negative leaks data. Only counts are ever reported, never matched values.
Sources that hold health or HR records should be excluded in sources.yml instead
of relying on redaction.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Callable, Optional, Union

Replacement = Union[None, str, Callable[[re.Match], Optional[str]]]


def _luhn_ok(digits: str) -> bool:
    total, double = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if double:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        double = not double
    return total % 10 == 0


def _card(match: re.Match) -> Optional[str]:
    digits = re.sub(r"\D", "", match.group(0))
    if 13 <= len(digits) <= 19 and _luhn_ok(digits):
        return "[REDACTED:card]"
    return None  # not a card number; leave unchanged


_RULES: list[tuple[str, re.Pattern, Replacement]] = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), None),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})"), None),
    ("aws_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), None),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), None),
    ("bearer", re.compile(r"(?i)\bbearer\s+(?!\[REDACTED)[A-Za-z0-9\-._~+/]{20,}=*"), "Bearer [REDACTED:bearer]"),
    ("url_credentials", re.compile(r"(?i)\b([a-z][a-z0-9+.\-]*://)[^\s/:@]+:[^\s/@]+@"), r"\1[REDACTED:credentials]@"),
    ("secret", re.compile(
        r"(?i)\b(password|passwd|pwd|secret|client[_-]?secret|api[_-]?key)(\s*[:=]\s*)([\"']?)(?!\[REDACTED)[^\s\"']{3,}\3"),
        r"\1\2[REDACTED:secret]"),
    ("secret", re.compile(
        r"(?i)\b([a-z_\-]*token)(\s*[:=]\s*)([\"']?)(?!\[REDACTED)[^\s\"']{16,}\3"),
        r"\1\2[REDACTED:secret]"),
    ("card", re.compile(r"\b\d(?:[ -]?\d){12,18}\b"), _card),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), None),
    ("aadhaar", re.compile(r"\b[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}\b"), None),
    ("pan", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), None),
    ("passport", re.compile(r"\b[A-Z]\d{7}\b"), None),
    ("driving_licence", re.compile(r"\b[A-Z]{2}[ -]?\d{2}[ -]?(?:19|20)\d{2}[ -]?\d{7}\b"), None),
    ("medical_record", re.compile(
        r"(?i)\b(MRN|medical record (?:number|no\.?)|patient (?:id|name|number))(\s*[:=#]\s*)[^\n]+"),
        r"\1\2[REDACTED:medical_record]"),
]

_EMAIL = ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), None)


def redact(text: str, emails: bool = False) -> tuple[str, dict[str, int]]:
    """Return (redacted_text, counts_by_type)."""
    if not text:
        return text, {}
    counts: Counter[str] = Counter()
    rules = _RULES + ([_EMAIL] if emails else [])
    for name, pattern, repl in rules:
        def _sub(match: re.Match, name=name, repl=repl) -> str:
            if callable(repl):
                out = repl(match)
                if out is None:
                    return match.group(0)
            elif isinstance(repl, str):
                out = match.expand(repl)
            else:
                out = f"[REDACTED:{name}]"
            counts[name] += 1
            return out
        text = pattern.sub(_sub, text)
    return text, dict(counts)
```

### `mcp-server/src/docs_to_spec_mcp/sources.py`

```python
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
```

### `mcp-server/src/docs_to_spec_mcp/snapshot.py`

```python
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
```

### `mcp-server/src/docs_to_spec_mcp/server.py`

```python
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
```

### `mcp-server/src/docs_to_spec_mcp/cli.py`

```python
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
```

### `mcp-server/tests/test_redact.py`

The test values below are built in code from format placeholders. They are not real identifiers.

```python
from docs_to_spec_mcp.redact import _luhn_ok, redact


def _luhn_complete(prefix: str) -> str:
    for digit in "0123456789":
        if _luhn_ok(prefix + digit):
            return prefix + digit
    raise AssertionError("unreachable")


def test_plain_requirement_untouched():
    text = "When the user saves a draft, the system shall show a confirmation within 2 seconds."
    out, counts = redact(text)
    assert out == text and counts == {}


def test_github_token():
    fake = "ghp_" + "a" * 36
    out, counts = redact(f"use {fake} here")
    assert fake not in out and counts["github_token"] == 1


def test_secret_assignment_keeps_key():
    out, counts = redact("api_key = not-a-real-value")
    assert out.startswith("api_key = [REDACTED:secret]") and counts["secret"] == 1


def test_card_needs_valid_checksum():
    valid = _luhn_complete("4" + "1" * 14)
    out, counts = redact(f"card {valid}")
    assert valid not in out and counts["card"] == 1
    invalid = valid[:-1] + str((int(valid[-1]) + 1) % 10)
    assert redact(f"ref {invalid}")[1].get("card") is None


def test_pan_format():
    fake = "A" * 5 + "0" * 4 + "A"
    assert redact(f"id {fake}")[1]["pan"] == 1


def test_aadhaar_format():
    fake = "2" + "0" * 11
    assert redact(f"id {fake}")[1]["aadhaar"] == 1


def test_url_credentials():
    out, counts = redact("https://user:pass@example.com/x")
    assert "user:pass" not in out and counts["url_credentials"] == 1
```

### Build and test the server locally

```powershell
cd "$D2S\mcp-server"
$env:UV_PROJECT_ENVIRONMENT = Join-Path $env:LOCALAPPDATA "docs-to-spec\dev-venv"
uv sync                      # creates uv.lock; commit it
uv run pytest -q
```

---

## Phase 3: Scripts (PowerShell and bash)

All scripts find the extension folder from their own location. They work both from the `docs-to-spec` clone and from the installed copy at `.specify/extensions/docs-to-spec/`.

### `scripts/powershell/setup-mcp.ps1`

```powershell
#Requires -Version 7.0
<#
.SYNOPSIS
  Installs the docs-to-spec MCP server and wires it into a repo.
.DESCRIPTION
  - Creates the server venv outside OneDrive (default %LOCALAPPDATA%\docs-to-spec\venv)
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
$Venv = if ($env:DOCS_TO_SPEC_VENV) { $env:DOCS_TO_SPEC_VENV } else { Join-Path $env:LOCALAPPDATA 'docs-to-spec\venv' }

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

# 4. Keep the per-machine mcp.json out of git.
$gi = Join-Path $WorkspaceRoot '.gitignore'
$entry = '.vscode/mcp.json'
$existing = if (Test-Path $gi) { Get-Content $gi } else { @() }
if ($existing -notcontains $entry) {
  $prefix = ''
  if ((Test-Path $gi) -and -not (Get-Content -Raw $gi).EndsWith("`n")) { $prefix = "`n" }
  [IO.File]::AppendAllText($gi, "$prefix$entry`n", [Text.UTF8Encoding]::new($false))
  Write-Host "added $entry to .gitignore"
}

Write-Host ""
Write-Host "Next:"
Write-Host "  1. Edit .specify/docs-to-spec/sources.yml"
Write-Host "  2. In VS Code open .vscode/mcp.json and click Start above 'docs-to-spec' (or run 'MCP: List Servers')"
Write-Host "  3. In Copilot Chat (agent mode) enable the docs-to-spec tools, then run /speckit-docs-to-spec-harvest"
```

### `scripts/powershell/run-mcp.ps1`

```powershell
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
$Venv = if ($env:DOCS_TO_SPEC_VENV) { $env:DOCS_TO_SPEC_VENV } else { Join-Path $env:LOCALAPPDATA 'docs-to-spec\venv' }
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
```

### `scripts/powershell/harvest.ps1`

This runs the snapshot without the agent. Use it as a fallback, in CI, and once interactively so Git Credential Manager can complete sign-in for wikis.

```powershell
#Requires -Version 7.0
[CmdletBinding()]
param([string]$WorkspaceRoot, [string]$Source)
$ErrorActionPreference = 'Stop'

if (-not $WorkspaceRoot) {
  $WorkspaceRoot = git rev-parse --show-toplevel 2>$null
  if (-not $WorkspaceRoot) { $WorkspaceRoot = (Get-Location).Path }
}
$WorkspaceRoot = (Resolve-Path $WorkspaceRoot).Path
$Venv = if ($env:DOCS_TO_SPEC_VENV) { $env:DOCS_TO_SPEC_VENV } else { Join-Path $env:LOCALAPPDATA 'docs-to-spec\venv' }
$Cli = Join-Path $Venv 'Scripts\docs-to-spec.exe'
if (-not (Test-Path $Cli)) { throw "Not installed. Run setup-mcp.ps1 first." }
if (-not $env:GH_TOKEN) { Write-Warning "GH_TOKEN is not set: private issues and 'auth: token' wikis will fail." }

$cliArgs = @('--root', $WorkspaceRoot, 'snapshot')
if ($Source) { $cliArgs += @('--source', $Source) }
& $Cli @cliArgs
$code = $LASTEXITCODE
& $Cli --root $WorkspaceRoot status
exit $code
```

### `scripts/bash/setup-mcp.sh`

```bash
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
VENV="${DOCS_TO_SPEC_VENV:-${XDG_DATA_HOME:-$HOME/.local/share}/docs-to-spec/venv}"

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
if ! grep -qxF '.vscode/mcp.json' "$GI" 2>/dev/null; then
  if [[ -s "$GI" && -n "$(tail -c1 "$GI")" ]]; then echo >> "$GI"; fi
  echo '.vscode/mcp.json' >> "$GI"
  echo "added .vscode/mcp.json to .gitignore"
fi

cat <<'EOF'

Next:
  1. Edit .specify/docs-to-spec/sources.yml
  2. In VS Code open .vscode/mcp.json and click Start above 'docs-to-spec' (or run 'MCP: List Servers')
  3. In Copilot Chat (agent mode) enable the docs-to-spec tools, then run /speckit-docs-to-spec-harvest
EOF
```

### `scripts/bash/run-mcp.sh`

```bash
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
VENV="${DOCS_TO_SPEC_VENV:-${XDG_DATA_HOME:-$HOME/.local/share}/docs-to-spec/venv}"
SRV="$VENV/bin/docs-to-spec-mcp"
[[ -x "$SRV" ]] || { echo "Not installed. Run setup-mcp.sh first." >&2; exit 1; }
export DOCS_TO_SPEC_ROOT="$(cd "$ROOT" && pwd)"
[[ -n "${GH_TOKEN:-}" ]] || echo "Note: GH_TOKEN is not set for this session." >&2
if [[ "$INSPECT" -eq 1 ]]; then exec npx -y @modelcontextprotocol/inspector "$SRV"; fi
echo "docs-to-spec MCP server on stdio for $DOCS_TO_SPEC_ROOT (Ctrl+C to stop)" >&2
exec "$SRV"
```

### `scripts/bash/harvest.sh`

```bash
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
VENV="${DOCS_TO_SPEC_VENV:-${XDG_DATA_HOME:-$HOME/.local/share}/docs-to-spec/venv}"
CLI="$VENV/bin/docs-to-spec"
[[ -x "$CLI" ]] || { echo "Not installed. Run setup-mcp.sh first." >&2; exit 1; }
[[ -n "${GH_TOKEN:-}" ]] || echo "Warning: GH_TOKEN is not set: private issues and 'auth: token' wikis will fail." >&2
ARGS=(--root "$ROOT" snapshot)
[[ -n "$SOURCE" ]] && ARGS+=(--source "$SOURCE")
set +e; "$CLI" "${ARGS[@]}"; CODE=$?; set -e
"$CLI" --root "$ROOT" status
exit "$CODE"
```

Mark the bash scripts executable in git, since Windows won't do it for you:

```powershell
cd $D2S
git add scripts/bash/*.sh
git update-index --chmod=+x scripts/bash/setup-mcp.sh scripts/bash/run-mcp.sh scripts/bash/harvest.sh
```

---

## Phase 4: Assets

### `assets/sources.template.yml`

```yaml
# docs-to-spec sources. Patterns are fnmatch-style; '*' also matches '/'.
version: 1
snapshot_dir: .specify/harvest/raw   # committed, so reviews and re-runs diff cleanly

redaction:
  emails: false          # set true to also redact e-mail addresses

sources:
  - id: product-wiki
    type: github-wiki
    repo: OWNER/REPO                 # the repo whose wiki you want
    auth: gcm                        # gcm = Git Credential Manager (recommended); token = GH_TOKEN
    include: ["*.md"]
    exclude: ["*_Sidebar.md", "*_Footer.md"]

  - id: feature-requests
    type: github-issues
    repo: OWNER/REPO
    state: open                      # open | closed | all
    labels: ["feature-request"]      # multiple labels = AND
    max_items: 200
    include_comments: true

  - id: repo-docs
    type: local
    path: docs                       # relative to the repo root
    include: ["*.md"]
    exclude: []
```

### `assets/requirements-rubric.md`

```markdown
# Requirements rubric (docs-to-spec)

Every harvested requirement is checked against this rubric. A requirement passes only if every criterion passes.

## Criteria (ISO/IEC/IEEE 29148 characteristics)

| ID | Criterion | Passes when |
|----|-----------|-------------|
| C1 | Singular | The statement expresses one requirement. No "and/or" joining two behaviours. |
| C2 | Unambiguous | Two engineers would build the same thing. No weak words (see list). |
| C3 | Verifiable | A concrete acceptance test with real values can be written for it. |
| C4 | Complete | Trigger, actor/system, response, and any limits or error behaviour are stated, or marked [NEEDS CLARIFICATION]. |
| C5 | Feasible | Nothing in the architecture file or sources makes it impossible as stated. |
| C6 | Traceable | Cites a snapshot file and section that actually supports it. |
| C7 | Implementation-free | States what, not how (no class names, libraries or UI widgets unless the source mandates them). |
| C8 | Consistent | Does not contradict another requirement; if it does, both are listed under Conflicts. |

## EARS patterns

- Ubiquitous: The <system> shall <response>.
- Event-driven: When <trigger>, the <system> shall <response>.
- State-driven: While <state>, the <system> shall <response>.
- Unwanted behaviour: If <condition>, then the <system> shall <response>.
- Optional feature: Where <feature is included>, the <system> shall <response>.
- Complex: combinations of the above, e.g. While <state>, when <trigger>, the <system> shall <response>.

## Weak words (each occurrence fails C2 unless quantified in the same sentence)

fast, quick, slow, responsive, efficient, user-friendly, easy, intuitive, simple, flexible, robust, reliable,
scalable, secure (unqualified), appropriate, adequate, reasonable, normal, as needed, as appropriate,
if possible, where possible, etc., and/or, support (as a verb without detail), handle, manage, process
(without detail), minimal, maximal, optimal, seamless, modern, best-in-class, state-of-the-art, some, several, many.

## Question ranking (for open questions)

1. Scope: changes what is built or for whom
2. Security / privacy: data exposure, access, retention
3. User experience: what the user sees or does
4. Technical detail: values, limits, formats

## Status values

confirmed | needs-clarification | inferred | assumed-pending-confirmation | needs-human
```

### `assets/requirements-reviewer.agent.md`

If your existing agents in `.github/agents/` use extra front-matter fields (for example `tools`), match them here.

```markdown
---
name: Requirements Reviewer
description: Adversarial reviewer for harvested requirements. Scores each requirement against the docs-to-spec rubric, runs test-first, round-trip and grounding checks, and proposes rewrites. Never invents requirements.
---

# Requirements Reviewer

You review `docs/requirements/harvested.md`. You are deliberately sceptical: your job is to find what is wrong, not to approve.

## Constraints

- Use `.specify/docs-to-spec/requirements-rubric.md` as the only definition of "good".
- Never add facts that are not in the cited snapshot file. If a fix needs information the sources don't have, the fix is a [NEEDS CLARIFICATION: ...] marker plus an open question, not a guess.
- Never copy secrets or personal data. Treat any `[REDACTED:*]` token as unknown content; do not guess it.
- Keep requirement IDs stable. Never renumber.

## Checks (run all, per requirement)

1. Rubric: score C1–C8 pass/fail. Quote the exact failing words.
2. Test-first: write one Given/When/Then acceptance test with concrete values. If you cannot, C3 fails.
3. Round-trip: without re-reading the source, restate in one sentence what the requirement makes a developer build. Then open the cited snapshot file and compare. If the meanings differ, C2 or C6 fails; say how.
4. Grounding: confirm the cited file and section exist and support the statement. Unsupported → status `inferred`.
5. Misreading: name the single most likely way a developer would get this wrong, and whether the text prevents it.

## Output format

Write `docs/requirements/review.md`:

| ID | Score (x/8) | Failing criteria | Evidence (failing words) | Proposed rewrite or question |
|----|-------------|------------------|--------------------------|------------------------------|

Then a section "Acceptance tests (draft)" with one Given/When/Then per passing requirement, and a section "Needs human" for anything still failing after two revision loops.
```

---

## Phase 5: Commands

Each command file has a short front matter and a body that uses `$ARGUMENTS`. The commands call scripts by their installed path. If your existing extensions use the `scripts:` front-matter and `{SCRIPT}` placeholder instead, switch to that pattern for consistency.

### `commands/speckit.docs-to-spec.setup.md`

````markdown
---
description: "Install the docs-to-spec MCP server, create sources.yml, and copy the rubric and Requirements Reviewer agent"
---

## User input

```text
$ARGUMENTS
```

If the input contains `force`, pass `-Force` (PowerShell) or `--force` (bash).

## Steps

1. On Windows run:
   `pwsh -NoProfile -File .specify/extensions/docs-to-spec/scripts/powershell/setup-mcp.ps1`
   On Linux/macOS run:
   `bash .specify/extensions/docs-to-spec/scripts/bash/setup-mcp.sh`
2. If the script fails, show its last error line and stop. Do not modify the environment yourself.
3. Report each file the script wrote or skipped.
4. Tell the user the manual next steps, exactly:
   - Edit `.specify/docs-to-spec/sources.yml` (replace OWNER/REPO, remove sources you don't need).
   - For wiki sources with `auth: gcm`, run `harvest.ps1` / `harvest.sh` once from a terminal so Git Credential Manager can sign in.
   - Start the server: open `.vscode/mcp.json` and click **Start** above `docs-to-spec`, or run **MCP: List Servers**. Paste the GitHub token when prompted, or leave it empty.
   - In Copilot Chat agent mode, open the tools picker and enable the `docs-to-spec` tools.
   - Then run `/speckit-docs-to-spec-harvest`.
````

### `commands/speckit.docs-to-spec.harvest.md`

````markdown
---
description: "Fetch the configured sources through the docs-to-spec MCP server and write a redacted snapshot"
---

## User input

```text
$ARGUMENTS
```

Optional: a single source id to refresh.

## Rules

- Fetch only through the `docs-to-spec` MCP tools. Do not fetch sources any other way and do not paste source content into chat.
- Never print, reconstruct or guess redacted values. Report only the counts the tools return.

## Steps

1. Call `list_sources`. If the docs-to-spec tools are not available, stop and tell the user to start the server and enable its tools, or to run
   `pwsh -NoProfile -File .specify/extensions/docs-to-spec/scripts/powershell/harvest.ps1` (or `bash .../scripts/bash/harvest.sh`) and then re-run this command with `status`.
2. If the input is `status`, skip to step 4. If it names a source id, call `snapshot_source` with it; otherwise call `snapshot_all`.
3. If any source returned an error, show a table of source and error with the likely fix:
   - git auth or 403 on a wiki → run the harvest script once from a terminal (Credential Manager sign-in) or switch `auth`.
   - 404 on a wiki → the wiki is disabled or has no pages, or you lack access.
   - 401/403 on issues → GH_TOKEN missing or lacks Issues: Read on that repo.
4. Call `snapshot_status` and show a table: source, type, documents, fetched_at, redactions.
5. If any redactions are non-zero, say how many and that the values were replaced with `[REDACTED:<type>]` tokens.
6. **Gate.** Tell the user to review `.specify/harvest/raw/manifest.json` and a sample of files, then commit the snapshot before running `/speckit-docs-to-spec-extract`. Stop here.
````

### `commands/speckit.docs-to-spec.extract.md`

This command contains the gap-handling requirements FR-Q1 to FR-Q6.

````markdown
---
description: "Extract EARS requirements with citations and ranked open questions from the redacted snapshot. Never guesses."
---

## User input

```text
$ARGUMENTS
```

Optional: a focus (for example `export and reporting only`). Default: everything in the snapshot.

## Inputs

- Snapshot: `.specify/harvest/raw/**` and `manifest.json`. Read only these files. Do not fetch anything new.
- Rubric: `.specify/docs-to-spec/requirements-rubric.md`.
- Optional: `.github/instructions/architecture.instructions.md` (to note stated vs implemented).
- Existing output: `docs/requirements/harvested.md`, if present.

## Rules

1. **No guessing.** Where a requirement lacks a trigger, actor, value, limit, error behaviour or success criterion, keep it, add an inline `[NEEDS CLARIFICATION: <specific question>]` marker, and do not infer the missing detail.
2. Every requirement cites its source as `[<source_id>/<doc_id> § <heading>](<url>)` and the snapshot file path.
3. Write statements in EARS form (see rubric). One requirement per statement.
4. Questions come before assumptions. Only record an assumption when a question has been explicitly deferred (see clarify), under "Assumed, pending confirmation".
5. Rank open questions: scope > security/privacy > user experience > technical detail. Link each to the requirement IDs and citations it affects.
6. Never copy secrets or personal data. Treat `[REDACTED:*]` as unknown.
7. **Stable IDs.** If `harvested.md` exists, keep the IDs of requirements whose source and meaning are unchanged, mark removed ones `withdrawn`, and give new ones the next free number. Never renumber.
8. Requirements found in more than one source are merged, with all citations listed. Contradictions go under Conflicts, not resolved silently.

## Output: `docs/requirements/harvested.md`

```markdown
# Harvested requirements

Snapshot: <manifest generated_at> · Sources: <ids> · Focus: <focus>

## Requirements

### REQ-001 <short title>
- **Statement:** When <trigger>, the <system> shall <response>. [NEEDS CLARIFICATION: ...]
- **Type:** functional | non-functional (<category>)
- **Status:** confirmed | needs-clarification | inferred
- **Sources:** [product-wiki/Export § Formats](url) — `.specify/harvest/raw/product-wiki/Export.md`
- **Evidence:** <one-line paraphrase of what the source says>
- **Stated vs implemented:** <only if the architecture file says something relevant>

## Conflicts
| Conflict | Requirements | Sources | Question ID |

## Open questions (ranked)
| QID | Rank | Impact | Question | Affects | Source | State |
(State: open | asked | answered | deferred)

## Assumed, pending confirmation
## Inferred (no direct source)
## Clarification log
| Date | QID | Answer (summary) | Answered by | Requirements updated |
```

## Finish

Report counts: requirements by status, conflicts, open questions by rank. Suggest `/speckit-docs-to-spec-review` next.
````

### `commands/speckit.docs-to-spec.review.md`

````markdown
---
description: "Run the Requirements Reviewer agent instructions against harvested.md (rubric, test-first, round-trip, grounding), with at most two revision loops"
---

## User input

```text
$ARGUMENTS
```

## Steps

1. Check that `.github/agents/requirements-reviewer.agent.md` exists. If not, tell the user to run `/speckit-docs-to-spec-setup` and stop.
2. Read that file in full and follow its Constraints, Checks and Output Format against `docs/requirements/harvested.md`.
3. **Loop (maximum 2 times):** apply the proposed rewrites that need no new information to `harvested.md`, keeping IDs. For rewrites that need information, add a `[NEEDS CLARIFICATION]` marker and an open question instead. Re-run the checks on changed requirements only.
4. After the second loop, set any requirement still failing to status `needs-human` and list it under "Needs human" in `review.md`.
5. Report: requirements passing 8/8, average score, weak-word hits, requirements without a possible acceptance test, inferred count, and new open questions. Suggest `/speckit-docs-to-spec-clarify` next.
````

### `commands/speckit.docs-to-spec.clarify.md`

This command contains FR-Q4 to FR-Q7.

````markdown
---
description: "Ask the top-ranked open questions (at most five per round), write the answers back into the requirements, and log them"
---

## User input

```text
$ARGUMENTS
```

Optional: specific QIDs to ask instead of the top-ranked ones.

## Steps

1. Read the Open questions table in `docs/requirements/harvested.md`. Select open questions by rank (or the QIDs given), **at most five**. Leave the rest queued and say how many remain.
2. Ask them. If an interactive question tool is available in this chat (for example Copilot's ask-user tool, as used by the copilot-assess-ask-questions preset), use it, with short answer options where the question allows. Otherwise ask them as a numbered list in one message and wait for the answers.
   For each question, also allow the answer "defer".
3. For each answer:
   - Update the affected requirements, remove the matching `[NEEDS CLARIFICATION]` marker, and set status `confirmed` when no markers remain.
   - Set the question's state to `answered` and add a Clarification log row with today's date (ISO), a one-line summary, the respondent (from `git config user.name`, or ask), and the requirement IDs updated.
4. For each "defer": set state `deferred`. If work must proceed, record the working assumption under "Assumed, pending confirmation" with the QID, and set the requirement status `assumed-pending-confirmation`. Never present an assumption as a confirmed requirement.
5. Never copy secrets or personal data from answers into the file. If an answer contains any, summarise without the value.
6. Report what changed. If questions remain, offer another round; otherwise suggest `/speckit-docs-to-spec-review` once more, then `/speckit-docs-to-spec-propose`.
````

### `commands/speckit.docs-to-spec.propose.md`

````markdown
---
description: "Group confirmed requirements into candidate features and write ready-to-run assess and specify prompts"
---

## User input

```text
$ARGUMENTS
```

Optional: a candidate number to start immediately.

## Steps

1. Read `docs/requirements/harvested.md` and `docs/requirements/review.md`. Use only requirements with status `confirmed` or `assumed-pending-confirmation`. List any `needs-clarification` or `needs-human` ones as blockers.
2. Group them into 3–7 candidate features. Rank by value and readiness (fewest open questions first).
3. For each candidate, write:
   - title, slug (kebab-case), requirement IDs, open blockers, main risk
   - an assess prompt:
     `/speckit-assess-intake "<one-paragraph idea>. Grounded in docs/requirements/harvested.md <REQ IDs>; sources <snapshot files>. Research local snapshot and codebase first." slug=<slug>`
   - a specify prompt containing the requirement statements verbatim, plus:
     "Do not invent details. Keep every [NEEDS CLARIFICATION] marker. Cite REQ IDs in the spec."
4. Write `docs/requirements/candidates.md`.
5. If `.specify/extensions/assess` does not exist, say so and suggest `specify extension add assess`; keep the specify prompts as the main path.
6. If the input names a candidate number, run its assess intake (or its specify prompt if assess isn't installed).
7. **Gate.** Remind the user to review `candidates.md` before starting any spec.
````

---

## Phase 6: Manifest, README and evals

### `extension.yml`

```yaml
schema_version: "1.0"

extension:
  id: "docs-to-spec"
  name: "Docs to Spec"
  version: "1.0.0"
  description: "Harvest wikis, issues and docs via a local MCP server, extract cited EARS requirements, review them, clarify gaps, and propose specs."
  author: "Raamesh Bhardwaj (UST PACE)"
  repository: "https://github.com/Raamesh-Bhardwaj-UST/docs-to-spec"
  license: "MIT"

requires:
  speckit_version: ">=1.0.12"
  commands:
    - "speckit.specify"

provides:
  commands:
    - name: "speckit.docs-to-spec.setup"
      file: "commands/speckit.docs-to-spec.setup.md"
      description: "Install the MCP server, create sources.yml, copy rubric and reviewer agent"
    - name: "speckit.docs-to-spec.harvest"
      file: "commands/speckit.docs-to-spec.harvest.md"
      description: "Snapshot configured sources (redacted) through the MCP server"
    - name: "speckit.docs-to-spec.extract"
      file: "commands/speckit.docs-to-spec.extract.md"
      description: "Extract cited EARS requirements and ranked open questions"
    - name: "speckit.docs-to-spec.review"
      file: "commands/speckit.docs-to-spec.review.md"
      description: "Review requirements against the rubric with the Requirements Reviewer agent"
    - name: "speckit.docs-to-spec.clarify"
      file: "commands/speckit.docs-to-spec.clarify.md"
      description: "Ask up to five ranked questions and write answers back"
    - name: "speckit.docs-to-spec.propose"
      file: "commands/speckit.docs-to-spec.propose.md"
      description: "Propose candidate features with assess and specify prompts"

tags: ["requirements", "wiki", "mcp", "ears", "brownfield", "ust"]
```

Check that the description is 200 characters or fewer, and that the command names follow `speckit.{extension-id}.{command}`.

### `README.md` (outline)

Write sections for:
- what it does
- prerequisites (including the Copilot MCP policy)
- install
- setup
- `sources.yml` reference
- the command order with gates
- redaction (what is caught, that it is best-effort, and to exclude health or HR sources entirely)
- the manual `mcp.json` entry for files with comments (copy the JSON block from Phase 2's `configure_vscode`)
- troubleshooting

### `evals/README.md`

```markdown
# Evaluation set

1. Pick 10–15 source pages where the correct requirements are known.
2. For each, create `evals/<case>/source.md` (a redacted copy) and `evals/<case>/expected.md` (the agreed requirement statements and expected open questions).
3. After any change to the commands, rubric or reviewer agent, run harvest (as a `local` source pointing at `evals`), extract and review, then record per case:
   requirements found / missed / extra, weak-word hits, requirements without citation, requirements without a possible acceptance test, invented values (must be 0).
4. Keep the results table in `evals/results.md` with the date and commit.
```

Add an MIT `LICENSE` file, or whatever licence your team uses.

---

## Phase 7: Test locally before installing anywhere

1. Run the unit tests (if you didn't already in Phase 2):

   ```powershell
   cd "$D2S\mcp-server"; uv run pytest -q
   ```

2. Run the server against a scratch folder with the Inspector:

   ```powershell
   $scratch = Join-Path $env:TEMP "d2s-scratch"
   New-Item -ItemType Directory -Force "$scratch\docs", "$scratch\.specify\docs-to-spec" | Out-Null
   Set-Content "$scratch\docs\export.md" "# Export`nThe export should be fast. Users can export reports as CSV.`napi_key = not-a-real-value" -Encoding utf8
   @"
   version: 1
   sources:
     - id: repo-docs
       type: local
       path: docs
   "@ | Set-Content "$scratch\.specify\docs-to-spec\sources.yml" -Encoding utf8
   cd $scratch; git init -q
   & "$D2S\scripts\powershell\setup-mcp.ps1" -WorkspaceRoot $scratch
   & "$D2S\scripts\powershell\run-mcp.ps1" -WorkspaceRoot $scratch -Inspect
   ```

   In the Inspector, connect, call `snapshot_all`, then `snapshot_status`. Expected result: 1 document and 1 redaction (`secret`). The file `.specify\harvest\raw\repo-docs\export.md` should contain `api_key = [REDACTED:secret]`.

3. Run the CLI fallback:

   ```powershell
   & "$D2S\scripts\powershell\harvest.ps1" -WorkspaceRoot $scratch
   ```

---

## Phase 8: Install into the throwaway repo and run end to end

1. Prepare the test repo:

   ```powershell
   cd $TMP
   git checkout main; git pull; git status          # clean
   git checkout -b try/docs-to-spec
   specify extension add --dev $D2S                 # confirm the flag from `specify extension add --help`
   Get-ChildItem .specify\extensions\docs-to-spec   # must include mcp-server\ and scripts\
   ```

   If `mcp-server\` was not copied, run setup with `-ServerDir "$D2S\mcp-server"`. Everything else still works.

2. Add test material. Enable the wiki on the throwaway repo (Settings → Features → Wikis) and create a page **Export** with:

   ```text
   The export should be fast. Users can export reports as CSV or Excel.
   Only admins can export audit data.
   ```

   Also create `docs/notes.md` in the repo with a second, conflicting line: "Any signed-in user can export audit data."

3. **Copilot Chat:** run setup.

   ```text
   /speckit-docs-to-spec-setup
   ```

4. Edit `.specify\docs-to-spec\sources.yml`:
   - Set the wiki `repo` to `Raamesh-Bhardwaj-UST/throwaway-angular-repo-v2`.
   - Keep the `repo-docs` source.
   - Delete the issues source, or point it at a repo with labelled issues.

5. Do the first wiki sign-in from a terminal, then commit:

   ```powershell
   & .specify\extensions\docs-to-spec\scripts\powershell\harvest.ps1
   git add -A; git commit -m "docs-to-spec: setup and first snapshot"
   ```

6. Start the server in VS Code and enable the tools:
   - Open `.vscode\mcp.json` → **Start** above `docs-to-spec`.
   - Paste the token, or leave it empty.
   - In agent mode, open the tools picker → enable `docs-to-spec`.

7. **Copilot Chat:** run the pipeline, committing after each step so every step has its own diff.

   ```text
   /speckit-docs-to-spec-harvest
   /speckit-docs-to-spec-extract
   /speckit-docs-to-spec-review
   /speckit-docs-to-spec-clarify
   /speckit-docs-to-spec-review
   /speckit-docs-to-spec-propose
   ```

8. Acceptance checks (these are the FR-Q tests):

   | Check | Pass when |
   |---|---|
   | No guessing (FR-Q1) | "export should be fast" produces a `[NEEDS CLARIFICATION]` asking for a target time and data size, and there is no invented number anywhere in `harvested.md`. |
   | Ranking (FR-Q2/Q3) | The admin vs. any-user conflict appears under Conflicts and as a question ranked above the performance question (security beats technical detail). |
   | Five per round (FR-Q4) | Clarify asks five or fewer questions and reports how many remain queued. |
   | Write-back (FR-Q5) | After answering, the marker is gone, the status is `confirmed`, and the log row has a date and respondent. |
   | Deferral (FR-Q6) | A deferred answer appears only under "Assumed, pending confirmation". |
   | Ask tool (FR-Q7) | If the interactive tool is available, questions arrive as tappable options. |
   | Redaction | `api_key = ...` style test lines show `[REDACTED:secret]` in the snapshot and never appear in chat. |
   | Stable IDs | Re-running extract after editing the wiki keeps existing REQ IDs. |

9. Review the full diff, then either keep the branch or delete it:

   ```powershell
   git diff main --stat
   ```

---

## Phase 9: Commit, tag and publish docs-to-spec

1. Commit and tag:

   ```powershell
   cd $D2S
   git add -A
   git status              # no .venv, no __pycache__
   git commit -m "docs-to-spec 1.0.0: MCP harvest, extract, review, clarify, propose"
   git tag v1.0.0
   git push origin main; git push origin v1.0.0
   ```

2. In the GitHub web UI: **Releases → Draft new release** → tag `v1.0.0` → publish.

3. Choose how teams install it:
   - **Simplest:** they clone `docs-to-spec` and run `specify extension add --dev <clone path>`.
   - **Through your catalog:** add `docs-to-spec` to the `speckit-ust-sdd` extensions catalog with your existing `release.py` flow. Run it once, upload the zips, and check the sha256. Teams then get it with the same `catalog add` and `--install-allowed` steps they already use, and it uses the private-repo auth you already set up in `auth.json`. You can also list it in the `ust-sdd` bundle later.
   - Installing straight from the GitHub archive URL of a private repo redirects to `codeload.github.com`. Your `auth.json` doesn't list that host, so test this before relying on it.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Server shows in VS Code but Copilot never calls its tools | The org's MCP policy is off, or the tools aren't enabled in the agent tools picker. |
| Server fails to start | Output panel → **MCP: docs-to-spec** for the error. Re-run setup. Check that the exe path in `.vscode/mcp.json` exists. |
| `uv sync` fails with "access denied" | The server is running and Windows has locked the exe. Stop it in VS Code (MCP: List Servers → Stop) and re-run setup. |
| `uv` can't download Python | Use an installed interpreter: `setup-mcp.ps1 -Python "C:\path\to\python.exe"`. |
| Wiki clone 403/404 with `auth: token` | Fine-grained PATs may not cover wiki git access. Switch to `auth: gcm` and run `harvest.ps1` once from a terminal. |
| Harvest hangs or fails on wiki auth inside chat | Credential Manager needs an interactive sign-in. Run `harvest.ps1` from a terminal once, then retry. |
| Issues return 401/403 | The token is missing or lacks Issues: Read. Re-enter it: stop the server, start it, and paste the token at the prompt. |
| `configure-vscode` says mcp.json isn't plain JSON | The file has comments. Add the `docs-to-spec` server and input by hand, using the structure from `configure_vscode` in `cli.py`. |
| `.vscode/mcp.json` still tracked by git | It was committed before. `git rm --cached .vscode/mcp.json` and commit. |
| Corporate proxy blocks GitHub API calls | Set `HTTPS_PROXY` before starting VS Code; httpx honours it. |
| Too much text redacted | Patterns are deliberately broad. Tune `redact.py`, add a test, and re-release. Never weaken the PII rules. |
| Slash commands missing | Reload the VS Code window. Check `specify extension list`. |
| `extract` invents values | Re-run review. If it persists, add that page to `evals/` and tighten rule 1 in `extract.md`. |
