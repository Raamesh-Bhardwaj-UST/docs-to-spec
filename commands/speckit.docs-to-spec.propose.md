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
   - a specify prompt containing, verbatim for each requirement, the Statement, Success criterion and Acceptance criteria (with their `AC-` numbers), plus:
     "Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec."
4. Write `docs/requirements/candidates.md`.
5. If `.specify/extensions/assess` does not exist, say so and suggest `specify extension add assess`; keep the specify prompts as the main path.
6. If the input names a candidate number, run its assess intake (or its specify prompt if assess isn't installed).
7. **Gate.** Remind the user to review `candidates.md` before starting any spec.
