# Harvested requirements

Snapshot: 2026-10-09T08:54:19+00:00 · Sources: astra-alert-rules · Focus: all snapshot content

## Requirements

### REQ-001 Validate 5XX errors
- **Statement:** When an alert contains an HTTP 500–599 code and its message indicates a failure, the system shall mark the alert as VALID. [NEEDS CLARIFICATION: Which message patterns, beyond the examples, indicate a failure?]
- **Success criterion:** The alert is marked VALID when a 5XX code and a failure-indicating message are present; [NEEDS CLARIFICATION: which message patterns qualify beyond the examples?]
- **Acceptance criteria:**
	- AC-001.1 Given an alert with HTTP 500, 502, 503, or 504 and a message containing “unable to connect,” “failed,” “timeout,” or “unreachable,” when the system validates it, then the alert is marked VALID.
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 1. 5XX Errors (API / Backend)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** HTTP 500, 502, 503, and 504 are examples of 5XX triggers; failure-message examples include “unable to connect,” “failed,” “timeout,” and “unreachable.”

### REQ-002 Filter 5XX noise
- **Statement:** When an alert contains a 5XX code and its message indicates noise, the system shall mark the alert as FALSE POSITIVE. [NEEDS CLARIFICATION: Which message patterns count as noise, beyond the examples?]
- **Success criterion:** The alert is marked FALSE POSITIVE when a 5XX code and a noise-indicating message are present; [NEEDS CLARIFICATION: which message patterns qualify beyond the examples?]
- **Acceptance criteria:**
	- AC-002.1 Given an alert with a 5XX code and a message containing “probe failure,” “transient,” “intermittent,” or “staging,” when the system validates it, then the alert is marked FALSE POSITIVE.
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 1. 5XX Errors (API / Backend)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** Noise-message examples are “probe failure,” “transient,” “intermittent,” and “staging.”

### REQ-003 Assign 5XX priorities
- **Statement:** When the system assigns priority to a 5XX alert, it shall use the source's stated mapping: P1 for Cart, Checkout, Payment, Auth, or Recommendations; P2 for non-critical production APIs; P3 for Dev/Staging environments; P4 for intermittent errors that auto-recovered with no user impact; and P5 for alerts triggered by retries or synthetic-monitoring noise. [NEEDS CLARIFICATION: what defines a non-critical production API, and what qualifies as intermittent and auto-recovered?]
- **Success criterion:** The assigned priority matches the stated P1–P5 condition; [NEEDS CLARIFICATION: what defines a non-critical production API, and what qualifies as intermittent and auto-recovered?]
- **Acceptance criteria:**
	- AC-003.1 Given a 5XX alert for Cart, Checkout, Payment, Auth, or Recommendations, when priority is assigned, then the priority is P1.
	- AC-003.2 Given a 5XX alert for a non-critical production API, when priority is assigned, then the priority is P2. [NEEDS CLARIFICATION: how is this API group defined?]
	- AC-003.3 Given a 5XX alert from a Dev/Staging environment, when priority is assigned, then the priority is P3.
	- AC-003.4 Given an intermittent 5XX error that auto-recovered with no user impact, when priority is assigned, then the priority is P4. [NEEDS CLARIFICATION: what qualifies as intermittent and auto-recovered?]
	- AC-003.5 Given a 5XX alert triggered by retries or synthetic-monitoring noise, when priority is assigned, then the priority is P5.
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 1. 5XX Errors (API / Backend)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P1–P5 conditions for 5XX alerts and separately says below-threshold alerts are FALSE POSITIVE → P5.

### REQ-004 Detect latency spikes
- **Statement:** When 1-minute p95 API latency exceeds 2 seconds for 3 consecutive datapoints, the system shall identify a latency spike.
- **Success criterion:** A latency spike is identified when 1-minute p95 API latency exceeds 2 seconds for 3 consecutive datapoints (yes/no).
- **Acceptance criteria:**
	- AC-004.1 Given 1-minute p95 API latency greater than 2 seconds for 3 consecutive datapoints, when the system evaluates latency, then it identifies a latency spike.
	- AC-004.2 Given 1-minute p95 API latency greater than 2 seconds for only 2 consecutive datapoints, when the system evaluates latency, then it does not identify a latency spike.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 2. Latency Spikes (API Latency > 2s)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The trigger is latency greater than 2 seconds for 3 consecutive datapoints. Q-006: each datapoint is 1-minute p95 API latency.

### REQ-005 Categorize latency causes
- **Statement:** When a latency spike occurs and, over the same window as the spike, average CPU usage exceeds 80% or average memory usage exceeds 75%, the system shall classify it as an infrastructure issue; when average CPU usage is at or below 80% and average memory usage is at or below 75% over that window, the system shall classify it as an application bottleneck.
- **Success criterion:** The spike is classified as infrastructure when average CPU exceeds 80% or average memory exceeds 75% over the spike window, and as an application bottleneck when average CPU is at or below 80% and average memory at or below 75% (yes/no).
- **Acceptance criteria:**
-	- AC-005.1 Given a latency spike and, over the spike window, average CPU usage greater than 80% or average memory usage greater than 75%, when the system classifies the cause, then it identifies an infrastructure issue.
	- AC-005.2 Given a latency spike and, over the spike window, average CPU usage at or below 80% and average memory usage at or below 75%, when the system classifies the cause, then it identifies an application bottleneck.
	- AC-005.3 Given a latency spike with average CPU usage of exactly 80% and average memory usage of exactly 75% over the spike window, when the system classifies the cause, then it identifies an application bottleneck.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 2. Latency Spikes (API Latency > 2s)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** CPU above 80% or memory above 75% indicates infrastructure; healthy infrastructure indicates an application bottleneck. Q-007 sets the spike window and strict boundaries; Q-027 selects average usage.

