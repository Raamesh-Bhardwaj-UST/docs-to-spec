"""Confluence fetcher (Cloud and Data Center).

Pages are selected with CQL through /rest/api/content/search, which both Cloud and
Data Center provide. Each page body is then read in storage format: REST v2 on Cloud,
REST v1 on Data Center. Storage XHTML is converted to Markdown here; user mentions
become "@user", so no names or account ids reach the snapshot. Credentials come from
environment variables only and are never sent to any host other than base_url.
"""
from __future__ import annotations

import base64
import html
import os
import re
import time
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

from .sources import Document

_SEARCH_LIMIT = 50
_MAX_RETRIES = 3


# ---------- configuration ----------

def _settings(src: dict) -> tuple[str, str, str]:
    """Return (base_url, deployment, auth) for a confluence source."""
    base = str(src.get("base_url", "")).rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"Source '{src['id']}': base_url must be an https URL.")
    deployment = src.get("deployment") or (
        "cloud" if parsed.hostname.endswith(".atlassian.net") else "datacenter")
    if deployment not in ("cloud", "datacenter"):
        raise ValueError(f"Source '{src['id']}': deployment must be cloud or datacenter.")
    if deployment == "cloud" and not base.endswith("/wiki"):
        base += "/wiki"
    auth = src.get("auth") or ("basic" if deployment == "cloud" else "bearer")
    if auth not in ("basic", "bearer"):
        raise ValueError(f"Source '{src['id']}': auth must be basic or bearer.")
    return base, deployment, auth


def _auth_header(src: dict, auth: str) -> dict:
    token_env = src.get("token_env", "CONFLUENCE_TOKEN")
    token = os.environ.get(token_env)
    if not token:
        raise RuntimeError(f"Source '{src['id']}' needs {token_env} set "
                           "(Confluence API token on Cloud, personal access token on Data Center).")
    if auth == "bearer":
        return {"Authorization": f"Bearer {token}"}
    email_env = src.get("email_env", "CONFLUENCE_EMAIL")
    email = os.environ.get(email_env)
    if not email:
        raise RuntimeError(f"Source '{src['id']}' uses auth: basic but {email_env} is not set.")
    return {"Authorization": "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()}


def _quote(value) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_cql(src: dict) -> str:
    """CQL from space / ancestor / labels, or the source's own cql used as-is."""
    if src.get("cql"):
        return str(src["cql"])
    parts = ["type = page"]
    if src.get("space"):
        parts.append(f"space = {_quote(src['space'])}")
    if src.get("ancestor"):
        ancestor = str(src["ancestor"])
        if not ancestor.isdigit():
            raise ValueError(f"Source '{src['id']}': ancestor must be a numeric page id.")
        parts.append(f"ancestor = {ancestor}")
    for label in src.get("labels") or []:  # multiple labels = AND, as for GitHub issues
        parts.append(f"label = {_quote(label)}")
    if len(parts) == 1:
        raise ValueError(f"Source '{src['id']}': set space, ancestor, labels or cql "
                         "(refusing to harvest a whole Confluence site).")
    return " AND ".join(parts) + " ORDER BY lastmodified DESC"


# ---------- HTTP ----------

def _join(base: str, link: str) -> str:
    """Resolve a Confluence _links value against base_url; refuse other hosts."""
    b = urlparse(base)
    if link.startswith(("http://", "https://")):
        if urlparse(link).netloc != b.netloc:
            raise RuntimeError("Confluence returned a link to another host; refusing to follow it.")
        return link
    if b.path and link.startswith(b.path + "/"):
        return f"{b.scheme}://{b.netloc}{link}"
    return base + link


def _get(client: httpx.Client, url: str, params: dict | None = None) -> dict:
    for attempt in range(_MAX_RETRIES + 1):
        resp = client.get(url, params=params)
        if resp.status_code in (429, 503) and attempt < _MAX_RETRIES:
            delay = resp.headers.get("Retry-After", "")
            time.sleep(min(float(delay) if delay.isdigit() else 2.0 ** attempt, 30.0))
            continue
        if resp.status_code >= 400:
            raise RuntimeError(f"Confluence returned {resp.status_code} for {urlparse(url).path}")
        try:
            return resp.json()
        except ValueError:
            raise RuntimeError(f"Confluence did not return JSON for {urlparse(url).path}; "
                               "check base_url and credentials.") from None
    raise RuntimeError("unreachable")


def _page(client: httpx.Client, base: str, deployment: str, src: dict, page_id: str) -> Document:
    if deployment == "cloud":
        data = _get(client, f"{base}/api/v2/pages/{page_id}", {"body-format": "storage"})
    else:
        data = _get(client, f"{base}/rest/api/content/{page_id}", {"expand": "body.storage,version"})
    storage = ((data.get("body") or {}).get("storage") or {}).get("value") or ""
    title = data.get("title") or f"page {page_id}"
    webui = (data.get("_links") or {}).get("webui")
    body = storage_to_markdown(storage)
    return Document(
        source_id=src["id"],
        doc_id=f"page-{page_id}",
        title=title,
        url=_join(base, webui) if webui else f"{base}/pages/viewpage.action?pageId={page_id}",
        body=f"# {title}\n\n{body}",
        revision=str((data.get("version") or {}).get("number", "")),
    )


def confluence_documents(src: dict, transport: httpx.BaseTransport | None = None) -> list[Document]:
    base, deployment, auth = _settings(src)
    max_items = int(src.get("max_items", 200))
    headers = {"Accept": "application/json", "User-Agent": "docs-to-spec-mcp", **_auth_header(src, auth)}
    with httpx.Client(headers=headers, timeout=30, follow_redirects=False, transport=transport) as client:
        ids: list[str] = []
        url: str | None = f"{base}/rest/api/content/search"
        params: dict | None = {"cql": build_cql(src), "limit": _SEARCH_LIMIT}
        while url and len(ids) < max_items:
            data = _get(client, url, params)
            for item in data.get("results", []):
                page_id = str(item.get("id", ""))
                if item.get("type", "page") == "page" and page_id.isdigit() and page_id not in ids:
                    ids.append(page_id)
            nxt = (data.get("_links") or {}).get("next")
            url, params = (_join(base, nxt), None) if nxt else (None, None)
        return [_page(client, base, deployment, src, pid) for pid in ids[:max_items]]


# ---------- storage format -> Markdown ----------

_CDATA = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)
_DROP = {"ac:parameter", "ac:task-id", "ac:task-status", "ac:placeholder", "ac:emoticon"}
_CALLOUTS = {"info", "note", "tip", "warning", "panel"}
_CODE_MACROS = {"code", "noformat"}


