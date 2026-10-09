# Requirements review

Reviewed `docs/requirements/harvested.md` against `.specify/docs-to-spec/requirements-rubric.md` and `.github/agents/requirements-reviewer.agent.md`. Round-trip and grounding checks used `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`; all cited sections exist and support the grounded statements. No requirement was found to be unsupported, and no architecture instructions were present to assess additional feasibility constraints.

Two revision passes were completed. The first used source-stated numeric examples in REQ-007 and REQ-017 and split REQ-016's HTTP 5XX and backend-stacktrace tests to retain the source's unresolved category label. The second found no further source-only changes that could resolve the remaining ambiguities. The 19 unresolved requirements are marked `needs-human` in `harvested.md`; IDs remain stable.

| ID | Score (x/8) | Failing criteria | Evidence (failing words) | Proposed rewrite or question |
|----|-------------|------------------|--------------------------|------------------------------|
| REQ-001 | 7/8 | C2 | “message indicates a failure” | Q-004: define failure cues beyond examples. Misreading: treat any 5XX message as failure. |
| REQ-002 | 7/8 | C2 | “message indicates noise” | Q-004: define noise cues beyond examples. Misreading: treat any transient or staging mention as noise. |
| REQ-003 | 7/8 | C2 | “non-critical production APIs”; “intermittent errors that auto-recovered” | Q-002 and Q-004: define service grouping and recovery conditions. Misreading: assign priority using an undocumented inventory or duration. |
| REQ-004 | 7/8 | C2 | “datapoints” | Q-006: define datapoint interval and measurement source. Misreading: assume a sampling interval. |
| REQ-005 | 6/8 | C1, C2 | “CPU usage exceeds 80% or memory usage exceeds 75%”; “infrastructure is healthy” | Keep the two classification branches separate in tests; Q-007 defines measurement windows and healthy state. Misreading: classify from an unbounded sample. |
| REQ-006 | 7/8 | C2 | “short-lived self-recovered latency” | Q-006: define duration and recovery evidence. Misreading: treat any latency drop as recovery. |
| REQ-007 | 8/8 | — | — | No rewrite needed. |
| REQ-008 | 8/8 | — | — | No rewrite needed. |
| REQ-009 | 7/8 | C2 | “production business services” | Q-002: identify the service group. Misreading: infer business-critical status from service names. |
| REQ-010 | 7/8 | C2 | “usage exceeds 84%”; “flagged for decommissioning” | Q-008: define evaluation window and whether the flag suppresses or clears alerts. Misreading: ignore existing alerts without a defined rule. |
| REQ-011 | 7/8 | C2 | “P2 above 90%”; “P3 from 85% to 90%” | Q-008: resolve the 84%-to-85% gap, endpoints, and categorical overrides. Misreading: assume unstated boundaries or precedence. |
| REQ-012 | 6/8 | C2, C3 | “multiple services and nodes” | Q-009: quantify how many services/nodes and what evidence confirms the error. Misreading: consider arbitrary observations sufficient. |
| REQ-013 | 7/8 | C2 | “cluster-wide”; “temporary DNS failure”; “false alarms” | Q-010: define these conditions and single-retry success. Misreading: classify a probe timeout P5 without considering impact. |
| REQ-014 | 7/8 | C2 | “business-logic failure indicator” | Q-011: specify exact-match versus broader keyword behavior. Misreading: treat a keyword in unrelated text as a failure. |
| REQ-015 | 7/8 | C2 | “order-processing degradation”; “unused feature-workflow errors” | Q-011: define degradation/workflow conditions and Redis priority. Misreading: assign Redis a neighboring category's priority without evidence. |
| REQ-016 | 6/8 | C1, C2 | “its stated category”; unresolved alternatives in AC-016.1 and AC-016.9 | Q-014 and Q-015: resolve overlapping indicators and category-label alternatives. Misreading: stop at the first matching indicator or treat cause and category as identical. |
| REQ-017 | 8/8 | — | — | No rewrite needed. |
| REQ-018 | 6/8 | C2, C3 | “data is insufficient” | Q-012: define minimum required data. Misreading: treat any missing optional field as insufficient. |
| REQ-019 | 6/8 | C2, C3 | “use evidence”; “shall not use a guess” | Q-012: define allowed evidence and behavior when evidence is inconclusive. Misreading: present an inference as evidence. |
| REQ-020 | 6/8 | C2, C3 | “business-critical services”; “higher” | Q-002: identify services and the priority relationship. Misreading: read “higher” as a larger number despite P1 being worst. |
| REQ-021 | 6/8 | C2, C3 | “below the applicable threshold” | Q-005: define the threshold and measurement. Misreading: reuse a different alert's threshold. |
| REQ-022 | 7/8 | C2 | “message semantics” | Q-004: define allowed cues and precedence when failure and noise cues coexist. Misreading: decide from an unlisted phrase. |

