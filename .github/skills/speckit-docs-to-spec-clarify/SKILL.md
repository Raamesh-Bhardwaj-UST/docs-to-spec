---
name: speckit-docs-to-spec-clarify
description: Ask the top-ranked open questions (at most five per round), write the
  answers back into the requirements, and log them
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: Raamesh Bhardwaj (UST PACE)
  source: extension:docs-to-spec
---

# Docs To Spec Clarify Skill

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
   - Update the affected requirements: replace the matching `[NEEDS CLARIFICATION]` marker in the Statement, Success criterion or Acceptance criteria with the answered value, and add an acceptance criterion if the answer introduces a new limit or error case. Set status `confirmed` when no markers remain in any of the three.
   - Set the question's state to `answered` and add a Clarification log row with today's date (ISO), a one-line summary, the respondent (from `git config user.name`, or ask), and the requirement IDs updated.
4. For each "defer": set state `deferred`. If work must proceed, record the working assumption under "Assumed, pending confirmation" with the QID, and set the requirement status `assumed-pending-confirmation`. If the assumed value is used in a Success criterion or Acceptance criterion, tag it there as `[ASSUMED: <QID>]`. Never present an assumption as a confirmed requirement.
5. Never copy secrets or personal data from answers into the file. If an answer contains any, summarise without the value.
6. Report what changed. If questions remain, offer another round; otherwise suggest `/speckit-docs-to-spec-review` once more, then `/speckit-docs-to-spec-propose`.
