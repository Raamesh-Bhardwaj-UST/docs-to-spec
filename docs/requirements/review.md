# Requirements review

Reviewed `docs/requirements/harvested.md` against `.specify/docs-to-spec/requirements-rubric.md` and `.github/agents/requirements-reviewer.agent.md`. Round-trip and grounding checks used `.specify/harvest/raw/astra-alert-rules/page-1398800396.md` (REQ-001–REQ-022) and `.specify/harvest/raw/astra-alert-rules/page-1514635295.md` (REQ-023–REQ-032); all cited sections exist and support the grounded statements. No requirement was found to be unsupported, and no architecture instructions were present to assess additional feasibility constraints.

This review incorporates clarification answers through Q-010. Requirements not changed since the previous review retain their prior results; changed requirements were rechecked against both snapshot pages and their clarification log entries. Two review passes were completed on the changed requirements. IDs remain stable. AC-032.2 was withdrawn because neither the source nor the clarification specifies pre-approval availability.

| ID | Score (x/8) | Failing criteria | Evidence (failing words) | Proposed rewrite or question |
|----|-------------|------------------|--------------------------|------------------------------|
| REQ-001 | 7/8 | C2 | “message indicates a failure” | Q-004: define failure cues beyond examples. Misreading: treat any 5XX message as failure. |
| REQ-002 | 7/8 | C2 | “message indicates noise” | Q-004: define noise cues beyond examples. Misreading: treat any transient or staging mention as noise. |
| REQ-003 | 7/8 | C2 | “non-critical production APIs”; “intermittent errors that auto-recovered” | Q-002 and Q-004: define service grouping and recovery conditions. Misreading: assign priority using an undocumented inventory or duration. |
| REQ-004 | 8/8 | — | — | Q-006 defines each datapoint as 1-minute p95 API latency. Main and 2-of-3 boundary tests are present. Misreading prevented: counting two consecutive datapoints as a spike. |
| REQ-005 | 6/8 | C2 | “over the same window”; “usage” | Q-027: specify whether usage means average or peak across the window. Misreading: use different aggregation for CPU and memory. Branch and equality tests are present. |
| REQ-006 | 8/8 | — | — | Q-006 defines short-lived recovery as latency returning to ≤2 seconds within 5 minutes without intervention; AC-006.6 tests the boundary. Misreading prevented: assign P4 to any latency decrease. |
| REQ-007 | 8/8 | — | — | No rewrite needed. |
| REQ-008 | 8/8 | — | — | No rewrite needed. |
| REQ-009 | 7/8 | C2 | “production business services” | Q-002: identify the service group. Misreading: infer business-critical status from service names. |
| REQ-010 | 8/8 | — | — | Q-008 defines 5-minute evaluation, suppression of new alerts, and closure of existing alerts. ACs cover threshold, exception, closure, and exact 84%. Source does not state the added interval or closure; both are attributed to the clarification. |
| REQ-011 | 6/8 | C2, C8 | “P4 for cold-storage volumes or non-production”; “P5 for duplicate alerts” | Q-028: P4/P5 cannot be selected if every alert above 84% receives P3 or P2 and highest severity wins. AC-011.3/.4 retain markers. Misreading: silently discard one set of rules. |
| REQ-012 | 8/8 | — | — | Q-009 gives a 5-minute window and the 2-service-or-node threshold. ACs cover both positive branches and the 1-service/1-node case. |
| REQ-013 | 6/8 | C2, C3 | “exactly 2 services and fewer than 50%” | Q-029: no priority is specified for a confirmed 2-service error below the cluster-wide node threshold. AC-013.8 keeps the marker. |
| REQ-014 | 7/8 | C2 | “business-logic failure indicator” | Q-011: specify exact-match versus broader keyword behavior. Misreading: treat a keyword in unrelated text as a failure. |
| REQ-015 | 7/8 | C2 | “order-processing degradation”; “unused feature-workflow errors” | Q-011: define degradation/workflow conditions and Redis priority. Misreading: assign Redis a neighboring category's priority without evidence. |
| REQ-016 | 6/8 | C1, C2 | “its stated category”; unresolved alternatives in AC-016.1 and AC-016.9 | Q-014 and Q-015: resolve overlapping indicators and category-label alternatives. Misreading: stop at the first matching indicator or treat cause and category as identical. |
| REQ-017 | 8/8 | — | — | No rewrite needed. |
| REQ-018 | 6/8 | C2, C3 | “data is insufficient” | Q-012: define minimum required data. Misreading: treat any missing optional field as insufficient. |
| REQ-019 | 6/8 | C2, C3 | “use evidence”; “shall not use a guess” | Q-012: define allowed evidence and behavior when evidence is inconclusive. Misreading: present an inference as evidence. |
| REQ-020 | 6/8 | C2, C3 | “business-critical services”; “higher” | Q-002: identify services and the priority relationship. Misreading: read “higher” as a larger number despite P1 being worst. |
| REQ-021 | 6/8 | C2, C3 | “below the applicable threshold” | Q-005: define the threshold and measurement. Misreading: reuse a different alert's threshold. |
| REQ-022 | 7/8 | C2 | “message semantics” | Q-004: define allowed cues and precedence when failure and noise cues coexist. Misreading: decide from an unlisted phrase. |
| REQ-023 | 7/8 | C2 | “`<public-domain>`” | Q-022: specify the public domain per environment. Authentication behavior is now defined by Q-023. Misreading: configure the endpoint with a non-public or non-HTTPS URL. |
| REQ-024 | 8/8 | — | — | Q-019/Q-025 specify Key Vault and managed-identity-only read access. AC-024.3/.4 test both allowed and denied access. Secret values are not copied. |
| REQ-025 | 8/8 | — | — | No rewrite needed. Misreading (prevented by text): letting the Azure Bot create a new App ID instead of reusing the app registration's. |
| REQ-026 | 8/8 | — | — | No rewrite needed. Misreading (prevented by text): assuming the Teams channel is on by default. |
| REQ-027 | 8/8 | — | — | Q-017 resolves Group Chat as not required; manifest tests cover included and excluded scopes. |
| REQ-028 | 8/8 | — | — | Q-026 resolves the source conflict in favor of dropping both permissions; the conflict is explicitly recorded. Misreading prevented: retaining message-read permissions for a one-way bot. |
| REQ-029 | 8/8 | — | — | Q-016/Q-021 define one-way alert-result notifications in Team scope to a designated alerts channel. ACs cover content, replies/commands, and Personal scope exclusion. |
| REQ-030 | 8/8 | — | — | Q-018 selects single tenant; the app registration's account type is directly verifiable. |
| REQ-031 | 8/8 | — | — | Q-025 specifies 6-month expiry and replacement 30 days before expiry. The new secret is stored in Key Vault per REQ-024. |
| REQ-032 | 8/8 | — | — | Q-024 specifies all tenant users and a Teams admin approver. AC-032.2 was withdrawn because pre-approval visibility is unspecified. |