### REQ-006 Assign latency priorities
- **Statement:** When the system assigns priority to a latency alert, it shall use the source's stated mapping: P1 for latency combined with 5XX, P2 for infrastructure saturation leading to latency, P3 for debug/analytics endpoints, P4 for short-lived latency that returns to 2 seconds or less within 5 minutes of the spike being identified without intervention, and P5 for non-user-facing staging traffic.
- **Success criterion:** The assigned priority matches the stated P1–P5 condition (yes/no).
- **Acceptance criteria:**
	- AC-006.1 Given latency combined with 5XX, when priority is assigned, then the priority is P1.
	- AC-006.2 Given infrastructure saturation leading to latency, when priority is assigned, then the priority is P2.
	- AC-006.3 Given a latency alert on a debug or analytics endpoint, when priority is assigned, then the priority is P3.
	- AC-006.4 Given latency that returns to 2 seconds or less within 5 minutes of the spike being identified, without intervention, when priority is assigned, then the priority is P4.
	- AC-006.5 Given non-user-facing staging traffic with a latency alert, when priority is assigned, then the priority is P5.
	- AC-006.6 Given latency still above 2 seconds 5 minutes after the spike was identified, when priority is assigned, then the short-lived P4 rule does not apply.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 2. Latency Spikes (API Latency > 2s)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P1–P5 conditions for latency alerts. Q-006: short-lived = back to ≤2 s within 5 minutes without intervention.

### REQ-007 Detect pod restart loops
- **Statement:** When a Kubernetes pod restarts more than 5 times within 10 minutes, the system shall identify a pod restart loop.
- **Success criterion:** The system identifies a pod restart loop when restarts exceed 5 within 10 minutes.
- **Acceptance criteria:**
	- AC-007.1 Given a Kubernetes pod with 6 restarts within 10 minutes, when the system evaluates the restart count, then it identifies a pod restart loop.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 3. Pod Restart Loop (Kubernetes)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The trigger is more than 5 restarts within 10 minutes.

### REQ-008 Validate pod restart loops from logs
- **Statement:** When validating a pod restart loop, the system shall check logs for `OOMKilled`, `CrashLoopBackOff`, and `ImagePullBackoff`.
- **Success criterion:** The system checks for all 3 log indicators named by the source.
- **Acceptance criteria:**
	- AC-008.1 Given a pod restart-loop validation, when the system checks logs, then it checks for `OOMKilled`, `CrashLoopBackOff`, and `ImagePullBackoff`.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 3. Pod Restart Loop (Kubernetes)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** These three log indicators are listed for validation.

### REQ-009 Assign pod restart priorities
- **Statement:** When the system assigns priority to a pod restart alert, it shall use the source's stated mapping: P1 for production business services, P2 for staging or shared services, P3 for Dev/test environments, P4 for expected node-drain or maintenance restarts, and P5 for autoscaling-driven scheduled restarts. [NEEDS CLARIFICATION: What defines a production business service?]
- **Success criterion:** The assigned priority matches the stated P1–P5 condition; [NEEDS CLARIFICATION: which services are production business services?]
- **Acceptance criteria:**
	- AC-009.1 Given a pod restart alert for a production business service, when priority is assigned, then the priority is P1. [NEEDS CLARIFICATION: which services are in this group?]
	- AC-009.2 Given a pod restart alert for a staging or shared service, when priority is assigned, then the priority is P2.
	- AC-009.3 Given a pod restart alert in a Dev/test environment, when priority is assigned, then the priority is P3.
	- AC-009.4 Given an expected node-drain or maintenance restart, when priority is assigned, then the priority is P4.
	- AC-009.5 Given an autoscaling-driven scheduled restart, when priority is assigned, then the priority is P5.
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 3. Pod Restart Loop (Kubernetes)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P1–P5 conditions for pod restart alerts.

