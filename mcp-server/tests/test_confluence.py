"""Confluence fetcher tests. All HTTP is mocked; credentials are placeholders."""
import base64
import json

import httpx
import pytest

from docs_to_spec_mcp.confluence import build_cql, confluence_documents, storage_to_markdown
from docs_to_spec_mcp.redact import redact

FAKE_TOKEN = "not-a-real-token"
FAKE_LOGIN = "someone@example.invalid"


def _json(data, status=200):
    return httpx.Response(status, content=json.dumps(data).encode(), headers={"Content-Type": "application/json"})


# ---------- CQL ----------

def test_cql_from_space_ancestor_labels():
    cql = build_cql({"id": "c", "space": "PROD", "ancestor": "123", "labels": ["req", 'a"b']})
    assert cql == ('type = page AND space = "PROD" AND ancestor = 123 AND label = "req" '
                   'AND label = "a\\"b" ORDER BY lastmodified DESC')


def test_cql_custom_is_used_as_is():
    assert build_cql({"id": "c", "cql": "space = X and title ~ \"Export\""}) == "space = X and title ~ \"Export\""


def test_cql_refuses_whole_site():
    with pytest.raises(ValueError):
        build_cql({"id": "c"})


def test_cql_ancestor_must_be_numeric():
    with pytest.raises(ValueError):
        build_cql({"id": "c", "ancestor": "1 OR 1=1"})


# ---------- storage format ----------

def test_storage_to_markdown():
    storage = (
        "<h2>Export</h2><p>The export <strong>should</strong> be fast.</p>"
        "<ul><li><p>CSV</p></li><li>Excel<ul><li>xlsx only</li></ul></li></ul>"
        "<ol><li>first</li><li>second</li></ol>"
        "<table><tbody><tr><th>Role</th><th>Can export</th></tr>"
        "<tr><td>Admin</td><td>Yes | all</td></tr></tbody></table>"
        '<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">sql</ac:parameter>'
        "<ac:plain-text-body><![CDATA[SELECT * FROM t WHERE a < 3;]]></ac:plain-text-body></ac:structured-macro>"
        '<ac:structured-macro ac:name="info"><ac:parameter ac:name="title">t</ac:parameter>'
        "<ac:rich-text-body><p>Audit data is sensitive.</p></ac:rich-text-body></ac:structured-macro>"
        '<p>Owner: <ac:link><ri:user ri:account-id="5b10ac8d82e05b22cc7d4ef5" /></ac:link>, see '
        '<ac:link><ri:page ri:content-title="Audit rules" /></ac:link> and '
        '<a href="https://example.com/spec">the spec</a>.</p>'
        '<ac:image><ri:attachment ri:filename="flow.png" /></ac:image>'
        "<ac:task-list><ac:task><ac:task-id>1</ac:task-id><ac:task-status>incomplete</ac:task-status>"
        "<ac:task-body>Confirm limits</ac:task-body></ac:task></ac:task-list>"
    )
    md = storage_to_markdown(storage)
    assert "## Export" in md
    assert "The export **should** be fast." in md
    assert "- CSV\n- Excel\n  - xlsx only\n\n1. first" in md
    assert "1. first" in md and "2. second" in md
    assert "| Role | Can export |" in md and "| Admin | Yes \\| all |" in md
    assert "```\nSELECT * FROM t WHERE a < 3;\n```" in md
    assert "language" not in md and "sql" not in md.replace("SELECT", "")
    assert "**Info:** Audit data is sensitive." in md
    assert "Owner: @user, see Audit rules and [the spec](https://example.com/spec)." in md
    assert "5b10ac8d" not in md
    assert "[image]" in md and "flow.png" not in md
    assert "- [ ] Confirm limits" in md and "incomplete" not in md


def test_storage_empty():
    assert storage_to_markdown("") == ""


# ---------- fetching ----------

def _cloud_handler(seen):
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        path = request.url.path
        if path == "/wiki/rest/api/content/search":
            if "cursor" not in request.url.params:
                return _json({"results": [{"id": "101", "type": "page"}, {"id": "102", "type": "page"}],
                              "_links": {"next": "/rest/api/content/search?cql=x&cursor=abc"}})
            return _json({"results": [{"id": "103", "type": "page"}, {"id": "9", "type": "blogpost"}],
                          "_links": {}})
        if path.startswith("/wiki/api/v2/pages/"):
            pid = path.rsplit("/", 1)[1]
            return _json({"id": pid, "title": f"Page {pid}", "version": {"number": 4},
                          "body": {"storage": {"value": f"<p>Body {pid}</p>"}},
                          "_links": {"webui": f"/spaces/PROD/pages/{pid}/Page"}})
        return httpx.Response(404)
    return handler