## Acceptance criteria and success criteria (proposed)

| ID | Acceptance criteria and success criterion disposition |
|----|--------------------------------------------------------|
| REQ-001 | Keep existing AC-001.1 and success criterion; Q-004 must resolve message-pattern scope. |
| REQ-002 | Keep existing AC-002.1 and success criterion; Q-004 must resolve message-pattern scope. |
| REQ-003 | Keep AC-003.1–AC-003.5 and success criterion; Q-002/Q-004 must define service groups and recovery conditions. |
| REQ-004 | Keep AC-004.1–AC-004.2 and success criterion; Q-006 defines 1-minute p95 datapoints. |
| REQ-005 | Keep AC-005.1–AC-005.3; Q-027 must say whether CPU/memory are compared by average or peak. |
| REQ-006 | Keep AC-006.1–AC-006.6 and success criterion; Q-006 defines recovery as ≤2 seconds within 5 minutes without intervention. |
| REQ-007 | Success criterion unchanged; AC-007.1 now uses 6 restarts within 10 minutes, a source-grounded example above 5. |
| REQ-008 | Keep AC-008.1 and success criterion; no rewrite needed. |
| REQ-009 | Keep AC-009.1–AC-009.5 and success criterion; Q-002 must define production business services. |
| REQ-010 | Keep AC-010.1–AC-010.4 and success criterion; Q-008 supplies the 5-minute interval and closes existing alerts on decommission flag. |
| REQ-011 | Keep AC-011.1–AC-011.6; Q-028 must resolve the unreachable P4/P5 rules before a complete priority test can be written. |
| REQ-012 | Keep AC-012.1–AC-012.3 and success criterion; Q-009 defines the 2-service-or-node, 5-minute threshold. |
| REQ-013 | Keep AC-013.1–AC-013.8; Q-029 must define the priority for exactly 2 affected services below the cluster-wide node threshold. |
| REQ-014 | Keep AC-014.1 and success criterion; Q-011 must define keyword matching. |
| REQ-015 | Keep AC-015.1–AC-015.6 and success criterion; Q-011 must define missing conditions and Redis priority. |
| REQ-016 | AC-016.1 now isolates HTTP 5XX; AC-016.12 tests backend stack trace as Server issue. Keep AC-016.2–AC-016.11 and success criterion; Q-014/Q-015 must resolve label conflicts and overlaps. |
| REQ-017 | Success criterion unchanged; AC-017.1 now tests simultaneous P1/P4 applicability and selects P1, the source's worst severity. |
| REQ-018 | Keep AC-018.1 and success criterion with markers; Q-012 must define insufficient data. |
| REQ-019 | Keep AC-019.1–AC-019.2 with markers; Q-012 must define evidence and inconclusive-evidence behavior. Success criterion remains marked pending that answer. |
| REQ-020 | Keep AC-020.1 with markers; Q-002 must define service groups and the priority relationship. Success criterion remains marked pending that answer. |
| REQ-021 | Keep AC-021.1 and success criterion with markers; Q-005 must define the threshold and measurement. |
| REQ-022 | Keep AC-022.1–AC-022.3 and success criterion; Q-004 must define cue scope and precedence. |
| REQ-023 | Keep AC-023.1–AC-023.3. Q-022 must supply the public domain for each environment. |
| REQ-024 | Keep AC-024.1–AC-024.4 and success criterion; Q-019/Q-025 define Key Vault and managed-identity-only access. |
| REQ-025 | Keep AC-025.1 and success criterion; no rewrite needed. |
| REQ-026 | Keep AC-026.1 and success criterion; no rewrite needed. |
| REQ-027 | Keep AC-027.1–AC-027.2 and success criterion; Group Chat is excluded by Q-017. |
| REQ-028 | Keep AC-028.1 and success criterion; Q-026 resolves the documented conflict by dropping both read permissions. AC-028.2 remains withdrawn. |
| REQ-029 | Keep AC-029.1–AC-029.4 and success criterion; Q-016/Q-021 define one-way Team-channel notifications. |
| REQ-030 | Keep AC-030.1 and success criterion; Q-018 selects single tenant. |
| REQ-031 | Keep AC-031.1–AC-031.3 and success criterion; Q-025 specifies 6-month expiry and rotation 30 days before expiry. |
| REQ-032 | Keep AC-032.1 and success criterion. AC-032.2 withdrawn because pre-approval availability is not specified. |