### REQ-010 Detect disk usage alerts
- **Statement:** When disk usage, evaluated every 5 minutes, exceeds 84%, the system shall raise a disk usage alert, unless the node is flagged for decommissioning.
- **Success criterion:** Disk usage above 84% at a 5-minute evaluation raises an alert unless the node is flagged for decommissioning, and flagging a node closes its open disk alerts (yes/no).
- **Acceptance criteria:**
	- AC-010.1 Given disk usage above 84% on a node not flagged for decommissioning, when the system evaluates usage at its 5-minute interval, then it raises a disk usage alert.
	- AC-010.2 Given disk usage above 84% on a node flagged for decommissioning, when the system evaluates usage, then it raises no new disk usage alert.
	- AC-010.3 Given an open disk usage alert on a node, when the node is flagged for decommissioning, then the system closes that alert.
	- AC-010.4 Given disk usage of exactly 84%, when the system evaluates usage, then it raises no disk usage alert.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 4. Disk Usage Alerts](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The trigger is usage above 84%; alerts are ignored if the node is flagged for decommissioning. Q-008: evaluated every 5 minutes; the flag suppresses new alerts and closes existing ones.

### REQ-011 Assign disk usage priorities
- **Statement:** When the system assigns priority to a disk usage alert, it shall assign P2 above 90% or P3 above 84% through 90%, unless a categorical rule applies; cold-storage or non-production alerts receive P4, and duplicate, already ticketed, or acknowledged alerts receive P5, overriding the percentage-based priority. When multiple categorical rules apply, the highest severity (P1 worst) is used.
- **Success criterion:** The assigned priority matches the percentage-based condition unless an applicable P4/P5 categorical condition overrides it; when multiple categorical conditions apply, the highest severity is assigned (yes/no).
- **Acceptance criteria:**
	- AC-011.1 Given disk usage above 90%, when priority is assigned, then the priority is P2.
	- AC-011.2 Given disk usage above 84% and at most 90%, when priority is assigned, then the priority is P3.
	- AC-011.3 Given a disk alert for a cold-storage volume or a non-production environment, when priority is assigned, then the priority is P4 even if the usage-based priority is P2 or P3.
	- AC-011.4 Given a duplicate disk alert or an alert already ticketed or acknowledged, when priority is assigned, then the priority is P5 even if the usage-based priority is P2 or P3.
	- AC-011.5 Given disk usage above 84% but below 85%, when priority is assigned, then the priority is P3.
	- AC-011.6 Given disk usage of exactly 90%, when priority is assigned, then the priority is P3.
	- AC-011.7 Given a disk alert that is both for a cold-storage volume and a duplicate alert, when priority is assigned, then the priority is P4 as the higher severity of the applicable categorical rules.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 4. Disk Usage Alerts](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P2–P5 conditions, while its alert trigger begins above 84%. Q-008 sets the 5-minute evaluation and P3 range; Q-028 specifies that P4/P5 categorical conditions override percentage thresholds and that highest severity resolves multiple categorical rules. See the resolved conflict entry.

### REQ-012 Validate network errors
- **Statement:** When validating a timeout or connection-refused error, the system shall confirm a network error if such errors appear on 2 or more services or 2 or more nodes within the same 5-minute window; otherwise it shall treat the error as affecting one service.
- **Success criterion:** A network error is confirmed when timeout or connection-refused errors appear on 2 or more services or 2 or more nodes within one 5-minute window (yes/no).
- **Acceptance criteria:**
	- AC-012.1 Given timeout or connection-refused errors on 2 services within the same 5-minute window, when the system validates them, then it confirms a network error.
	- AC-012.2 Given timeout or connection-refused errors on 2 nodes within the same 5-minute window, when the system validates them, then it confirms a network error.
	- AC-012.3 Given timeout or connection-refused errors on only 1 service and 1 node within a 5-minute window, when the system validates them, then it treats the error as affecting one service.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 5. Network Errors (Timeout, Connection Refused)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source categorizes timeout and connection-refused errors as network/connectivity and directs checking multiple services and nodes. Q-009: 2 or more services or nodes within one 5-minute window.

### REQ-013 Assign network error priorities
- **Statement:** When the system assigns priority to a network error, it shall use the source's stated mapping: P1 for cluster-wide impact (errors on at least 50% of a cluster's nodes or on 3 or more services); P2 for one affected production service or errors on exactly 2 services below the cluster-wide threshold; P3 for staging-only disruption; P4 when the first retry succeeds or a DNS failure resolves on retry within 1 minute; and P5 for synthetic-probe timeouts or false alarms (probe errors with no matching user-traffic errors).
- **Success criterion:** The assigned priority matches the stated P1–P5 condition (yes/no).
- **Acceptance criteria:**
	- AC-013.1 Given network errors on at least 50% of a cluster's nodes, when priority is assigned, then the priority is P1.
	- AC-013.2 Given one affected production service, when priority is assigned, then the priority is P2.
	- AC-013.3 Given a staging-only network disruption, when priority is assigned, then the priority is P3.
	- AC-013.4 Given a network error where the first retry succeeds, or a DNS failure that resolves on retry within 1 minute, when priority is assigned, then the priority is P4.
	- AC-013.5 Given a synthetic-probe timeout, or probe errors with no matching user-traffic errors, when priority is assigned, then the priority is P5.
	- AC-013.6 Given network errors on 3 or more services, when priority is assigned, then the priority is P1.
	- AC-013.7 Given a DNS failure that has not resolved on retry after 1 minute, when priority is assigned, then it is not treated as a temporary DNS failure.
	- AC-013.8 Given a confirmed network error on exactly 2 services and fewer than 50% of a cluster's nodes, when priority is assigned, then the priority is P2.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 5. Network Errors (Timeout, Connection Refused)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P1–P5 conditions for network errors. Q-010 defines cluster-wide impact, temporary DNS failure, false alarm and single-retry success; Q-029 assigns P2 to exactly 2 affected services below the cluster-wide threshold.

### REQ-014 Categorize business logic failures
- **Statement:** When logs contain an exact match for one of the four listed phrases, the system shall categorize the alert as Application / Business domain.
- **Success criterion:** An alert whose logs exactly match one of the four listed phrases is categorized as Application / Business domain (yes/no).
- **Acceptance criteria:**
-	- AC-014.1 Given logs containing an exact match for “payment failed,” “order creation failed,” “inventory mismatch,” or “redis failure,” when the system categorizes the alert, then it assigns Application / Business domain.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § 6. Business Logic Failures (Logs)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The four listed phrases are exact-match indicators per Q-011.

### REQ-015 Assign business logic priorities
- **Statement:** When the system assigns priority to a business-logic alert, it shall use the source's stated mapping: P1 for Payment and Checkout failures, P2 for order-processing throughput reduced without total failure, P2 for Redis failures, P3 for inventory mismatches, P4 for incorrect analytics/metadata, and P5 for errors in a disabled feature path. [NEEDS CLARIFICATION: what measured reduction in order-processing throughput qualifies as degradation?]
- **Success criterion:** The assigned priority matches the stated P1–P5 condition (yes/no); [NEEDS CLARIFICATION: what measured throughput reduction qualifies for P2?]
- **Acceptance criteria:**
	- AC-015.1 Given a Payment or Checkout failure, when priority is assigned, then the priority is P1.
	- AC-015.2 Given order-processing throughput reduced without total failure by [NEEDS CLARIFICATION: what measured amount or percentage?], when priority is assigned, then the priority is P2.
	- AC-015.3 Given an inventory mismatch, when priority is assigned, then the priority is P3.
	- AC-015.4 Given incorrect analytics or metadata, when priority is assigned, then the priority is P4.
	- AC-015.5 Given an error in a disabled feature path, when priority is assigned, then the priority is P5.
	- AC-015.6 Given a Redis failure, when priority is assigned, then the priority is P2.
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 6. Business Logic Failures (Logs)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P1–P5 conditions for business-logic failures. Q-011 defines Redis failure as P2, order-processing degradation as reduced throughput without total failure, and an unused workflow as a disabled feature path; Q-030 remains open for a measurable degradation threshold.

