# Requirements review

Reviewed `docs/requirements/harvested.md` against `.specify/docs-to-spec/requirements-rubric.md` and `.github/agents/requirements-reviewer.agent.md`. All citations were checked against `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`; the referenced headings exist and support the summarized rules. No unsupported requirement was found. The source does not define a software architecture, so feasibility is not independently established beyond the absence of a source-level contradiction.

Two revision passes were completed. The first split REQ-001's compound statement and added REQ-022 for the source's separate no-metrics behavior. The second removed redundant priority-overlap questions already governed by the global severity rule and moved unresolved items to `needs-human`. Requirement IDs were not renumbered.

| ID | Score (x/8) | Failing criteria | Evidence (failing words) | Proposed rewrite or question |
|---|---:|---|---|---|
| REQ-001 | 7/8 | C2 | “message indicates a failure” | Q-004 defines failure/noise cues and precedence. Likely misread: treat any 5XX message as failure. |
| REQ-002 | 7/8 | C2 | “message indicates noise” | Q-004 defines noise cues and precedence. Likely misread: treat every transient or staging mention as noise. |
| REQ-003 | 7/8 | C2 | “non-critical production APIs” | Q-002 asks for the service grouping. Likely misread: assign priority based on an undocumented service inventory. |
| REQ-004 | 7/8 | C2 | “datapoints” | Q-006 asks for interval and measurement source. Likely misread: assume an arbitrary sampling interval. |
| REQ-005 | 6/8 | C1, C2 | “CPU usage exceeds 80% or memory usage exceeds 75%”; “infrastructure is healthy” | Keep as one classification rule only if the branches are intended to form one decision; Q-007 defines measurement windows and healthy state. Likely misread: classify based on a single unbounded sample. |
| REQ-006 | 7/8 | C2 | “short-lived self-recovered latency” | Q-006 and a human answer must define duration/recovery boundaries. Likely misread: treat any latency drop as recovery. |
| REQ-007 | 8/8 | — | — | No rewrite needed. |
| REQ-008 | 8/8 | — | — | No rewrite needed. |
| REQ-009 | 7/8 | C2 | “production business services” | Q-002 supplies the service grouping. Likely misread: infer business-critical status from service names. |
| REQ-010 | 7/8 | C2 | “usage exceeds 84%”; “flagged for decommissioning” | Q-008 clarifies evaluation around the trigger; clarify whether the exception suppresses or clears an alert. Likely misread: suppress alerts without checking current decommission state. |
| REQ-011 | 7/8 | C2 | “P2 above 90%”; “P3 from 85% to 90%” | Q-008 addresses the uncovered interval and categorical overrides. Likely misread: assume inclusive/exclusive boundaries not stated by the source. |
| REQ-012 | 6/8 | C2, C3 | “multiple services and nodes” | Q-009 must quantify the sample and validation evidence before a concrete test can be defined. Likely misread: treat two arbitrary observations as sufficient confirmation. |
| REQ-013 | 7/8 | C2 | “cluster-wide”; “temporary DNS failure”; “false alarms” | Q-010 defines these cases. Likely misread: label any probe timeout P5 without checking service impact. |
| REQ-014 | 7/8 | C2 | “business-logic failure indicator” | Q-011 defines exact-match versus broader keyword behavior. Likely misread: treat a keyword in unrelated text as a failure. |
| REQ-015 | 7/8 | C2 | “order-processing degradation”; “unused feature-workflow errors” | Q-011 asks for the missing Redis priority and degradation boundary. Likely misread: apply a neighboring category's priority to Redis without evidence. |
| REQ-016 | 6/8 | C1, C2 | “one of the listed indicators”; “corresponding category” | Q-014 resolves cross-category matches. Likely misread: stop at the first matching indicator when several apply. |
| REQ-017 | 8/8 | — | — | No rewrite needed. |
| REQ-018 | 6/8 | C2, C3 | “data is insufficient” | Q-012 must define minimum required data before an acceptance test can distinguish sufficient from insufficient input. Likely misread: classify any missing optional field as insufficient. |
| REQ-019 | 6/8 | C2, C3 | “use evidence”; “shall not use a guess” | Q-012 defines accepted evidence and inconclusive-evidence behavior before a concrete test can be written. Likely misread: present an unsupported inference as evidence. |
| REQ-020 | 6/8 | C2, C3 | “business-critical services”; “higher” | Q-002 must name the services and priority relationship before a concrete test can be written. Likely misread: treat “higher” as a numeric priority increase despite P1 being worst. |
| REQ-021 | 6/8 | C2, C3 | “below the applicable threshold” | Q-005 must define the metric and threshold before a concrete test can be written. Likely misread: reuse the disk or latency threshold for 5XX alerts. |
| REQ-022 | 7/8 | C2 | “message semantics” | Q-004 defines the allowed failure/noise cues and precedence. Likely misread: decide validity from an unlisted phrase without a defined rule. |

## Acceptance tests (draft)

- **REQ-007:** Given a Kubernetes pod with 6 restarts in 10 minutes, when the system evaluates the restart count, then it identifies a pod restart loop.
- **REQ-008:** Given a pod restart-loop validation and logs containing `OOMKilled`, `CrashLoopBackOff`, and `ImagePullBackoff`, when the system checks the logs, then it checks for all three listed indicators.
- **REQ-017:** Given an alert to which P2 and P4 rules apply, when the system resolves priority, then it selects P2 because P1 is the worst severity and P2 is more severe than P4.

## Needs human

After two revision passes, these 19 requirements remain unresolved and are marked `needs-human`: REQ-001–REQ-006, REQ-009–REQ-016, and REQ-018–REQ-022. Their markers and corresponding questions are retained in `harvested.md`; no missing policy values were guessed.

No concrete acceptance test can yet distinguish pass from fail for REQ-012, REQ-018, REQ-019, REQ-020, or REQ-021 because the source does not quantify the relevant terms or threshold. Other needs-human items have concrete example cases, but their complete rule remains ambiguous.

## Summary

- Requirements passing 8/8: 3 of 22.
- Average score: 6.82/8.
- Weak-word hits from the rubric's list: 0.
- Requirements with no possible acceptance test yet: 5 (REQ-012, REQ-018, REQ-019, REQ-020, REQ-021).
- Inferred requirements: 0.
- Direct contradictions: 0.
- Open questions: 13 (scope 2, security/privacy 1, user experience 0, technical detail 10). The missing Redis priority was added to existing Q-011; no additional question row was needed.

Next: run `/speckit-docs-to-spec-clarify` to resolve the highest-ranked open questions, at most five per round.