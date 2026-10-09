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
   - Start the server: open `.vscode/mcp.json` and click **Start** above `docs-to-spec`, or run **MCP: List Servers**. Paste the GitHub token when prompted, or leave it empty. For Confluence sources, also enter the Confluence e-mail (Cloud only) and token at their prompts; leave them empty otherwise.
   - In Copilot Chat agent mode, open the tools picker and enable the `docs-to-spec` tools.
   - Then run `/speckit-docs-to-spec-harvest`.
