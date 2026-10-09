# Candidate features

Only confirmed requirements are candidates. REQ-007, REQ-008, and REQ-017 are confirmed; the other 19 requirements remain `needs-human` and are blockers, not candidate scope. Q-001 through Q-005 are deferred; nine other questions remain open. Q-001 (alerting system and population) is unresolved for every candidate.

## Blockers

- **REQ-001–REQ-006, REQ-009–REQ-016, REQ-018–REQ-022:** Needs-human requirements are excluded from candidate scope. Do not assume their behavior or expand these candidates to include them.
- **Q-001 (deferred):** Alerting system and alert population are unspecified; confirm whether each candidate applies to the intended system/population.
- **Q-002 (deferred):** Service groups and priority meaning are unspecified; this blocks interpreting or extending service-based priority policy.
- **Q-003 (deferred):** Security-specific handling is desired but its details are unspecified.
- **Q-004 (deferred):** 5XX message-cue scope, precedence, and recovery conditions are unspecified.
- **Q-005 (deferred):** The 5XX below-threshold metric and threshold are unspecified.
- **Q-006–Q-012, Q-014–Q-015 (open):** Latency, infrastructure, disk, network, business-logic, insufficient-data, evidence, category-precedence, and category-label details remain unresolved.

## Candidate 1: Detect Kubernetes Pod Restart Loops

- **Slug:** `detect-kubernetes-pod-restart-loops`
- **Requirements:** REQ-007
- **Open blockers:** Q-001 (deferred scope); the other needs-human alerting requirements are excluded.
- **Main risk:** The source gives a concrete trigger, but the alerting system/population governed by the rule is not identified.

**Assess prompt**

`/speckit-assess-intake "Specify detection of Kubernetes pod restart loops using the stated restart threshold and time window. Grounded in docs/requirements/harvested.md REQ-007; sources .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=detect-kubernetes-pod-restart-loops`

**Specify prompt**

Create a feature specification for detecting Kubernetes pod restart loops. Ground it in docs/requirements/harvested.md and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`. Resolve Q-001 before treating scope as final; do not invent details.

- **REQ-007 Statement:** When a Kubernetes pod restarts more than 5 times within 10 minutes, the system shall identify a pod restart loop.
- **REQ-007 Success criterion:** The system identifies a pod restart loop when restarts exceed 5 within 10 minutes.
- **REQ-007 Acceptance criteria:** AC-007.1 Given a Kubernetes pod with 6 restarts within 10 minutes, when the system evaluates the restart count, then it identifies a pod restart loop.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Candidate 2: Validate Pod Restart Indicators in Logs

- **Slug:** `validate-pod-restart-log-indicators`
- **Requirements:** REQ-008
- **Open blockers:** Q-001 (deferred scope); the other needs-human alerting requirements are excluded.
- **Main risk:** The source names three log indicators but does not state what action follows each finding; keep scope to checking for those indicators.

**Assess prompt**

`/speckit-assess-intake "Specify log validation for pod restart loops by checking the three indicators named in the source. Grounded in docs/requirements/harvested.md REQ-008; sources .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=validate-pod-restart-log-indicators`

**Specify prompt**

Create a feature specification for checking the named log indicators during pod restart-loop validation. Ground it in docs/requirements/harvested.md and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`. Resolve Q-001 before treating scope as final; do not infer remediation or classification behavior beyond the requirement.

- **REQ-008 Statement:** When validating a pod restart loop, the system shall check logs for `OOMKilled`, `CrashLoopBackOff`, and `ImagePullBackoff`.
- **REQ-008 Success criterion:** The system checks for all 3 log indicators named by the source.
- **REQ-008 Acceptance criteria:** AC-008.1 Given a pod restart-loop validation, when the system checks logs, then it checks for `OOMKilled`, `CrashLoopBackOff`, and `ImagePullBackoff`.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Candidate 3: Resolve Overlapping Alert Priorities

- **Slug:** `resolve-overlapping-alert-priorities`
- **Requirements:** REQ-017
- **Open blockers:** Q-001 (deferred scope); priority policies in REQ-003, REQ-006, REQ-009, REQ-011, REQ-013, and REQ-015 remain `needs-human` and may affect integration. Do not add those policies to this feature.
- **Main risk:** “Highest severity” could be misread without honoring the source's explicit rule that P1 is worst; source-backed acceptance coverage is limited to P1 and P4.

**Assess prompt**

`/speckit-assess-intake "Specify resolution when multiple alert priority rules apply, selecting the highest severity with P1 worst. Grounded in docs/requirements/harvested.md REQ-017; sources .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=resolve-overlapping-alert-priorities`

**Specify prompt**

Create a feature specification for resolving an alert's priority when multiple priority rules apply. Ground it in docs/requirements/harvested.md and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`. Resolve Q-001 before treating scope as final. Do not define priority policies that are outside REQ-017.

- **REQ-017 Statement:** When multiple rules apply to an alert, the system shall select the highest severity, where P1 is the worst severity.
- **REQ-017 Success criterion:** When multiple rules apply, the selected priority is the highest severity, with P1 worst.
- **REQ-017 Acceptance criteria:** AC-017.1 Given an alert to which P1 and P4 priority rules apply, when the system resolves priority, then it selects P1 as the highest severity.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Next Steps

The assess extension was not found at `.specify/extensions/assess`. To enable assess intake, run `specify extension add assess`; the specify prompts above remain the main path. Review this candidate list and its blockers before starting any spec.