One new open question was raised this round: Q-023 (security / privacy) on authenticating requests to the public `/api/messages` endpoint. Existing markers are retained wherever required source details are absent.

## Needs human

After two review passes, these 16 requirements still fail at least one rubric check and need answers to open questions: REQ-001–REQ-003, REQ-005, REQ-009, REQ-011, REQ-013–REQ-016, and REQ-018–REQ-023. They are marked `needs-human` in `harvested.md`. Their IDs and clarification markers are retained.

No complete discriminating acceptance test can yet be written for REQ-011, REQ-018, REQ-019, REQ-020, REQ-021 or REQ-023 because their priority interaction, minimum data, evidence rules, threshold, service comparison or endpoint domain remain unresolved. Other needs-human requirements have concrete example cases but unresolved rule boundaries or scope.

## Summary

- Requirements passing 8/8: 16 of 32 (REQ-004, REQ-006–REQ-008, REQ-010, REQ-012, REQ-017, REQ-024–REQ-032).
- Average score: 7.25/8.
- Weak-word hits from the rubric list: 0.
- Requirements without a possible complete acceptance test: 6 (REQ-011, REQ-018, REQ-019, REQ-020, REQ-021, REQ-023).
- Requirements without a measurable success criterion: 2 (REQ-019, REQ-020).
- Inferred requirements: 0.
- Conflicts recorded: 3, including 1 unresolved priority conflict (REQ-011 / Q-028); two source differences are resolved by clarification (REQ-010 and REQ-028).
- Open questions: 8 (scope 0, security/privacy 0, user experience 0, technical detail 8); no new questions this review.

Next: run `/speckit-docs-to-spec-clarify` to resolve the highest-ranked open questions, up to five at a time.
