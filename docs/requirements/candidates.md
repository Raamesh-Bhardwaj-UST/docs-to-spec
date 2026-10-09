# Candidate Features

**Approval record**
- **Date:** 2026-10-09
- **Approver:** Raamesh-Bhardwaj-UST (`git config user.name`)
- **Approval:** Proposing from confirmed and assumed-pending-confirmation requirements only; explicit approval received in this chat.
- **Gate results:** 22 confirmed; 0 assumed-pending-confirmation; 10 needs-human (REQ-001–REQ-003, REQ-009, REQ-015, REQ-016, REQ-020–REQ-023); 0 needs-clarification; 0 open/asked questions. `docs/requirements` has no uncommitted changes. Last commit timestamps for harvested.md and review.md are both 2026-10-09T15:25:42+05:30. The git freshness check does not show review.md as older, but its summary content is stale: it reports 16 passing requirements and 8 open questions, while harvested.md currently has 22 confirmed requirements and no open questions.

Only `confirmed` requirements are in candidate scope; there are no `assumed-pending-confirmation` requirements. Needs-human requirements below are blockers only and must not be added to candidate scope without clarification. All candidates have zero active open/asked questions; deferred questions and related needs-human requirements are listed as blockers. Candidates are ranked by readiness first, then value.

## Candidate 1: Detect and Validate Kubernetes Pod Restart Loops

- **Slug:** `detect-kubernetes-pod-restart-loops`
- **Requirements:** REQ-007, REQ-008
- **Open blockers:** Q-001 is deferred (alerting system/population). REQ-009 is needs-human and excluded (pod restart priorities).
- **Main risk:** The detection threshold is defined, but the alerting system and population governed by the rule are not.

**Assess prompt**

`/speckit-assess-intake "Specify detection and log validation for Kubernetes pod restart loops using the stated restart threshold, time window, and log indicators. Grounded in docs/requirements/harvested.md REQ-007, REQ-008; sources .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=detect-kubernetes-pod-restart-loops`

**Specify prompt**

Create a feature specification for detecting Kubernetes pod restart loops and checking the named log indicators. Ground it in `docs/requirements/harvested.md` and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`.

- **REQ-007 Statement:** When a Kubernetes pod restarts more than 5 times within 10 minutes, the system shall identify a pod restart loop.
- **REQ-007 Success criterion:** The system identifies a pod restart loop when restarts exceed 5 within 10 minutes.
- **REQ-007 Acceptance criteria:** AC-007.1 Given a Kubernetes pod with 6 restarts within 10 minutes, when the system evaluates the restart count, then it identifies a pod restart loop.
- **REQ-008 Statement:** When validating a pod restart loop, the system shall check logs for `OOMKilled`, `CrashLoopBackOff`, and `ImagePullBackoff`.
- **REQ-008 Success criterion:** The system checks for all 3 log indicators named by the source.
- **REQ-008 Acceptance criteria:** AC-008.1 Given a pod restart-loop validation, when the system checks logs, then it checks for `OOMKilled`, `CrashLoopBackOff`, and `ImagePullBackoff`.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Candidate 2: Detect and Classify API Latency Spikes

- **Slug:** `detect-and-classify-api-latency-spikes`
- **Requirements:** REQ-004, REQ-005, REQ-006
- **Open blockers:** Q-001 is deferred (alerting system/population). REQ-016 is needs-human and excluded (final category precedence); Q-031 and Q-032 are deferred (category tie-breaking).
- **Main risk:** Detection, cause classification, and priority are specified, but the final user-facing category can still be ambiguous when rules overlap.

**Assess prompt**

`/speckit-assess-intake "Specify API latency spike detection using 1-minute p95 measurements, classify infrastructure versus application causes, and assign the stated priority mapping. Grounded in docs/requirements/harvested.md REQ-004, REQ-005, REQ-006; source .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=detect-and-classify-api-latency-spikes`

**Specify prompt**

