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
9. **Success criterion.** Every requirement has exactly one: a measurable outcome (a number with a unit, or an observable yes/no result) that the source states. If the source gives none, write `[NEEDS CLARIFICATION: what counts as success for <requirement>?]` and add an open question. Never invent a target.
10. **Acceptance criteria.** Every requirement has at least one Given/When/Then criterion: one for the main path, plus one for each limit or error behaviour the source states. Use only values from the source. Where a value is missing, put the `[NEEDS CLARIFICATION: ...]` marker inside the criterion instead of an example value. Number them `AC-<REQ number>.<n>` (for example `AC-001.1`) and keep the numbers stable, like REQ IDs.
11. A requirement is `confirmed` only when no `[NEEDS CLARIFICATION]` marker remains in its Statement, Success criterion or Acceptance criteria.

## Output: `docs/requirements/harvested.md`

```markdown
# Harvested requirements

Snapshot: <manifest generated_at> · Sources: <ids> · Focus: <focus>

## Requirements

### REQ-001 <short title>
- **Statement:** When <trigger>, the <system> shall <response>. [NEEDS CLARIFICATION: ...]
- **Success criterion:** <measurable outcome from the source> | [NEEDS CLARIFICATION: ...]
- **Acceptance criteria:**
  - AC-001.1 Given <context>, when <action>, then <observable result>.
  - AC-001.2 Given <context>, when <error or limit case>, then <observable result>. [NEEDS CLARIFICATION: ...]
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

Report counts: requirements by status, requirements whose success criterion or acceptance criteria still contain a marker, conflicts, open questions by rank. Suggest `/speckit-docs-to-spec-review` next.
