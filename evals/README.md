# Evaluation set

1. Pick 10–15 source pages where the correct requirements are known.
2. For each, create `evals/<case>/source.md` (a redacted copy) and `evals/<case>/expected.md` (the agreed requirement statements and expected open questions).
3. After any change to the commands, rubric or reviewer agent, run harvest (as a `local` source pointing at `evals`), extract and review, then record per case:
   requirements found / missed / extra, weak-word hits, requirements without citation, requirements without a possible acceptance test, invented values (must be 0).
4. Keep the results table in `evals/results.md` with the date and commit.