Create a feature specification for API latency spike detection, cause classification, and priority assignment. Ground it in `docs/requirements/harvested.md` and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`.

- **REQ-004 Statement:** When 1-minute p95 API latency exceeds 2 seconds for 3 consecutive datapoints, the system shall identify a latency spike.
- **REQ-004 Success criterion:** A latency spike is identified when 1-minute p95 API latency exceeds 2 seconds for 3 consecutive datapoints (yes/no).
- **REQ-004 Acceptance criteria:**
	- AC-004.1 Given 1-minute p95 API latency greater than 2 seconds for 3 consecutive datapoints, when the system evaluates latency, then it identifies a latency spike.
	- AC-004.2 Given 1-minute p95 API latency greater than 2 seconds for only 2 consecutive datapoints, when the system evaluates latency, then it does not identify a latency spike.
- **REQ-005 Statement:** When a latency spike occurs and, over the same window as the spike, average CPU usage exceeds 80% or average memory usage exceeds 75%, the system shall classify it as an infrastructure issue; when average CPU usage is at or below 80% and average memory usage is at or below 75% over that window, the system shall classify it as an application bottleneck.
- **REQ-005 Success criterion:** The spike is classified as infrastructure when average CPU exceeds 80% or average memory exceeds 75% over the spike window, and as an application bottleneck when average CPU is at or below 80% and average memory at or below 75% (yes/no).
- **REQ-005 Acceptance criteria:**
	- AC-005.1 Given a latency spike and, over the spike window, average CPU usage greater than 80% or average memory usage greater than 75%, when the system classifies the cause, then it identifies an infrastructure issue.
	- AC-005.2 Given a latency spike and, over the spike window, average CPU usage at or below 80% and average memory usage at or below 75%, when the system classifies the cause, then it identifies an application bottleneck.
	- AC-005.3 Given a latency spike with average CPU usage of exactly 80% and average memory usage of exactly 75% over the spike window, when the system classifies the cause, then it identifies an application bottleneck.
- **REQ-006 Statement:** When the system assigns priority to a latency alert, it shall use the source's stated mapping: P1 for latency combined with 5XX, P2 for infrastructure saturation leading to latency, P3 for debug/analytics endpoints, P4 for short-lived latency that returns to 2 seconds or less within 5 minutes of the spike being identified without intervention, and P5 for non-user-facing staging traffic.
- **REQ-006 Success criterion:** The assigned priority matches the stated P1–P5 condition (yes/no).
- **REQ-006 Acceptance criteria:**
	- AC-006.1 Given latency combined with 5XX, when priority is assigned, then the priority is P1.
	- AC-006.2 Given infrastructure saturation leading to latency, when priority is assigned, then the priority is P2.
	- AC-006.3 Given a latency alert on a debug or analytics endpoint, when priority is assigned, then the priority is P3.
	- AC-006.4 Given latency that returns to 2 seconds or less within 5 minutes of the spike being identified, without intervention, when priority is assigned, then the priority is P4.
	- AC-006.5 Given non-user-facing staging traffic with a latency alert, when priority is assigned, then the priority is P5.
	- AC-006.6 Given latency still above 2 seconds 5 minutes after the spike was identified, when priority is assigned, then the short-lived P4 rule does not apply.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Candidate 3: Monitor Disk Usage and Assign Alert Priorities

- **Slug:** `monitor-disk-usage-alerts`
- **Requirements:** REQ-010, REQ-011
- **Open blockers:** Q-001 is deferred (alerting system/population). Q-008 and Q-028 are answered; the clarified decommissioning and categorical-priority behavior differs from the source and should be reconciled in Confluence before a later harvest.
- **Main risk:** The clarified categorical P4/P5 overrides are intentional policy choices that differ from the source's global highest-severity rule unless modeled as explicit exceptions.

**Assess prompt**

`/speckit-assess-intake "Specify disk usage alerting with 5-minute evaluation, decommissioning suppression/closure, percentage thresholds, and categorical P4/P5 overrides. Grounded in docs/requirements/harvested.md REQ-010, REQ-011; source .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=monitor-disk-usage-alerts`

**Specify prompt**

