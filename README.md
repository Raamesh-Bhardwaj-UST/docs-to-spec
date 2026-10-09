# docs-to-spec

A Spec Kit extension that turns GitHub wikis, GitHub issues, Atlassian Confluence pages and local docs into cited, reviewed requirements and ready-to-run spec prompts.

## What it does

1. **Harvest** GitHub wikis, GitHub issues, Confluence (Cloud or Data Center) and local docs through a local MCP server. The server redacts sensitive data before anything reaches the agent or the disk, and writes a snapshot to `.specify/harvest/raw/`.
2. **Extract** EARS requirements, each with a citation and a ranked open-questions list. Gaps are marked `[NEEDS CLARIFICATION]`, never filled by guessing.
3. **Review** the requirements against a written rubric, using a separate Requirements Reviewer agent and test-first, round-trip and grounding checks.
4. **Clarify** gaps with you, at most five questions per round, and write your answers back.
5. **Propose** candidate features as ready-to-run `/speckit-assess-intake` and `/speckit-specify` prompts.

## Prerequisites

- PowerShell 7 (Windows) or bash (Linux/macOS)
- git
- [uv](https://docs.astral.sh/uv/) (Python 3.11 or later is installed by uv if needed; default 3.12)
- Spec Kit `specify` 1.0.12 or later
- Node.js (optional, only for the MCP Inspector smoke test)
- VS Code with GitHub Copilot Chat in agent mode
- **Copilot MCP policy:** Copilot Business and Enterprise orgs have a policy for *MCP servers in Copilot*. If it is disabled, VS Code lists the server but Copilot won't call its tools. Check with your admin first.
- For Confluence sources: on Cloud, your Atlassian account e-mail and an [API token](https://id.atlassian.com/manage-profile/security/api-tokens); on Data Center, a personal access token. Read access to the spaces you harvest is enough. Like the GitHub token, these are only entered at the VS Code prompts or set as `CONFLUENCE_EMAIL` / `CONFLUENCE_TOKEN` for the session.
- A GitHub fine-grained PAT (Contents: Read and Issues: Read on the source repos) for private issues or `auth: token` wikis. It is never stored on disk: VS Code prompts for it when the server starts, and the scripts read `GH_TOKEN` from the session environment.

## Install

Clone this repo, then in the target repo:

```powershell
specify extension add --dev <path-to-docs-to-spec-clone>
```

Confirm the local-install flag with `specify extension add --help`. Check that `.specify/extensions/docs-to-spec/` includes `mcp-server/` and `scripts/`. If `mcp-server/` was not copied, run setup with `-ServerDir <clone>\mcp-server` (PowerShell) or `--server-dir <clone>/mcp-server` (bash).

## Setup

In Copilot Chat run `/speckit-docs-to-spec-setup` (add `force` to overwrite the rubric and agent), or run the script directly:

```powershell
pwsh -NoProfile -File .specify/extensions/docs-to-spec/scripts/powershell/setup-mcp.ps1
```

```bash
bash .specify/extensions/docs-to-spec/scripts/bash/setup-mcp.sh
```

Setup:

- installs the server into a venv **inside the extension folder** (`.specify/extensions/docs-to-spec/.venv` when installed, `docs-to-spec/.venv` in a clone; override with `DOCS_TO_SPEC_VENV`) and git-ignores it when it is inside the workspace
- creates `.specify/docs-to-spec/sources.yml` from the template (never overwritten)
- copies `requirements-rubric.md` to `.specify/docs-to-spec/` and the Requirements Reviewer agent to `.github/agents/` (overwritten only with `-Force` / `--force`)
- writes or merges `.vscode/mcp.json` and git-ignores it (it holds the absolute venv path, so it is per machine)

Then:

1. Edit `.specify/docs-to-spec/sources.yml` (replace `OWNER/REPO`, remove sources you don't need).
2. For wiki sources with `auth: gcm`, run `harvest.ps1` / `harvest.sh` once from a terminal so Git Credential Manager can sign in.
3. Open `.vscode/mcp.json` and click **Start** above `docs-to-spec` (or run **MCP: List Servers**). Paste the GitHub token when prompted, or leave it empty.
4. In Copilot Chat agent mode, open the tools picker and enable the `docs-to-spec` tools.

VS Code launches the server executable directly over stdio. The `run-mcp` scripts are only for manual testing (`-Inspect` / `--inspect` opens the MCP Inspector).

## `sources.yml` reference

| Key | Applies to | Meaning |
|-----|-----------|---------|
| `version` | top level | `1` |
| `snapshot_dir` | top level | Snapshot folder inside the repo. Default `.specify/harvest/raw` (committed, so reviews and re-runs diff cleanly). |
| `redaction.emails` | top level | `true` also redacts e-mail addresses. Default `false`. |
| `id` | every source | Lowercase letters, digits and hyphens. |
| `type` | every source | `github-wiki`, `github-issues`, `confluence` or `local`. |
| `repo` | wiki, issues | `OWNER/REPO`. |
| `auth` | wiki | `gcm` (Git Credential Manager, recommended, default) or `token` (uses `GH_TOKEN`). |
| `include` / `exclude` | wiki, local | fnmatch-style patterns; `*` also matches `/`. Default include `["*.md"]`. |
| `state` | issues | `open` (default), `closed` or `all`. |
| `labels` | issues | Multiple labels are combined with AND. |
| `max_items` | issues | Default `200`. Pull requests are skipped. |
| `include_comments` | issues | Default `true`. Comment author logins are left out. |
| `base_url` | confluence | `https://<site>.atlassian.net/wiki` (Cloud) or your Data Center URL including any context path. Must be https. |
| `deployment` | confluence | `cloud` or `datacenter`. Default: `cloud` for `*.atlassian.net`, otherwise `datacenter`. |
| `auth` | confluence | `basic` (e-mail + API token; Cloud default) or `bearer` (personal access token; Data Center default). |
| `space` / `ancestor` / `labels` | confluence | Space key, a parent page id (only pages below it) and labels (AND). At least one of these or `cql` is required, so a whole site is never harvested by accident. |
| `cql` | confluence | Your own CQL, used as-is instead of `space`/`ancestor`/`labels`. Only pages are harvested. |
| `max_items` | confluence | Default `200`. |
| `token_env` / `email_env` | confluence | Environment variable names to read credentials from. Default `CONFLUENCE_TOKEN` / `CONFLUENCE_EMAIL`. Use different names for a second Confluence site and add them to `.vscode/mcp.json` by hand. |
| `path` | local | Folder relative to the repo root (default `docs`); must be inside the workspace. |

Confluence pages are selected with CQL search and read in storage format (REST v2 on Cloud, REST v1 on Data Center), then converted to Markdown. Each page becomes `page-<id>.md` with the page title as its top heading. User mentions become `@user` and images become `[image]`, so no names, account ids or attachments reach the snapshot. Credentials are only sent to `base_url`; pagination links to any other host are refused.

Wiki clones are cached outside the repo (`%LOCALAPPDATA%\docs-to-spec\cache` on Windows, `$XDG_CACHE_HOME/docs-to-spec` or `~/.cache/docs-to-spec` elsewhere; override with `DOCS_TO_SPEC_CACHE`).

## Command order and gates

```text
harvest (MCP, redacted snapshot) → [gate: commit snapshot] → extract → review → clarify (≤5/round)
  → [gate: human approval] → propose → /speckit-assess-* → /speckit-specify → /speckit-clarify → /speckit-checklist
```

| Command | Output |
|---------|--------|
| `/speckit-docs-to-spec-setup` | Server venv, `sources.yml`, rubric, reviewer agent, `.vscode/mcp.json` |
| `/speckit-docs-to-spec-harvest` | `.specify/harvest/raw/<source>/*.md` and `manifest.json`. Pass a source id to refresh one source, or `status`. **Gate:** review the manifest and a sample of files, then commit the snapshot. |
| `/speckit-docs-to-spec-extract` | `docs/requirements/harvested.md` (EARS statements, a measurable success criterion and Given/When/Then acceptance criteria per requirement, citations, conflicts, ranked open questions, stable REQ and AC IDs) |
| `/speckit-docs-to-spec-review` | `docs/requirements/review.md` (rubric scores, proposed acceptance and success criteria, "Needs human"); fixes are written back into `harvested.md`; at most two revision loops |
| `/speckit-docs-to-spec-clarify` | Answers written back to `harvested.md` with a clarification log; deferred answers go under "Assumed, pending confirmation" |
| `/speckit-docs-to-spec-propose` | `docs/requirements/candidates.md` with assess and specify prompts. **Gate:** review it before starting any spec. |

Open questions are ranked scope > security/privacy > user experience > technical detail. A typical run is harvest, extract, review, clarify, review, propose, committing after each step.

The MCP server exposes these tools: `list_sources`, `snapshot_all`, `snapshot_source`, `snapshot_status`, `search_snapshot`, `list_documents`, `read_document`.

Without the agent (fallback, CI, or first-time credential sign-in):

```powershell
pwsh -NoProfile -File .specify/extensions/docs-to-spec/scripts/powershell/harvest.ps1 [-Source <id>]
```

```bash
bash .specify/extensions/docs-to-spec/scripts/bash/harvest.sh [--source <id>]
```

## Redaction

Redaction runs inside the server on every document before it is returned to the agent or written to disk. Only counts per type are reported, never matched values; replaced text appears as `[REDACTED:<type>]`.

Caught: private keys, GitHub tokens, AWS access keys, JWTs, bearer tokens, credentials in URLs, Atlassian API tokens, `password` / `secret` / `client_secret` / `api_key` / `*token` assignments, card numbers (Luhn-checked), SSN, Aadhaar, PAN, passport and driving-licence formats, medical-record lines (MRN, patient id/name/number), and optionally e-mail addresses.

Redaction is **best-effort**. Patterns are deliberately broad: a false positive costs a look at the source, a false negative leaks data. **Exclude sources that hold health or HR records entirely** in `sources.yml` instead of relying on redaction.

## Manual `.vscode/mcp.json` entry

If `.vscode/mcp.json` contains comments, `configure-vscode` refuses to edit it. Add the entry by hand, using the absolute path to the server executable in your venv (`Scripts\docs-to-spec-mcp.exe` on Windows, `bin/docs-to-spec-mcp` elsewhere):

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "docs-to-spec-gh-token",
      "description": "GitHub PAT for docs-to-spec (leave empty for public sources or gcm-only wikis)",
      "password": true
    },
    {
      "type": "promptString",
      "id": "docs-to-spec-confluence-email",
      "description": "Atlassian account e-mail for Confluence Cloud (leave empty for Data Center or no Confluence sources)",
      "password": false
    },
    {
      "type": "promptString",
      "id": "docs-to-spec-confluence-token",
      "description": "Confluence API token (Cloud) or personal access token (Data Center); leave empty if unused",
      "password": true
    }
  ],
  "servers": {
    "docs-to-spec": {
      "type": "stdio",
      "command": "<venv>/Scripts/docs-to-spec-mcp.exe",
      "args": [],
      "env": {
        "DOCS_TO_SPEC_ROOT": "${workspaceFolder}",
        "GH_TOKEN": "${input:docs-to-spec-gh-token}",
        "CONFLUENCE_EMAIL": "${input:docs-to-spec-confluence-email}",
        "CONFLUENCE_TOKEN": "${input:docs-to-spec-confluence-token}"
      }
    }
  }
}
```

## Development

```powershell
cd mcp-server
$env:UV_PROJECT_ENVIRONMENT = Join-Path (Resolve-Path ..) ".venv"   # same venv setup uses
uv sync
uv run pytest -q
```

See `evals/README.md` for the evaluation set to run after changing the commands, rubric or reviewer agent.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Server shows in VS Code but Copilot never calls its tools | The org's MCP policy is off, or the tools aren't enabled in the agent tools picker. |
| Server fails to start | Output panel → **MCP: docs-to-spec** for the error. Re-run setup. Check that the exe path in `.vscode/mcp.json` exists. |
| `uv sync` fails with "access denied" | The server is running and Windows has locked the exe. Stop it in VS Code (MCP: List Servers → Stop) and re-run setup. |
| Venv slow to create, or files locked, in a OneDrive folder | OneDrive syncs the venv's thousands of files. Pause OneDrive sync while running setup, or set `DOCS_TO_SPEC_VENV` to a folder outside OneDrive and re-run setup. |
| `uv` can't download Python | Use an installed interpreter: `setup-mcp.ps1 -Python "C:\path\to\python.exe"`. |
| Wiki clone 403/404 with `auth: token` | Fine-grained PATs may not cover wiki git access. Switch to `auth: gcm` and run `harvest.ps1` once from a terminal. |
| Harvest hangs or fails on wiki auth inside chat | Credential Manager needs an interactive sign-in. Run `harvest.ps1` from a terminal once, then retry. |
| Issues return 401/403 | The token is missing or lacks Issues: Read. Stop the server, start it, and paste the token at the prompt. |
| Confluence: `CONFLUENCE_TOKEN` / `CONFLUENCE_EMAIL` not set | Stop and start the server and enter them at the prompts. If `.vscode/mcp.json` predates Confluence support, re-run setup to add the prompts. |
| Confluence 401/403 | Wrong token or e-mail, `auth` doesn't match the deployment (Cloud: `basic`, Data Center: `bearer`), or no view permission on the space. |
| Confluence 404 or "did not return JSON" | Check `base_url`: Cloud is `https://<site>.atlassian.net/wiki`; Data Center must include any context path such as `/confluence`. |
| Confluence 429 | The server retries with back-off. Lower `max_items` or narrow the CQL if it keeps happening. |
| `configure-vscode` says mcp.json isn't plain JSON | The file has comments. Add the entry by hand (see above). |
| `.vscode/mcp.json` still tracked by git | It was committed before. `git rm --cached .vscode/mcp.json` and commit. |
| Corporate proxy blocks GitHub API calls | Set `HTTPS_PROXY` before starting VS Code; httpx honours it. |
| Too much text redacted | Patterns are deliberately broad. Tune `redact.py`, add a test, and re-release. Never weaken the PII rules. |
| Slash commands missing | Reload the VS Code window. Check `specify extension list`. |
| `extract` invents values | Re-run review. If it persists, add that page to `evals/` and tighten rule 1 in `extract.md`. |

## License

MIT. See [LICENSE](LICENSE).