### REQ-016 Categorize alerts by indicator
- **Statement:** When an alert matches a source-listed indicator, the system shall assign its stated category: HTTP 5XX or backend stack trace to Server issue; pod restarts or node pressure to Infrastructure; high latency alone to Application; DNS, routing, or connection refused to Network; fraud alerts or unauthorized access to Security; browser/client request failures to Client issue; missing context or unclear logs to Unknown; latency spikes due to an infrastructure cause to Infra bottleneck and otherwise to Application performance; disk usage alerts to Infrastructure; and network errors to Network / Connectivity. When a specific alert rule and a generic decision-tree indicator both match, the specific rule shall determine the category; when multiple specific rules match, the rule with the highest severity determines the category. [NEEDS CLARIFICATION: how are categories chosen when multiple specific rules of equal severity match?] [NEEDS CLARIFICATION: how are categories chosen when multiple generic decision-tree indicators match and no specific rule applies?]
- **Success criterion:** Every source-listed indicator is assigned its stated category, with specific rules taking precedence over generic indicators and highest severity resolving multiple specific matches (yes/no); [NEEDS CLARIFICATION: how are equal-severity specific matches and multiple generic indicators resolved?]
- **Acceptance criteria:**
	- AC-016.1 Given an HTTP 5XX alert, when the system categorizes it, then it assigns Server issue.
	- AC-016.2 Given pod restarts or node pressure, when the system categorizes the alert, then it assigns Infrastructure.
	- AC-016.3 Given high latency only, when the system categorizes the alert, then it assigns Application.
	- AC-016.4 Given DNS, routing, or connection-refused indicators, when the system categorizes the alert, then it assigns Network.
	- AC-016.5 Given a fraud alert or unauthorized access, when the system categorizes the alert, then it assigns Security.
	- AC-016.6 Given a browser/client request failure, when the system categorizes the alert, then it assigns Client issue.
	- AC-016.7 Given missing context or unclear logs, when the system categorizes the alert, then it assigns Unknown.
	- AC-016.8 Given both a specific alert rule and a generic decision-tree indicator match, when the system categorizes the alert, then the specific alert rule determines the category.
	- AC-016.9 Given multiple specific alert rules match, when the system categorizes the alert, then the category comes from the rule with the highest severity; if multiple matching rules have equal severity, then [NEEDS CLARIFICATION: which category takes precedence?].
	- AC-016.10 Given a disk usage alert, when the system categorizes it, then it assigns Infrastructure.
	- AC-016.11 Given a network error, when the system categorizes it, then it assigns Network / Connectivity.
	- AC-016.12 Given a backend stack trace, when the system categorizes the alert, then it assigns Server issue.
	- AC-016.13 Given a latency spike classified as an infrastructure issue, when the system categorizes it, then it assigns Infra bottleneck.
	- AC-016.14 Given a latency spike classified as an application bottleneck, when the system categorizes it, then it assigns Application performance.
	- AC-016.15 Given multiple generic decision-tree indicators match and no specific rule applies, when the system categorizes the alert, then [NEEDS CLARIFICATION: which category takes precedence?].
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § Categorization Decision Tree](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 1. 5XX Errors (API / Backend)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 2. Latency Spikes (API Latency > 2s)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 3. Pod Restart Loop (Kubernetes)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 4. Disk Usage Alerts](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 5. Network Errors (Timeout, Connection Refused)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The decision table and alert-specific sections map the listed indicators to categories. Q-014 sets specific-rule precedence and highest-severity category selection; Q-015 selects Server issue for 5XX and maps latency categories to the cause classification. Equal-severity and generic-only overlaps remain open.

### REQ-017 Resolve multiple applicable rules
- **Statement:** When multiple rules apply to an alert, the system shall select the highest severity, where P1 is the worst severity.
- **Success criterion:** When multiple rules apply, the selected priority is the highest severity, with P1 worst.
- **Acceptance criteria:**
	- AC-017.1 Given an alert to which P1 and P4 priority rules apply, when the system resolves priority, then it selects P1 as the highest severity.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § Global Rules](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The global rule says to pick the highest severity when multiple rules apply and identifies P1 as worst.

### REQ-018 Classify insufficient-data alerts
- **Statement:** When an alert is missing its service, timestamp, or error signal, the system shall assign category Unknown and priority P5; when available evidence is inconclusive, the system shall also assign category Unknown and priority P5.
- **Success criterion:** An alert missing any of service, timestamp, or error signal, or having inconclusive evidence, receives category Unknown and priority P5 (yes/no).
- **Acceptance criteria:**
	- AC-018.1 Given an alert missing its service, timestamp, or error signal, when the system classifies the alert, then it assigns Unknown and P5.
	- AC-018.2 Given the available alert payload and service metrics are inconclusive, when the system classifies the alert, then it assigns Unknown and P5.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § Global Rules](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source assigns Unknown and P5 when data is insufficient. Q-012 defines missing service, timestamp, or error signal as insufficient and assigns Unknown/P5 when evidence is inconclusive.

### REQ-019 Base priority on evidence
- **Statement:** When assigning an alert priority, the system shall use only the alert payload and service metrics as evidence and shall assign Unknown/P5 when that evidence is inconclusive.
- **Success criterion:** The assigned priority is derived only from the alert payload and service metrics, and inconclusive evidence results in Unknown/P5 (yes/no).
- **Acceptance criteria:**
	- AC-019.1 Given an alert requiring a priority, when the system assigns priority, then it uses only the alert payload and service metrics as evidence.
	- AC-019.2 Given the alert payload and service metrics are inconclusive, when the system assigns priority, then it assigns Unknown/P5.
- **Type:** functional
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1398800396 § Global Rules](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source says priority must never be based on a guess, only evidence. Q-012 limits evidence to alert payload and service metrics and specifies Unknown/P5 for inconclusive evidence.

### REQ-020 Prioritize business-critical services
- **Statement:** When assigning priority, the system shall prioritize business-critical services higher than other services. [NEEDS CLARIFICATION: Which services are business-critical, and what priority increase does “higher” require?]
- **Success criterion:** [NEEDS CLARIFICATION: which services are business-critical, and what measurable priority outcome means they are prioritized higher?]
- **Acceptance criteria:**
	- AC-020.1 Given an alert for a business-critical service and an otherwise comparable alert for another service, when priorities are assigned, then [NEEDS CLARIFICATION: what priority relationship demonstrates “higher,” and which services are business-critical?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § Global Rules](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source states that business-critical services are always prioritized higher.

### REQ-021 Classify below-threshold 5XX alerts
- **Statement:** When a 5XX alert is below the applicable threshold, the system shall mark it FALSE POSITIVE and assign priority P5. [NEEDS CLARIFICATION: What threshold and measurement determine this condition?]
- **Success criterion:** A 5XX alert below the applicable threshold is marked FALSE POSITIVE and assigned P5; [NEEDS CLARIFICATION: what threshold and measurement apply?]
- **Acceptance criteria:**
	- AC-021.1 Given a 5XX alert below the source-defined threshold, when the system evaluates it, then it marks the alert FALSE POSITIVE and assigns P5. [NEEDS CLARIFICATION: what threshold and measurement define “below”?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 1. 5XX Errors (API / Backend)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source states “If below threshold → FALSE POSITIVE → P5” but does not define the threshold.

### REQ-022 Determine 5XX validity when metrics are absent
- **Statement:** When rate or occurrence-count metrics are not provided for a 5XX alert, the system shall determine validity from message semantics. [NEEDS CLARIFICATION: Are the listed failure and noise cues exhaustive, and which outcome takes precedence if both occur?]
- **Success criterion:** When rate and occurrence-count metrics are absent, the system determines validity from the message; [NEEDS CLARIFICATION: are the cues exhaustive, and which outcome takes precedence if failure and noise cues both occur?]
- **Acceptance criteria:**
	- AC-022.1 Given a 5XX alert without rate or occurrence-count metrics and a message containing a listed failure cue, when the system determines validity, then it uses message semantics to mark the alert VALID.
	- AC-022.2 Given a 5XX alert without rate or occurrence-count metrics and a message containing a listed noise cue, when the system determines validity, then it uses message semantics to mark the alert FALSE POSITIVE.
	- AC-022.3 Given a 5XX alert whose message contains both failure and noise cues, when the system determines validity, then [NEEDS CLARIFICATION: which result takes precedence?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 1. 5XX Errors (API / Backend)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source says rate or occurrence count metrics are optional and message semantics determine validity when metrics are not provided.

### REQ-023 Expose the bot messaging endpoint
- **Statement:** The Azure Bot resource's Messaging Endpoint shall be the backend application's public HTTPS URL `https://<public-domain>/api/messages`, which accepts only requests authenticated as coming from Azure Bot Service. [NEEDS CLARIFICATION: what is the public domain for each environment?]
- **Success criterion:** The Messaging Endpoint equals `https://<public-domain>/api/messages`, the backend accepts authenticated Azure Bot Service requests there over public HTTPS, and it rejects unauthenticated ones (yes/no); [NEEDS CLARIFICATION: what is the public domain for each environment?]
- **Acceptance criteria:**
	- AC-023.1 Given the Azure Bot resource, when its Configuration is inspected, then the Messaging Endpoint is `https://[NEEDS CLARIFICATION: public domain]/api/messages`.
	- AC-023.2 Given the backend application is deployed, when an HTTPS request authenticated as coming from Azure Bot Service is sent from the public internet to `https://[NEEDS CLARIFICATION: public domain]/api/messages`, then the backend application accepts the request.
	- AC-023.3 Given the backend application is deployed, when a request to `/api/messages` is not authenticated as coming from Azure Bot Service, then the backend application rejects it.
- **Type:** functional (integration)
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1514635295 § Prerequisites](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § Step 3: Configure Messaging Endpoint](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** A public HTTPS endpoint is a prerequisite; Step 3 sets the messaging endpoint to `https://<your-public-domain>/api/messages`. Q-023: unauthenticated requests are rejected.

### REQ-024 Configure bot credentials in the backend
- **Statement:** The backend application shall be configured with `MicrosoftAppId` set to the Application (Client) ID, `MicrosoftAppPassword` set to the client secret read from Azure Key Vault (readable only by the backend application's managed identity), and `MicrosoftAppTenantId` set to the Directory (Tenant) ID.
- **Success criterion:** All 3 settings hold the values from the Azure App Registration, the client secret is read from Azure Key Vault, and only the backend application's managed identity can read it (yes/no).
- **Acceptance criteria:**
	- AC-024.1 Given the app registration's client ID, client secret and tenant ID, when the backend configuration is inspected, then `MicrosoftAppId`, `MicrosoftAppPassword` and `MicrosoftAppTenantId` hold those values.
	- AC-024.2 Given the deployed backend application, when the source of `MicrosoftAppPassword` is inspected, then the value is read from Azure Key Vault.
	- AC-024.3 Given the Azure Key Vault holding the client secret, when its access assignments are inspected, then only the backend application's managed identity can read the secret.
	- AC-024.4 Given an identity other than the backend application's managed identity, when it tries to read the client secret from Azure Key Vault, then access is denied.
- **Type:** functional (configuration)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § Step 1.1: Create Client Secret](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § Step 7: Application Configuration](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Steps 1.1 and 7 map the client ID, client secret and tenant ID to these three setting names. Q-019: the client secret is stored in Azure Key Vault. Q-025: only the backend's managed identity may read it.

### REQ-025 Use one App ID for the bot and Teams app
- **Statement:** The Azure Bot resource's Microsoft App ID, the Teams app's App ID and the Teams app's Bot ID shall each equal the Azure App Registration's Application (Client) ID.
- **Success criterion:** All 3 IDs equal the Application (Client) ID (yes/no).
- **Acceptance criteria:**
	- AC-025.1 Given the Azure App Registration's Application (Client) ID, when the Azure Bot's Microsoft App ID, the Teams app's App ID and its Bot ID are compared with it, then all 3 match.
- **Type:** non-functional (configuration)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § Step 2: Create Azure Bot Resource](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § 5.3 Configure App ID](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § 5.4 Configure Bot](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Step 2 selects the existing app registration; 5.3 states the App ID must match the Azure Bot App ID; 5.4 sets Bot ID to the same client ID.

### REQ-026 Enable the Microsoft Teams channel
- **Statement:** The Azure Bot resource shall have the Microsoft Teams channel enabled.
- **Success criterion:** Microsoft Teams is listed as an enabled channel on the Azure Bot resource (yes/no).
- **Acceptance criteria:**
	- AC-026.1 Given the Azure Bot resource, when its Channels are inspected, then Microsoft Teams is enabled.
- **Type:** functional (integration)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § Step 4: Enable Microsoft Teams Channel](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Step 4 selects Microsoft Teams under Channels and saves, which connects the bot to Teams.

### REQ-027 Declare bot scopes
- **Statement:** The Teams app shall declare the Personal and Team bot scopes and shall not declare the Group Chat scope.
- **Success criterion:** The app manifest declares the Personal and Team scopes and does not declare Group Chat (yes/no).
- **Acceptance criteria:**
	- AC-027.1 Given the downloaded app manifest, when the bot scopes are inspected, then Personal and Team are declared.
	- AC-027.2 Given the downloaded app manifest, when the bot scopes are inspected, then Group Chat is not declared.
- **Type:** functional (integration)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § 5.4 Configure Bot](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Supported scopes are Personal, Team, and Group Chat "(if required)". Q-017: Group Chat is not required.

### REQ-028 Do not request Teams message-read permissions
- **Statement:** The Teams app shall not request the `ChannelMessage.Read.Group` or `ChatMessage.Read.Chat` permissions.
- **Success criterion:** The app manifest declares neither permission (yes/no).
- **Acceptance criteria:**
	- AC-028.1 Given the downloaded app manifest, when its permissions are inspected, then neither `ChannelMessage.Read.Group` nor `ChatMessage.Read.Chat` is declared.
	- AC-028.2 *(withdrawn: Q-026 removed both read permissions, so the bot no longer reads channel or chat messages.)*
- **Type:** non-functional (security / permissions)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § 5.4 Configure Bot](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** 5.4 lists these two permissions. Q-026 overrides the source: the one-way bot does not use message content, so both permissions are dropped. Q-020 (read all, store nothing) is superseded. See Conflicts.

### REQ-029 Enable bot notifications
- **Statement:** When the system produces an alert result (validity, category and priority), the Teams bot shall post it as a one-way notification to a designated alerts channel in Team scope.
- **Success criterion:** Send notifications is enabled, and each alert result appears as a bot notification in the designated alerts channel (yes/no).
- **Acceptance criteria:**
	- AC-029.1 Given the Teams app's bot configuration, when it is inspected, then Send notifications is enabled.
	- AC-029.2 Given an alert the system has validated, categorised and prioritised, when the result is produced, then the bot posts a notification containing the alert's validity, category and priority to the designated alerts channel.
	- AC-029.3 Given a user replies to or sends a command to the bot in Teams, when the bot receives it, then the bot does not act on it as a reply or command.
	- AC-029.4 Given an alert result is produced, when users' personal chats with the bot are inspected, then no notification for that result appears there.
- **Type:** functional (notification)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § 5.4 Configure Bot](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** 5.4 says to enable Send notifications; no trigger or content is described. Q-016: the bot posts alert results to Teams one-way and does not accept replies or commands. Q-021: results go to a designated alerts channel in Team scope.

### REQ-030 Set the app registration account type
- **Statement:** The Azure App Registration shall use the single-tenant supported account type.
- **Success criterion:** The app registration's supported account type is single tenant (yes/no).
- **Acceptance criteria:**
	- AC-030.1 Given the Azure App Registration, when its supported account type is inspected, then it is single tenant.
- **Type:** non-functional (security / access)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § Step 1: Create Azure App Registration](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Step 1 offers "Single tenant or Multi-tenant" without choosing. Q-018: single tenant.

### REQ-031 Set a client secret expiry
- **Statement:** The Azure App Registration's client secret shall have a 6-month expiry and be rotated 30 days before it expires.
- **Success criterion:** The client secret has a 6-month expiry and is replaced 30 days before it expires (yes/no).
- **Acceptance criteria:**
	- AC-031.1 Given the client secret under Certificates & Secrets, when it is inspected, then an expiry date is set.
	- AC-031.2 Given the client secret is 30 days from expiry, when that point is reached, then a new client secret with a 6-month expiry replaces it in Azure Key Vault.
	- AC-031.3 Given the client secret under Certificates & Secrets, when its expiry is inspected, then the expiry period is 6 months.
- **Type:** non-functional (security)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § Step 1.1: Create Client Secret](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Step 1.1 says to add a description and expiry; no period is given. Q-025: 6-month expiry, rotated 30 days before expiry.

### REQ-032 Publish the Teams app through Teams Admin Center
- **Statement:** The Teams app package shall be submitted through Teams Admin Center, where a Teams admin approves it for installation by all users in the tenant.
- **Success criterion:** After a Teams admin approves the submission, any user in the tenant can install the bot inside Microsoft Teams (yes/no).
- **Acceptance criteria:**
	- AC-032.1 Given the app package downloaded from Developer Portal containing `manifest.json`, `color.png` and `outline.png`, when it is submitted through Teams Admin Center and approved by a Teams admin, then any user in the tenant can install the bot inside Microsoft Teams.
	- AC-032.2 *(withdrawn: the source and clarification do not specify app availability before approval.)*
- **Type:** functional (deployment)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § Step 5: Create Teams App Manifest](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § 5.5 Generate and Download manifest.json](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § Step 6: Upload/Submit the App to Teams](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Step 5 is required to install the bot in Teams; 5.5 downloads the package; Step 6 submits it via Teams Admin Center. Q-024: all tenant users may install; a Teams admin approves.

## Conflicts
| Conflict | Requirements | Sources | Question ID |
|---|---|---|---|
| No additional contradictions found beyond the rows below. Some priority boundaries and overlapping conditions remain underspecified; see open questions. | — | — | — |
| Source 5.4 lists `ChannelMessage.Read.Group` and `ChatMessage.Read.Chat`; the Q-026 answer drops both. **Resolved in favour of Q-026**; update the Confluence page to match. | REQ-028 | [astra-alert-rules/page-1514635295 § 5.4 Configure Bot](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | Q-026 |
| With the original percentage thresholds, the disk P4 (cold-storage / non-production) and P5 (duplicate / acknowledged) rules were unreachable under highest-severity-wins. **Resolved by Q-028:** categorical P4/P5 conditions override percentage-based P2/P3 rules; highest severity still resolves multiple categorical rules. | REQ-011, REQ-017 | [astra-alert-rules/page-1398800396 § 4. Disk Usage Alerts](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § Global Rules](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | Q-028 |
| The source says to ignore disk alerts on nodes flagged for decommissioning; Q-008 additionally says to close existing alerts. **Resolved by clarification**; update the Confluence page to make closure explicit. | REQ-010 | [astra-alert-rules/page-1398800396 § 4. Disk Usage Alerts](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | Q-008 |

## Open questions (ranked)
| QID | Rank | Impact | Question | Affects | Source | State |
|---|---:|---|---|---|---|---|
| Q-001 | 1 | Scope | Which alerting system and alert population does this rule set govern? | REQ-001–REQ-022 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-002 | 1 | Scope | Which service names belong to the business-critical, production-business, and non-critical production groups, and how should “higher” priority be represented? | REQ-003, REQ-009, REQ-020 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-016 | 1 | Scope | Is the Teams bot the channel that delivers the alert validation, category and priority results of REQ-001–REQ-022? What messages does it send or receive? | REQ-023–REQ-032 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-017 | 1 | Scope | Which users or teams must be able to install the app, who approves the Teams Admin Center submission, and is the Group Chat scope required? | REQ-027, REQ-032 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-024 | 1 | Scope | Which users or teams must be able to install the app, and who approves the Teams Admin Center submission? (Remainder of Q-017.) | REQ-032 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-003 | 2 | Security / privacy | The decision tree includes Security for fraud and unauthorized access, but gives no validation or priority rule. Should those alerts follow additional security-specific handling? Specify the handling. | REQ-016 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-018 | 2 | Security / privacy | Should the app registration be single-tenant or multi-tenant? | REQ-030 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-019 | 2 | Security / privacy | Where must the client secret be stored, who may read it, what expiry period applies, and how and when is it rotated? | REQ-024, REQ-031 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-020 | 2 | Security / privacy | `ChannelMessage.Read.Group` and `ChatMessage.Read.Chat` let the bot read messages in the teams and chats where it is installed. What message content may it read, and may it store that content (if so, for how long)? | REQ-028 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-023 | 2 | Security / privacy | Must the backend reject requests to `/api/messages` that are not authenticated as coming from Azure Bot Service? The page makes the endpoint public but states no request validation. | REQ-023 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-025 | 2 | Security / privacy | Who may read the client secret in Azure Key Vault, what expiry period applies, and how and when is it rotated? (Remainder of Q-019.) | REQ-024, REQ-031 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-026 | 2 | Security / privacy | Q-016 makes the bot one-way, yet Q-020 lets it read every message in the teams and chats where it is installed. What does the bot use those messages for? If nothing, should the two read permissions be dropped? | REQ-028, REQ-029 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-021 | 3 | User experience | In which scope (Personal or Team) and to which recipients is each alert result posted? (Trigger and content answered by Q-016; Group Chat excluded by Q-017.) | REQ-029 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-004 | 4 | Technical detail | Which message patterns indicate 5XX failure or noise beyond the examples, which outcome takes precedence when both kinds of cue are present, and what qualifies as intermittent and auto-recovered for P4? | REQ-001, REQ-002, REQ-003, REQ-022 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-005 | 4 | Technical detail | What threshold and measurement are meant by “below threshold” for 5XX alerts? | REQ-021 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-006 | 4 | Technical detail | What interval and measurement source define a latency datapoint, and what duration and recovery evidence qualify as short-lived or self-recovered latency? | REQ-004, REQ-006 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-007 | 4 | Technical detail | What measurement window and boundary rules define CPU above 80%, memory above 75%, and healthy infrastructure? | REQ-005 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-008 | 4 | Technical detail | How should the disk policy classify usage above 84% but below 85%, how do the P4/P5 conditions interact with threshold-based P2/P3 priorities, and does a decommissioning flag suppress only new alerts or also clear existing alerts? | REQ-010, REQ-011 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-009 | 4 | Technical detail | What number of services and nodes constitutes “multiple,” and what evidence confirms a network error? | REQ-012 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-010 | 4 | Technical detail | What defines cluster-wide impact, temporary DNS failure, a false alarm, and single-retry success for network priority assignment? | REQ-013 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-011 | 4 | Technical detail | Are business-logic keywords exact matches, what defines order-processing degradation or an unused feature workflow, and what priority applies to “redis failure”? | REQ-014, REQ-015 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-012 | 4 | Technical detail | What minimum data is required, what evidence sources may be used, and what should happen when evidence is inconclusive? | REQ-018, REQ-019 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-014 | 4 | Technical detail | How should the system choose a category when an alert matches indicators from multiple decision-tree categories? | REQ-016 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-015 | 4 | Technical detail | For HTTP 5XX alerts, should the category be Server issue or Application backend failure? For latency spikes, how do Application performance and Infra bottleneck map to the cause classifications in REQ-005? | REQ-005, REQ-016 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-022 | 4 | Technical detail | What public domain hosts `/api/messages` in each environment? | REQ-023 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | deferred |
| Q-027 | 4 | Technical detail | Over the latency-spike window, is CPU and memory usage compared using the average or the peak value? (Remainder of Q-007.) | REQ-005 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-028 | 4 | Technical detail | Every disk alert is above 84%, so P3 or P2 always applies; under highest-severity-wins (Q-008, REQ-017) the disk P4 (cold-storage / non-production) and P5 (duplicate / acknowledged) rules can never be selected. Should P4/P5 override the thresholds for disk alerts, or be removed? | REQ-011, REQ-017 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-029 | 4 | Technical detail | A network error on exactly 2 services and fewer than 50% of a cluster's nodes is confirmed (Q-009) but is neither cluster-wide (Q-010) nor one affected service. Which priority applies? | REQ-013 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | answered |
| Q-030 | 4 | Technical detail | What measured reduction in order-processing throughput, relative to what baseline and over what window, qualifies as degradation for P2? | REQ-015 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-031 | 4 | Technical detail | If multiple specific alert rules of equal severity assign different categories, which category wins? | REQ-016 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-032 | 4 | Technical detail | If multiple generic decision-tree indicators match and no specific alert rule applies, which category wins? | REQ-016 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |

## Assumed, pending confirmation
None. No working assumptions were needed for this round.

## Inferred (no direct source)
None. Requirements above are grounded in the captured pages; unresolved interpretations are marked for clarification.

## Clarification log
| Date | QID | Answer (summary) | Answered by | Requirements updated |
|---|---|---|---|---|
| 2026-10-09 | Q-001 | Deferred. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-002 | Deferred. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-003 | Confirmed security-specific handling is desired; the handling details were deferred. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-004 | Deferred. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-005 | Deferred. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-016 | The Teams bot posts alert results (validity, category, priority) to Teams one-way; it does not accept replies or commands. | Raamesh-Bhardwaj-UST | REQ-029 |
| 2026-10-09 | Q-017 | Group Chat scope is not required. Install audience and approver not given; re-queued as Q-024. | Raamesh-Bhardwaj-UST | REQ-027 |
| 2026-10-09 | Q-018 | Single-tenant app registration. | Raamesh-Bhardwaj-UST | REQ-030 |
| 2026-10-09 | Q-019 | Client secret is stored in Azure Key Vault. Reader access, expiry period and rotation not given; re-queued as Q-025. | Raamesh-Bhardwaj-UST | REQ-024 |
| 2026-10-09 | Q-020 | The bot may read all messages in teams and chats where it is installed and stores no message content. | Raamesh-Bhardwaj-UST | REQ-028 |
| 2026-10-09 | Q-024 | All users in the tenant may install the app; a Teams admin approves the Teams Admin Center submission. | Raamesh-Bhardwaj-UST | REQ-032 |
| 2026-10-09 | Q-023 | The backend rejects requests to `/api/messages` not authenticated as coming from Azure Bot Service. | Raamesh-Bhardwaj-UST | REQ-023 |
| 2026-10-09 | Q-025 | Only the backend's managed identity may read the client secret; 6-month expiry; rotated 30 days before expiry. | Raamesh-Bhardwaj-UST | REQ-024, REQ-031 |
| 2026-10-09 | Q-026 | The bot does not use message content; both read permissions are dropped. Overrides source 5.4 and supersedes Q-020. | Raamesh-Bhardwaj-UST | REQ-028 |
| 2026-10-09 | Q-021 | Alert results are posted in Team scope to a designated alerts channel. | Raamesh-Bhardwaj-UST | REQ-029 |
| 2026-10-09 | Q-006 | Datapoint = 1-minute p95 API latency; P4 short-lived = back to ≤2 s within 5 minutes without intervention. | Raamesh-Bhardwaj-UST | REQ-004, REQ-006 |
| 2026-10-09 | Q-007 | CPU/memory measured over the latency-spike window; strictly >80% / >75%; healthy = CPU ≤80% and memory ≤75%. Average vs peak not given; re-queued as Q-027. | Raamesh-Bhardwaj-UST | REQ-005 |
| 2026-10-09 | Q-008 | Disk evaluated every 5 minutes; P3 = >84% to ≤90%, P2 = >90%; highest severity wins; decommission flag suppresses new alerts and closes existing ones. Raised Q-028 (disk P4/P5 unreachable). | Raamesh-Bhardwaj-UST | REQ-010, REQ-011 |
| 2026-10-09 | Q-009 | Network error confirmed if errors on ≥2 services or ≥2 nodes in the same 5-minute window; otherwise one affected service. | Raamesh-Bhardwaj-UST | REQ-012 |
| 2026-10-09 | Q-010 | Cluster-wide = ≥50% of a cluster's nodes or ≥3 services; temporary DNS = resolves on retry within 1 minute; false alarm = probe errors with no matching user-traffic errors; single-retry = first retry succeeds. Raised Q-029 (2-service gap). | Raamesh-Bhardwaj-UST | REQ-013 |
| 2026-10-09 | Q-011 | The four listed business-logic phrases are exact matches; Redis failure is P2; degradation means reduced throughput without total failure; unused workflow means disabled feature path. Measurable throughput threshold deferred to Q-030. | Raamesh-Bhardwaj-UST | REQ-014, REQ-015 |
| 2026-10-09 | Q-012 | Required alert fields are service, timestamp and error signal; priority evidence is limited to alert payload and service metrics; inconclusive evidence yields Unknown/P5. | Raamesh-Bhardwaj-UST | REQ-018, REQ-019 |
| 2026-10-09 | Q-014 | Specific alert rules take precedence over generic decision-tree indicators; among multiple specific rules, highest severity determines category. Equal-severity and generic-only overlaps deferred to Q-031/Q-032. | Raamesh-Bhardwaj-UST | REQ-016 |
| 2026-10-09 | Q-015 | HTTP 5XX category is Server issue; latency category follows cause: Infra bottleneck for infrastructure, Application performance otherwise. | Raamesh-Bhardwaj-UST | REQ-005, REQ-016 |
| 2026-10-09 | Q-022 | Different domains per environment; the environment-to-domain mapping was deferred. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-030 | Deferred; no measurable order-processing throughput threshold supplied. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-031 | Deferred; no equal-severity category tie-break supplied. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-032 | Deferred; no precedence for multiple generic indicators supplied. | Raamesh-Bhardwaj-UST | — |
| 2026-10-09 | Q-027 | CPU and memory usage are compared using the average over the latency-spike window. | Raamesh-Bhardwaj-UST | REQ-005 |
| 2026-10-09 | Q-028 | Disk P4/P5 categorical conditions override percentage thresholds; highest severity resolves multiple categorical matches. | Raamesh-Bhardwaj-UST | REQ-011 |
| 2026-10-09 | Q-029 | Exactly 2 affected services below the cluster-wide threshold receive P2. | Raamesh-Bhardwaj-UST | REQ-013 |