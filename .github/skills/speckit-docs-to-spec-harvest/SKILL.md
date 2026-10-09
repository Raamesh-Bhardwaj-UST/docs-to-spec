---
name: speckit-docs-to-spec-harvest
description: Fetch the configured sources through the docs-to-spec MCP server and
  write a redacted snapshot
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: Raamesh Bhardwaj (UST PACE)
  source: extension:docs-to-spec
---

# Docs To Spec Harvest Skill

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
   - CONFLUENCE_TOKEN / CONFLUENCE_EMAIL not set → restart the server and enter them at the prompts (Cloud: account e-mail + API token; Data Center: personal access token only).
   - Confluence 401/403 → wrong token or e-mail, wrong `auth` for the deployment, or no view permission on the space.
   - Confluence 404 or "did not return JSON" → check `base_url` (Cloud must be `https://<site>.atlassian.net/wiki`; Data Center includes any context path).
4. Call `snapshot_status` and show a table: source, type, documents, fetched_at, redactions.
5. If any redactions are non-zero, say how many and that the values were replaced with `[REDACTED:<type>]` tokens.
6. **Gate.** Tell the user to review `.specify/harvest/raw/manifest.json` and a sample of files, then commit the snapshot before running `/speckit-docs-to-spec-extract`. Stop here.