def test_cloud_fetch(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_TOKEN", FAKE_TOKEN)
    monkeypatch.setenv("CONFLUENCE_EMAIL", FAKE_LOGIN)
    seen = []
    src = {"id": "conf", "type": "confluence", "base_url": "https://acme.atlassian.net", "space": "PROD"}
    docs = confluence_documents(src, transport=httpx.MockTransport(_cloud_handler(seen)))
    assert [d.doc_id for d in docs] == ["page-101", "page-102", "page-103"]
    first = docs[0]
    assert first.title == "Page 101" and first.revision == "4"
    assert first.url == "https://acme.atlassian.net/wiki/spaces/PROD/pages/101/Page"
    assert first.body == "# Page 101\n\nBody 101"
    expected = "Basic " + base64.b64encode(f"{FAKE_LOGIN}:{FAKE_TOKEN}".encode()).decode()
    assert all(r.headers["Authorization"] == expected for r in seen)
    assert seen[0].url.params["cql"] == 'type = page AND space = "PROD" ORDER BY lastmodified DESC'
    assert seen[3].url.params["body-format"] == "storage"


def test_cloud_max_items(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_TOKEN", FAKE_TOKEN)
    monkeypatch.setenv("CONFLUENCE_EMAIL", FAKE_LOGIN)
    src = {"id": "conf", "base_url": "https://acme.atlassian.net/wiki", "space": "PROD", "max_items": 1}
    docs = confluence_documents(src, transport=httpx.MockTransport(_cloud_handler([])))
    assert [d.doc_id for d in docs] == ["page-101"]


def test_datacenter_fetch_uses_bearer_and_v1(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_TOKEN", FAKE_TOKEN)
    seen = []

    def handler(request):
        seen.append(request)
        if request.url.path == "/confluence/rest/api/content/search":
            return _json({"results": [{"id": "7", "type": "page"}], "_links": {}})
        if request.url.path == "/confluence/rest/api/content/7":
            return _json({"id": "7", "title": "Export", "version": {"number": 2},
                          "body": {"storage": {"value": "<h1>Formats</h1><p>CSV</p>"}},
                          "_links": {"webui": "/display/PROD/Export"}})
        return httpx.Response(404)

    src = {"id": "dc", "base_url": "https://wiki.example.com/confluence", "space": "PROD"}
    docs = confluence_documents(src, transport=httpx.MockTransport(handler))
    assert docs[0].url == "https://wiki.example.com/confluence/display/PROD/Export"
    assert docs[0].body == "# Export\n\n# Formats\n\nCSV"
    assert seen[1].url.params["expand"] == "body.storage,version"
    assert all(r.headers["Authorization"] == f"Bearer {FAKE_TOKEN}" for r in seen)


def test_refuses_next_link_to_other_host(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_TOKEN", FAKE_TOKEN)

    def handler(request):
        return _json({"results": [], "_links": {"next": "https://elsewhere.example.net/rest/api/content/search"}})

    src = {"id": "dc", "base_url": "https://wiki.example.com", "space": "PROD"}
    with pytest.raises(RuntimeError, match="another host"):
        confluence_documents(src, transport=httpx.MockTransport(handler))


def test_missing_token(monkeypatch):
    monkeypatch.delenv("CONFLUENCE_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="CONFLUENCE_TOKEN"):
        confluence_documents({"id": "dc", "base_url": "https://wiki.example.com", "space": "P"})


def test_requires_https():
    with pytest.raises(ValueError, match="https"):
        confluence_documents({"id": "dc", "base_url": "http://wiki.example.com", "space": "P"})


def test_http_error_hides_query(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_TOKEN", FAKE_TOKEN)
    src = {"id": "dc", "base_url": "https://wiki.example.com", "space": "P"}
    with pytest.raises(RuntimeError, match=r"401 for /rest/api/content/search$"):
        confluence_documents(src, transport=httpx.MockTransport(lambda r: httpx.Response(401)))


def test_atlassian_token_redacted():
    fake = "ATATT3" + "x" * 40
    out, counts = redact(f"token is {fake}")
    assert fake not in out and counts["atlassian_token"] == 1
