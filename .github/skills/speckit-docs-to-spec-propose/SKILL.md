---
name: speckit-docs-to-spec-propose
description: Group confirmed requirements into candidate features and write ready-to-run
  assess and specify prompts
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: Raamesh Bhardwaj (UST PACE)
  source: extension:docs-to-spec
---

# Docs To Spec Propose Skill

## User input

```text
$ARGUMENTS
```

Optional: a candidate number to start after `candidates.md` is written and you confirm.

## Steps

1. **Gate: human approval (before proposing).** Read `docs/requirements/harvested.md` and `docs/requirements/review.md`. If either is missing, say which and stop: suggest `/speckit-docs-to-spec-extract` or `/speckit-docs-to-spec-review`. Otherwise check:
   - requirements with status `needs-clarification` or `needs-human` (count and IDs)
   - open questions whose state is `open` or `asked` (count)
   - whether `review.md` is older than `harvested.md`: compare `git log -1 --format=%cI -- <file>` for each, and treat a file with uncommitted changes (`git status --porcelain docs/requirements`) as newer than its last commit
   Show the results as a short table, then ask: "Approve proposing from the confirmed and assumed-pending-confirmation requirements only? (yes/no)". Wait for the answer. Continue only on an explicit yes in this chat; otherwise stop and suggest `/speckit-docs-to-spec-clarify` and `/speckit-docs-to-spec-review`. Ask even when every check is clean.
2. Use only requirements with status `confirmed` or `assumed-pending-confirmation`. List any `needs-clarification` or `needs-human` ones as blockers.
3. Group them into 3–7 candidate features. Rank by value and readiness (fewest open questions first).
4. For each candidate, write:
   - title, slug (kebab-case), requirement IDs, open blockers, main risk
   - an assess prompt:
     `/speckit-assess-intake "<one-paragraph idea>. Grounded in docs/requirements/harvested.md <REQ IDs>; sources <snapshot files>. Research local snapshot and codebase first." slug=<slug>`
   - a specify prompt containing, verbatim for each requirement, the Statement, Success criterion and Acceptance criteria (with their `AC-` numbers), plus:
     "Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec."
5. Write `docs/requirements/candidates.md`. At the top, record the approval: date (ISO), approver (from `git config user.name`, or ask), and the check results from step 1.
6. If `.specify/extensions/assess` does not exist, say so and suggest `specify extension add assess`; keep the specify prompts as the main path.
7. **Gate: review candidates (after proposing). Stop here.** List the candidates (number, title, REQ IDs, blockers) and tell the user to review and commit `candidates.md` before starting any spec. Do not run any assess or specify prompt in this step.
   - If the input named a candidate number, ask: "Start candidate <n> (<title>) now? (yes/no)". Only on an explicit yes in this chat, run its assess intake (or its specify prompt if assess isn't installed).
   - If no number was given, do not start anything. The user starts a candidate by running its prompt from `candidates.md`, or by re-running this command with the number.