Create a feature specification for disk usage alert detection and priority assignment. Ground it in `docs/requirements/harvested.md` and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`.

- **REQ-010 Statement:** When disk usage, evaluated every 5 minutes, exceeds 84%, the system shall raise a disk usage alert, unless the node is flagged for decommissioning.
- **REQ-010 Success criterion:** Disk usage above 84% at a 5-minute evaluation raises an alert unless the node is flagged for decommissioning, and flagging a node closes its open disk alerts (yes/no).
- **REQ-010 Acceptance criteria:**
	- AC-010.1 Given disk usage above 84% on a node not flagged for decommissioning, when the system evaluates usage at its 5-minute interval, then it raises a disk usage alert.
	- AC-010.2 Given disk usage above 84% on a node flagged for decommissioning, when the system evaluates usage, then it raises no new disk usage alert.
	- AC-010.3 Given an open disk usage alert on a node, when the node is flagged for decommissioning, then the system closes that alert.
	- AC-010.4 Given disk usage of exactly 84%, when the system evaluates usage, then it raises no disk usage alert.
- **REQ-011 Statement:** When the system assigns priority to a disk usage alert, it shall assign P2 above 90% or P3 above 84% through 90%, unless a categorical rule applies; cold-storage or non-production alerts receive P4, and duplicate, already ticketed, or acknowledged alerts receive P5, overriding the percentage-based priority. When multiple categorical rules apply, the highest severity (P1 worst) is used.
- **REQ-011 Success criterion:** The assigned priority matches the percentage-based condition unless an applicable P4/P5 categorical condition overrides it; when multiple categorical conditions apply, the highest severity is assigned (yes/no).
- **REQ-011 Acceptance criteria:**
	- AC-011.1 Given disk usage above 90%, when priority is assigned, then the priority is P2.
	- AC-011.2 Given disk usage above 84% and at most 90%, when priority is assigned, then the priority is P3.
	- AC-011.3 Given a disk alert for a cold-storage volume or a non-production environment, when priority is assigned, then the priority is P4 even if the usage-based priority is P2 or P3.
	- AC-011.4 Given a duplicate disk alert or an alert already ticketed or acknowledged, when priority is assigned, then the priority is P5 even if the usage-based priority is P2 or P3.
	- AC-011.5 Given disk usage above 84% but below 85%, when priority is assigned, then the priority is P3.
	- AC-011.6 Given disk usage of exactly 90%, when priority is assigned, then the priority is P3.
	- AC-011.7 Given a disk alert that is both for a cold-storage volume and a duplicate alert, when priority is assigned, then the priority is P4 as the higher severity of the applicable categorical rules.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Candidate 4: Validate Network Errors and Assign Priorities

- **Slug:** `validate-network-errors-and-priorities`
- **Requirements:** REQ-012, REQ-013
- **Open blockers:** Q-001 is deferred (alerting system/population). Related service-group scope in Q-002 is deferred; REQ-020 is needs-human and excluded.
- **Main risk:** P2 depends on production-service scope, while Q-002 leaves the production/business-critical service inventory unspecified.

**Assess prompt**

`/speckit-assess-intake "Specify network error validation across services and nodes and assign the clarified priority mapping, including the two-service P2 case. Grounded in docs/requirements/harvested.md REQ-012, REQ-013; source .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=validate-network-errors-and-priorities`

**Specify prompt**