class _StorageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.lists: list[list] = []      # [tag, counter]
        self.drop = 0                    # inside elements whose text is not content
        self.pre = 0
        self.rows: list[list[str]] | None = None
        self.cell: list[str] | None = None
        self.hrefs: list[str | None] = []
        self.macros: list[str] = []
        self.link: dict | None = None
        self.glue = False                # keep the next paragraph on the current line

    # output helpers
    def write(self, text: str) -> None:
        if self.drop:
            return
        if self.cell is not None:
            self.cell.append(text)
        else:
            self.out.append(text)

    def block(self, sep: str = "\n\n") -> None:
        if self.cell is not None:
            self.cell.append(" ")
        elif not self.drop:
            self.out.append(sep)

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        if tag in _DROP:
            self.drop += 1
        elif re.fullmatch(r"h[1-6]", tag):
            self.block()
            self.write("#" * int(tag[1]) + " ")
        elif tag in ("p", "div"):
            if self.glue:
                self.glue = False
            elif not self.lists:
                self.block()
        elif tag == "br":
            self.write(" " if self.cell is not None else "\n")
        elif tag in ("ul", "ol", "ac:task-list"):
            if not self.lists:
                self.block("\n")
            self.lists.append([tag, 0])
        elif tag == "li":
            self.block("\n")
            kind = self.lists[-1] if self.lists else ["ul", 0]
            kind[1] += 1
            indent = "  " * max(len(self.lists) - 1, 0)
            self.write(indent + (f"{kind[1]}. " if kind[0] == "ol" else "- "))
        elif tag == "ac:task-body":
            self.block("\n")
            self.write("  " * max(len(self.lists) - 1, 0) + "- [ ] ")
        elif tag == "table":
            self.block()
            self.rows = []
        elif tag == "tr" and self.rows is not None:
            self.rows.append([])
        elif tag in ("th", "td") and self.rows is not None:
            self.cell = []
        elif tag == "pre":
            self.block()
            self.write("```\n")
            self.pre += 1
        elif tag == "code" and not self.pre:
            self.write("`")
        elif tag in ("strong", "b"):
            self.write("**")
        elif tag in ("em", "i"):
            self.write("_")
        elif tag == "a":
            href = a.get("href") or ""
            self.hrefs.append(href if href.startswith(("http://", "https://")) else None)
            if self.hrefs[-1]:
                self.write("[")
        elif tag == "time" and a.get("datetime"):
            self.write(a["datetime"])
        elif tag == "ac:structured-macro":
            name = (a.get("ac:name") or "").lower()
            self.macros.append(name)
            if name in _CODE_MACROS:
                self.block()
                self.write("```\n")
                self.pre += 1
            elif name in _CALLOUTS:
                self.block()
                self.write(f"**{name.capitalize()}:** ")
                self.glue = True
        elif tag == "ac:image":
            self.write("[image]")
            self.drop += 1
        elif tag == "ac:link":
            self.link = {"title": None, "body": False}
        elif tag in ("ac:link-body", "ac:plain-text-link-body") and self.link is not None:
            self.link["body"] = True
        elif tag == "ri:page" and self.link is not None:
            self.link["title"] = a.get("ri:content-title")
        elif tag == "ri:attachment" and self.link is not None:
            self.link["title"] = a.get("ri:filename")
        elif tag == "ri:user":
            self.write("@user")
            if self.link is not None:
                self.link["body"] = True

    def handle_endtag(self, tag: str) -> None:
        if tag in _DROP or tag == "ac:image":
            self.drop = max(self.drop - 1, 0)
        elif re.fullmatch(r"h[1-6]", tag) or (tag in ("p", "div") and not self.lists):
            self.block()
        elif tag in ("ul", "ol", "ac:task-list"):
            if self.lists:
                self.lists.pop()
            if not self.lists:
                self.block()
        elif tag in ("th", "td") and self.cell is not None and self.rows is not None:
            text = re.sub(r"\s+", " ", "".join(self.cell)).strip().replace("|", "\\|")
            if not self.rows:
                self.rows.append([])
            self.rows[-1].append(text)
            self.cell = None
        elif tag == "table" and self.rows is not None:
            rows = [r for r in self.rows if r]
            self.rows = None
            if rows:
                width = max(len(r) for r in rows)
                rows = [r + [""] * (width - len(r)) for r in rows]
                lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
                lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                self.write("\n".join(lines))
            self.block()
        elif tag == "pre":
            self.pre = max(self.pre - 1, 0)
            self.write("\n```")
            self.block()
        elif tag == "code" and not self.pre:
            self.write("`")
        elif tag in ("strong", "b"):
            self.write("**")
        elif tag in ("em", "i"):
            self.write("_")
        elif tag == "a":
            href = self.hrefs.pop() if self.hrefs else None
            if href:
                self.write(f"]({href})")
        elif tag == "ac:structured-macro":
            name = self.macros.pop() if self.macros else ""
            if name in _CODE_MACROS:
                self.pre = max(self.pre - 1, 0)
                self.write("\n```")
            if name in _CODE_MACROS or name in _CALLOUTS:
                self.block()
        elif tag == "ac:link" and self.link is not None:
            if not self.link["body"] and self.link["title"]:
                self.write(self.link["title"])
            self.link = None

    def handle_data(self, data: str) -> None:
        if self.pre:
            self.write(data)
            return
        text = re.sub(r"\s+", " ", data)
        if not text.strip():
            if self.out and not self.out[-1].endswith(("\n", " ")):
                self.write(" ")
            return
        if self.cell is None and (not self.out or self.out[-1].endswith("\n")):
            text = text.lstrip()
        self.write(text)


def storage_to_markdown(storage: str) -> str:
    """Convert Confluence storage-format XHTML to readable Markdown."""
    if not storage:
        return ""
    source = _CDATA.sub(lambda m: html.escape(m.group(1), quote=False), storage)
    parser = _StorageParser()
    parser.feed(source)
    parser.close()
    text = "".join(parser.out)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()