## Acceptance criteria and success criteria (proposed)

| ID | Acceptance criteria and success criterion disposition |
|----|--------------------------------------------------------|
| REQ-001 | Keep existing AC-001.1 and success criterion; Q-004 must resolve message-pattern scope. |
| REQ-002 | Keep existing AC-002.1 and success criterion; Q-004 must resolve message-pattern scope. |
| REQ-003 | Keep AC-003.1–AC-003.5 and success criterion; Q-002/Q-004 must define service groups and recovery conditions. |
| REQ-004 | Keep AC-004.1 and success criterion; Q-006 must define datapoints. |
| REQ-005 | Keep AC-005.1 and AC-005.2 and success criterion; Q-007 must define measurement windows and healthy infrastructure. |
| REQ-006 | Keep AC-006.1–AC-006.5 and success criterion; Q-006 must define short-lived and self-recovered. |
| REQ-007 | Success criterion unchanged; AC-007.1 now uses 6 restarts within 10 minutes, a source-grounded example above 5. |
| REQ-008 | Keep AC-008.1 and success criterion; no rewrite needed. |
| REQ-009 | Keep AC-009.1–AC-009.5 and success criterion; Q-002 must define production business services. |
| REQ-010 | Keep AC-010.1–AC-010.2 and success criterion; Q-008 must define evaluation and decommissioning behavior. |
| REQ-011 | Keep AC-011.1–AC-011.5 and success criterion; Q-008 must resolve boundaries, gap, and priority interaction. |
| REQ-012 | Keep AC-012.1 and success criterion with markers; Q-009 must define counts and evidence. |
| REQ-013 | Keep AC-013.1–AC-013.5 and success criterion; Q-010 must define ambiguous conditions. |
| REQ-014 | Keep AC-014.1 and success criterion; Q-011 must define keyword matching. |
| REQ-015 | Keep AC-015.1–AC-015.6 and success criterion; Q-011 must define missing conditions and Redis priority. |
| REQ-016 | AC-016.1 now isolates HTTP 5XX; AC-016.12 tests backend stack trace as Server issue. Keep AC-016.2–AC-016.11 and success criterion; Q-014/Q-015 must resolve label conflicts and overlaps. |
| REQ-017 | Success criterion unchanged; AC-017.1 now tests simultaneous P1/P4 applicability and selects P1, the source's worst severity. |
| REQ-018 | Keep AC-018.1 and success criterion with markers; Q-012 must define insufficient data. |
| REQ-019 | Keep AC-019.1–AC-019.2 with markers; Q-012 must define evidence and inconclusive-evidence behavior. Success criterion remains marked pending that answer. |
| REQ-020 | Keep AC-020.1 with markers; Q-002 must define service groups and the priority relationship. Success criterion remains marked pending that answer. |
| REQ-021 | Keep AC-021.1 and success criterion with markers; Q-005 must define the threshold and measurement. |
| REQ-022 | Keep AC-022.1–AC-022.3 and success criterion; Q-004 must define cue scope and precedence. |

No new open question was needed beyond Q-015, already present in `harvested.md` for category-label conflicts. Existing markers are retained wherever required source details are absent.

## Needs human

After two review passes, these 19 requirements still fail at least one rubric check and need answers to existing questions: REQ-001–REQ-006, REQ-009–REQ-016, and REQ-018–REQ-022. They are marked `needs-human` in `harvested.md`. Their IDs and clarification markers are retained.

No possible discriminating acceptance test can yet be completed for REQ-012, REQ-018, REQ-019, REQ-020, or REQ-021 because the snapshot omits quantities, definitions, evidence rules, or the threshold. Other needs-human requirements have concrete example cases but unresolved rule boundaries or scope.

## Summary

- Requirements passing 8/8: 3 of 22.
- Average score: 6.82/8.
- Weak-word hits from the rubric list: 0.
- Requirements without a possible acceptance test: 5 (REQ-012, REQ-018, REQ-019, REQ-020, REQ-021).
- Requirements without a measurable success criterion: 2 (REQ-019 and REQ-020).
- Inferred requirements: 0.
- Conflicts recorded: 0 direct contradictions; category-label alternatives are unresolved in Q-015.
- Open questions: 14 (scope 2, security/privacy 1, user experience 0, technical detail 11).

Next: run `/speckit-docs-to-spec-clarify` to resolve the highest-ranked open questions, up to five at a time.
