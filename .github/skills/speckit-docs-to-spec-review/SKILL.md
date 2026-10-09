---
name: speckit-docs-to-spec-review
description: Run the Requirements Reviewer agent instructions against harvested.md
  (rubric, test-first, round-trip, grounding), with at most two revision loops
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: Raamesh Bhardwaj (UST PACE)
  source: extension:docs-to-spec
---

# Docs To Spec Review Skill

## User input

```text
$ARGUMENTS
```

## Steps

1. Check that `.github/agents/requirements-reviewer.agent.md` exists. If not, tell the user to run `/speckit-docs-to-spec-setup` and stop.
2. Read that file in full and follow its Constraints, Checks and Output Format against `docs/requirements/harvested.md`.
3. **Loop (maximum 2 times):** apply the proposed rewrites that need no new information to `harvested.md`, keeping IDs. This includes the proposed Acceptance criteria and Success criterion, written into each requirement's own fields (keep `AC-` numbers stable; add new ones with the next free number). For rewrites that need information, add a `[NEEDS CLARIFICATION]` marker and an open question instead. Re-run the checks on changed requirements only.
4. After the second loop, set any requirement still failing to status `needs-human` and list it under "Needs human" in `review.md`.
5. Report: requirements passing 8/8, average score, weak-word hits, requirements without a possible acceptance test, requirements without a measurable success criterion, inferred count, and new open questions. Suggest `/speckit-docs-to-spec-clarify` next.