Create a feature specification for validating network errors and assigning their priorities. Ground it in `docs/requirements/harvested.md` and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`.

- **REQ-012 Statement:** When validating a timeout or connection-refused error, the system shall confirm a network error if such errors appear on 2 or more services or 2 or more nodes within the same 5-minute window; otherwise it shall treat the error as affecting one service.
- **REQ-012 Success criterion:** A network error is confirmed when timeout or connection-refused errors appear on 2 or more services or 2 or more nodes within one 5-minute window (yes/no).
- **REQ-012 Acceptance criteria:**
	- AC-012.1 Given timeout or connection-refused errors on 2 services within the same 5-minute window, when the system validates them, then it confirms a network error.
	- AC-012.2 Given timeout or connection-refused errors on 2 nodes within the same 5-minute window, when the system validates them, then it confirms a network error.
	- AC-012.3 Given timeout or connection-refused errors on only 1 service and 1 node within a 5-minute window, when the system validates them, then it treats the error as affecting one service.
- **REQ-013 Statement:** When the system assigns priority to a network error, it shall use the source's stated mapping: P1 for cluster-wide impact (errors on at least 50% of a cluster's nodes or on 3 or more services); P2 for one affected production service or errors on exactly 2 services below the cluster-wide threshold; P3 for staging-only disruption; P4 when the first retry succeeds or a DNS failure resolves on retry within 1 minute; and P5 for synthetic-probe timeouts or false alarms (probe errors with no matching user-traffic errors).
- **REQ-013 Success criterion:** The assigned priority matches the stated P1–P5 condition (yes/no).
- **REQ-013 Acceptance criteria:**
	- AC-013.1 Given network errors on at least 50% of a cluster's nodes, when priority is assigned, then the priority is P1.
	- AC-013.2 Given one affected production service, when priority is assigned, then the priority is P2.
	- AC-013.3 Given a staging-only network disruption, when priority is assigned, then the priority is P3.
	- AC-013.4 Given a network error where the first retry succeeds, or a DNS failure that resolves on retry within 1 minute, when priority is assigned, then the priority is P4.
	- AC-013.5 Given a synthetic-probe timeout, or probe errors with no matching user-traffic errors, when priority is assigned, then the priority is P5.
	- AC-013.6 Given network errors on 3 or more services, when priority is assigned, then the priority is P1.
	- AC-013.7 Given a DNS failure that has not resolved on retry after 1 minute, when priority is assigned, then it is not treated as a temporary DNS failure.
	- AC-013.8 Given a confirmed network error on exactly 2 services and fewer than 50% of a cluster's nodes, when priority is assigned, then the priority is P2.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Candidate 5: Categorize Business-Logic Failures from Logs

- **Slug:** `categorize-business-logic-failures`
- **Requirements:** REQ-014
- **Open blockers:** Q-001 is deferred (alerting system/population). REQ-015 is needs-human and excluded (business-logic priority mapping); REQ-016 is needs-human and excluded (overall category precedence).
- **Main risk:** This candidate covers categorization only; adding priority assignment or assuming how this category interacts with other indicators would exceed confirmed scope.

**Assess prompt**

`/speckit-assess-intake "Specify log-based categorization of alerts when logs exactly match one of the four named business-logic phrases. Grounded in docs/requirements/harvested.md REQ-014; source .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=categorize-business-logic-failures`

**Specify prompt**

Create a feature specification for categorizing business-logic failures from exact log-phrase matches. Ground it in `docs/requirements/harvested.md` and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`.

- **REQ-014 Statement:** When logs contain an exact match for one of the four listed phrases, the system shall categorize the alert as Application / Business domain.
- **REQ-014 Success criterion:** An alert whose logs exactly match one of the four listed phrases is categorized as Application / Business domain (yes/no).
- **REQ-014 Acceptance criteria:** AC-014.1 Given logs containing an exact match for “payment failed,” “order creation failed,” “inventory mismatch,” or “redis failure,” when the system categorizes the alert, then it assigns Application / Business domain.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Candidate 6: Resolve Priority Conflicts and Insufficient Evidence

- **Slug:** `resolve-alert-priority-conflicts-and-insufficient-evidence`
- **Requirements:** REQ-017, REQ-018, REQ-019
- **Open blockers:** Q-001 is deferred (alerting system/population); Q-002 is deferred (service groups and the meaning of higher priority); REQ-020 is needs-human and excluded (business-critical service priority policy).
- **Main risk:** The general highest-severity and evidence fallback rules may interact with unresolved service-specific policies; keep those policies outside this candidate.

**Assess prompt**

`/speckit-assess-intake "Specify highest-severity resolution when multiple priority rules apply, plus Unknown/P5 fallback for missing required alert data or inconclusive allowed evidence. Grounded in docs/requirements/harvested.md REQ-017, REQ-018, REQ-019; source .specify/harvest/raw/astra-alert-rules/page-1398800396.md. Research local snapshot and codebase first." slug=resolve-alert-priority-conflicts-and-insufficient-evidence`

**Specify prompt**

Create a feature specification for resolving overlapping alert priorities and handling insufficient or inconclusive evidence. Ground it in `docs/requirements/harvested.md` and `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`.

- **REQ-017 Statement:** When multiple rules apply to an alert, the system shall select the highest severity, where P1 is the worst severity.
- **REQ-017 Success criterion:** When multiple rules apply, the selected priority is the highest severity, with P1 worst.
- **REQ-017 Acceptance criteria:** AC-017.1 Given an alert to which P1 and P4 priority rules apply, when the system resolves priority, then it selects P1 as the highest severity.
- **REQ-018 Statement:** When an alert is missing its service, timestamp, or error signal, the system shall assign category Unknown and priority P5; when available evidence is inconclusive, the system shall also assign category Unknown and priority P5.
- **REQ-018 Success criterion:** An alert missing any of service, timestamp, or error signal, or having inconclusive evidence, receives category Unknown and priority P5 (yes/no).
- **REQ-018 Acceptance criteria:**
	- AC-018.1 Given an alert missing its service, timestamp, or error signal, when the system classifies the alert, then it assigns Unknown and P5.
	- AC-018.2 Given the available alert payload and service metrics are inconclusive, when the system classifies the alert, then it assigns Unknown and P5.
- **REQ-019 Statement:** When assigning an alert priority, the system shall use only the alert payload and service metrics as evidence and shall assign Unknown/P5 when that evidence is inconclusive.
- **REQ-019 Success criterion:** The assigned priority is derived only from the alert payload and service metrics, and inconclusive evidence results in Unknown/P5 (yes/no).
- **REQ-019 Acceptance criteria:**
	- AC-019.1 Given an alert requiring a priority, when the system assigns priority, then it uses only the alert payload and service metrics as evidence.
	- AC-019.2 Given the alert payload and service metrics are inconclusive, when the system assigns priority, then it assigns Unknown/P5.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Candidate 7: Integrate the Alert Bot with Microsoft Teams

- **Slug:** `integrate-alert-bot-with-microsoft-teams`
- **Requirements:** REQ-024–REQ-032
- **Open blockers:** Q-022 is deferred and REQ-023 is needs-human (public endpoint domain/authenticated messaging endpoint). REQ-028 conflicts with the current Confluence page's listed message-read permissions; the clarification resolves the requirement by removing those permissions, but the source page should be updated. Q-001 is deferred for the alerting system/population.
- **Main risk:** The Teams setup is broadly specified, but its public endpoint domain is unresolved and its confirmed no-read-permission policy differs from the captured source.

**Assess prompt**

`/speckit-assess-intake "Specify Azure Bot and Microsoft Teams integration for one-way delivery of alert validity, category, and priority results, including tenant configuration, credentials, permissions, notifications, and app publication. Grounded in docs/requirements/harvested.md REQ-024–REQ-032; source .specify/harvest/raw/astra-alert-rules/page-1514635295.md. Research local snapshot and codebase first." slug=integrate-alert-bot-with-microsoft-teams`

**Specify prompt**

Create a feature specification for integrating the alert bot with Microsoft Teams. Ground it in `docs/requirements/harvested.md` and `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`. Keep endpoint configuration from REQ-023 out of confirmed scope; list its unresolved domain as a blocker.

- **REQ-024 Statement:** The backend application shall be configured with `MicrosoftAppId` set to the Application (Client) ID, `MicrosoftAppPassword` set to the client secret read from Azure Key Vault (readable only by the backend application's managed identity), and `MicrosoftAppTenantId` set to the Directory (Tenant) ID.
- **REQ-024 Success criterion:** All 3 settings hold the values from the Azure App Registration, the client secret is read from Azure Key Vault, and only the backend application's managed identity can read it (yes/no).
- **REQ-024 Acceptance criteria:**
	- AC-024.1 Given the app registration's client ID, client secret and tenant ID, when the backend configuration is inspected, then `MicrosoftAppId`, `MicrosoftAppPassword` and `MicrosoftAppTenantId` hold those values.
	- AC-024.2 Given the deployed backend application, when the source of `MicrosoftAppPassword` is inspected, then the value is read from Azure Key Vault.
	- AC-024.3 Given the Azure Key Vault holding the client secret, when its access assignments are inspected, then only the backend application's managed identity can read the secret.
	- AC-024.4 Given an identity other than the backend application's managed identity, when it tries to read the client secret from Azure Key Vault, then access is denied.
- **REQ-025 Statement:** The Azure Bot resource's Microsoft App ID, the Teams app's App ID and the Teams app's Bot ID shall each equal the Azure App Registration's Application (Client) ID.
- **REQ-025 Success criterion:** All 3 IDs equal the Application (Client) ID (yes/no).
- **REQ-025 Acceptance criteria:** AC-025.1 Given the Azure App Registration's Application (Client) ID, when the Azure Bot's Microsoft App ID, the Teams app's App ID and its Bot ID are compared with it, then all 3 match.
- **REQ-026 Statement:** The Azure Bot resource shall have the Microsoft Teams channel enabled.
- **REQ-026 Success criterion:** Microsoft Teams is listed as an enabled channel on the Azure Bot resource (yes/no).
- **REQ-026 Acceptance criteria:** AC-026.1 Given the Azure Bot resource, when its Channels are inspected, then Microsoft Teams is enabled.
- **REQ-027 Statement:** The Teams app shall declare the Personal and Team bot scopes and shall not declare the Group Chat scope.
- **REQ-027 Success criterion:** The app manifest declares the Personal and Team scopes and does not declare Group Chat (yes/no).
- **REQ-027 Acceptance criteria:**
	- AC-027.1 Given the downloaded app manifest, when the bot scopes are inspected, then Personal and Team are declared.
	- AC-027.2 Given the downloaded app manifest, when the bot scopes are inspected, then Group Chat is not declared.
- **REQ-028 Statement:** The Teams app shall not request the `ChannelMessage.Read.Group` or `ChatMessage.Read.Chat` permissions.
- **REQ-028 Success criterion:** The app manifest declares neither permission (yes/no).
- **REQ-028 Acceptance criteria:** AC-028.1 Given the downloaded app manifest, when its permissions are inspected, then neither `ChannelMessage.Read.Group` nor `ChatMessage.Read.Chat` is declared.
- **REQ-029 Statement:** When the system produces an alert result (validity, category and priority), the Teams bot shall post it as a one-way notification to a designated alerts channel in Team scope.
- **REQ-029 Success criterion:** Send notifications is enabled, and each alert result appears as a bot notification in the designated alerts channel (yes/no).
- **REQ-029 Acceptance criteria:**
	- AC-029.1 Given the Teams app's bot configuration, when it is inspected, then Send notifications is enabled.
	- AC-029.2 Given an alert the system has validated, categorised and prioritised, when the result is produced, then the bot posts a notification containing the alert's validity, category and priority to the designated alerts channel.
	- AC-029.3 Given a user replies to or sends a command to the bot in Teams, when the bot receives it, then the bot does not act on it as a reply or command.
	- AC-029.4 Given an alert result is produced, when users' personal chats with the bot are inspected, then no notification for that result appears there.
- **REQ-030 Statement:** The Azure App Registration shall use the single-tenant supported account type.
- **REQ-030 Success criterion:** The app registration's supported account type is single tenant (yes/no).
- **REQ-030 Acceptance criteria:** AC-030.1 Given the Azure App Registration, when its supported account type is inspected, then it is single tenant.
- **REQ-031 Statement:** The Azure App Registration's client secret shall have a 6-month expiry and be rotated 30 days before it expires.
- **REQ-031 Success criterion:** The client secret has a 6-month expiry and is replaced 30 days before it expires (yes/no).
- **REQ-031 Acceptance criteria:**
	- AC-031.1 Given the client secret under Certificates & Secrets, when it is inspected, then an expiry date is set.
	- AC-031.2 Given the client secret is 30 days from expiry, when that point is reached, then a new client secret with a 6-month expiry replaces it in Azure Key Vault.
	- AC-031.3 Given the client secret under Certificates & Secrets, when its expiry is inspected, then the expiry period is 6 months.
- **REQ-032 Statement:** The Teams app package shall be submitted through Teams Admin Center, where a Teams admin approves it for installation by all users in the tenant.
- **REQ-032 Success criterion:** After a Teams admin approves the submission, any user in the tenant can install the bot inside Microsoft Teams (yes/no).
- **REQ-032 Acceptance criteria:** AC-032.1 Given the app package downloaded from Developer Portal containing `manifest.json`, `color.png` and `outline.png`, when it is submitted through Teams Admin Center and approved by a Teams admin, then any user in the tenant can install the bot inside Microsoft Teams.

Use the acceptance criteria as the spec's acceptance scenarios and the success criteria as its measurable success criteria. Do not invent details. Keep every [NEEDS CLARIFICATION] and [ASSUMED] marker. Cite REQ and AC IDs in the spec.

## Next Steps

The assess extension was not found at `.specify/extensions/assess`. To enable assess intake, run `specify extension add assess`; the specify prompts remain the main path. Review and commit this candidate file before starting any spec. Do not run an assess or specify prompt as part of this proposal step.
