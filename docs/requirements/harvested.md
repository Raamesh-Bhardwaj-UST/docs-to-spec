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
- **Statement:** When API latency exceeds 2 seconds for 3 consecutive datapoints, the system shall identify a latency spike. [NEEDS CLARIFICATION: What interval and measurement source define a datapoint?]
- **Success criterion:** A latency spike is identified when latency exceeds 2 seconds for 3 consecutive datapoints; [NEEDS CLARIFICATION: what interval and measurement source define a datapoint?]
- **Acceptance criteria:**
	- AC-004.1 Given API latency greater than 2 seconds for 3 consecutive datapoints, when the system evaluates latency, then it identifies a latency spike. [NEEDS CLARIFICATION: what interval and measurement source define each datapoint?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 2. Latency Spikes (API Latency > 2s)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The trigger is latency greater than 2 seconds for 3 consecutive datapoints.

### REQ-005 Categorize latency causes
- **Statement:** When a latency spike occurs and CPU usage exceeds 80% or memory usage exceeds 75%, the system shall classify it as an infrastructure issue; when infrastructure is healthy, the system shall classify it as an application bottleneck. [NEEDS CLARIFICATION: What measurement window and boundary rules define CPU, memory, and healthy infrastructure?]
- **Success criterion:** The spike is classified as infrastructure when CPU exceeds 80% or memory exceeds 75%, and as an application bottleneck when infrastructure is healthy; [NEEDS CLARIFICATION: what measurement window and boundary rules define these states?]
- **Acceptance criteria:**
	- AC-005.1 Given a latency spike and CPU usage greater than 80% or memory usage greater than 75%, when the system classifies the cause, then it identifies an infrastructure issue. [NEEDS CLARIFICATION: what measurement window and boundary rules apply?]
	- AC-005.2 Given a latency spike and healthy infrastructure, when the system classifies the cause, then it identifies an application bottleneck. [NEEDS CLARIFICATION: what defines healthy infrastructure?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 2. Latency Spikes (API Latency > 2s)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** CPU above 80% or memory above 75% indicates infrastructure; healthy infrastructure indicates an application bottleneck.

### REQ-006 Assign latency priorities
- **Statement:** When the system assigns priority to a latency alert, it shall use the source's stated mapping: P1 for latency combined with 5XX, P2 for infrastructure saturation leading to latency, P3 for debug/analytics endpoints, P4 for short-lived self-recovered latency, and P5 for non-user-facing staging traffic. [NEEDS CLARIFICATION: What qualifies as short-lived or self-recovered?]
- **Success criterion:** The assigned priority matches the stated P1–P5 condition; [NEEDS CLARIFICATION: what duration and evidence qualify as short-lived and self-recovered?]
- **Acceptance criteria:**
	- AC-006.1 Given latency combined with 5XX, when priority is assigned, then the priority is P1.
	- AC-006.2 Given infrastructure saturation leading to latency, when priority is assigned, then the priority is P2.
	- AC-006.3 Given a latency alert on a debug or analytics endpoint, when priority is assigned, then the priority is P3.
	- AC-006.4 Given short-lived latency that self-recovered, when priority is assigned, then the priority is P4. [NEEDS CLARIFICATION: what duration and recovery evidence qualify?]
	- AC-006.5 Given non-user-facing staging traffic with a latency alert, when priority is assigned, then the priority is P5.
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 2. Latency Spikes (API Latency > 2s)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P1–P5 conditions for latency alerts.

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
- **Statement:** When disk usage exceeds 84%, the system shall raise a disk usage alert, except when the node is flagged for decommissioning. [NEEDS CLARIFICATION: At what measurement interval is usage evaluated, and how does the decommissioning exception affect an existing alert?]
- **Success criterion:** Disk usage above 84% raises an alert unless the node is flagged for decommissioning; [NEEDS CLARIFICATION: what measurement interval applies, and does the flag clear existing alerts?]
- **Acceptance criteria:**
	- AC-010.1 Given disk usage above 84% on a node not flagged for decommissioning, when the system evaluates usage, then it raises a disk usage alert. [NEEDS CLARIFICATION: what measurement interval applies?]
	- AC-010.2 Given disk usage above 84% on a node flagged for decommissioning, when the system evaluates usage, then it ignores the alert. [NEEDS CLARIFICATION: does this suppress only new alerts or clear existing alerts?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 4. Disk Usage Alerts](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The trigger is usage above 84%; alerts are ignored if the node is flagged for decommissioning.

### REQ-011 Assign disk usage priorities
- **Statement:** When the system assigns priority to a disk usage alert, it shall use the source's stated mapping: P2 above 90%, P3 from 85% to 90%, P4 for cold-storage volumes or non-production, and P5 for duplicate alerts or alerts already ticketed or acknowledged. [NEEDS CLARIFICATION: Which priority applies between the alert trigger above 84% and the P3 range beginning at 85%?]
- **Success criterion:** The assigned priority matches the stated disk-usage priority conditions; [NEEDS CLARIFICATION: what priority applies above 84% but below 85%, and how do the categorical conditions interact?]
- **Acceptance criteria:**
	- AC-011.1 Given disk usage above 90%, when priority is assigned, then the priority is P2.
	- AC-011.2 Given disk usage from 85% to 90%, when priority is assigned, then the priority is P3. [NEEDS CLARIFICATION: are the endpoints inclusive?]
	- AC-011.3 Given a disk alert for a cold-storage volume or a non-production environment, when priority is assigned, then the priority is P4.
	- AC-011.4 Given a duplicate disk alert or an alert already ticketed or acknowledged, when priority is assigned, then the priority is P5.
	- AC-011.5 Given disk usage above 84% but below 85%, when priority is assigned, then [NEEDS CLARIFICATION: what priority applies?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 4. Disk Usage Alerts](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P2–P5 conditions, while its alert trigger begins above 84%.

### REQ-012 Validate network errors
- **Statement:** When validating a network error, the system shall check multiple services and nodes. [NEEDS CLARIFICATION: How many services and nodes constitute multiple, and what evidence is required to confirm a network error?]
- **Success criterion:** The system checks the source-required number of services and nodes; [NEEDS CLARIFICATION: what count and evidence confirm a network error?]
- **Acceptance criteria:**
	- AC-012.1 Given a timeout or connection-refused error, when the system validates it, then it checks [NEEDS CLARIFICATION: how many] services and [NEEDS CLARIFICATION: how many] nodes and uses [NEEDS CLARIFICATION: what evidence] to confirm the error.
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 5. Network Errors (Timeout, Connection Refused)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source categorizes timeout and connection-refused errors as network/connectivity and directs checking multiple services and nodes.

### REQ-013 Assign network error priorities
- **Statement:** When the system assigns priority to a network error, it shall use the source's stated mapping: P1 for cluster-wide, multi-service impact; P2 for one affected production service; P3 for staging-only disruption; P4 for a single-retry success or temporary DNS failure; and P5 for synthetic-probe timeouts or false alarms. [NEEDS CLARIFICATION: What defines cluster-wide impact, temporary DNS failure, and a false alarm?]
- **Success criterion:** The assigned priority matches the stated P1–P5 condition; [NEEDS CLARIFICATION: what defines cluster-wide impact, temporary DNS failure, and a false alarm?]
- **Acceptance criteria:**
	- AC-013.1 Given cluster-wide, multi-service network impact, when priority is assigned, then the priority is P1. [NEEDS CLARIFICATION: what defines cluster-wide impact?]
	- AC-013.2 Given one affected production service, when priority is assigned, then the priority is P2.
	- AC-013.3 Given a staging-only network disruption, when priority is assigned, then the priority is P3.
	- AC-013.4 Given a network error that succeeds on a single retry or is a temporary DNS failure, when priority is assigned, then the priority is P4. [NEEDS CLARIFICATION: what defines a temporary DNS failure?]
	- AC-013.5 Given a synthetic-probe timeout or false alarm, when priority is assigned, then the priority is P5. [NEEDS CLARIFICATION: what qualifies as a false alarm?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 5. Network Errors (Timeout, Connection Refused)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P1–P5 conditions for network errors.

### REQ-014 Categorize business logic failures
- **Statement:** When logs contain a business-logic failure indicator, the system shall categorize the alert as Application / Business domain. [NEEDS CLARIFICATION: Are the listed keywords exact matches, and are there additional indicators?]
- **Success criterion:** An alert containing a listed business-logic indicator is categorized as Application / Business domain; [NEEDS CLARIFICATION: are these exact matches, and are there additional indicators?]
- **Acceptance criteria:**
	- AC-014.1 Given logs containing “payment failed,” “order creation failed,” “inventory mismatch,” or “redis failure,” when the system categorizes the alert, then it assigns Application / Business domain. [NEEDS CLARIFICATION: are these exact-match phrases or examples of broader indicators?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 6. Business Logic Failures (Logs)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** Listed indicators are “payment failed,” “order creation failed,” “inventory mismatch,” and “redis failure.”

### REQ-015 Assign business logic priorities
- **Statement:** When the system assigns priority to a business-logic alert, it shall use the source's stated mapping: P1 for Payment and Checkout failures, P2 for order-processing degradation, P3 for inventory mismatches, P4 for incorrect analytics/metadata, and P5 for unused feature-workflow errors. [NEEDS CLARIFICATION: What priority applies to the listed “redis failure” indicator, and what distinguishes order-processing degradation from failure?]
- **Success criterion:** The assigned priority matches the stated P1–P5 condition; [NEEDS CLARIFICATION: what priority applies to “redis failure,” and what distinguishes order-processing degradation from failure?]
- **Acceptance criteria:**
	- AC-015.1 Given a Payment or Checkout failure, when priority is assigned, then the priority is P1.
	- AC-015.2 Given order-processing degradation, when priority is assigned, then the priority is P2. [NEEDS CLARIFICATION: what distinguishes degradation from failure?]
	- AC-015.3 Given an inventory mismatch, when priority is assigned, then the priority is P3.
	- AC-015.4 Given incorrect analytics or metadata, when priority is assigned, then the priority is P4.
	- AC-015.5 Given an unused feature-workflow error, when priority is assigned, then the priority is P5.
	- AC-015.6 Given a “redis failure” indicator, when priority is assigned, then [NEEDS CLARIFICATION: what priority applies?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § 6. Business Logic Failures (Logs)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The page lists P1–P5 conditions for business-logic failures.

### REQ-016 Categorize alerts by indicator
- **Statement:** When an alert matches a source-listed indicator, the system shall assign its stated category: HTTP 5XX or backend stack trace to Server issue; pod restarts or node pressure to Infrastructure; high latency alone to Application; DNS, routing, or connection refused to Network; fraud alerts or unauthorized access to Security; browser/client request failures to Client issue; missing context or unclear logs to Unknown; latency spikes to Application performance or Infra bottleneck; disk usage alerts to Infrastructure; and network errors to Network / Connectivity. [NEEDS CLARIFICATION: The 5XX section also names Application backend failure; which category label applies to HTTP 5XX alerts? Which category label applies to latency spikes? How should the system choose a category when indicators from multiple categories are present?]
- **Success criterion:** Each source-listed indicator is assigned its stated category; [NEEDS CLARIFICATION: which category label applies to HTTP 5XX alerts and latency spikes, and how should the system choose when indicators from multiple categories are present?]
- **Acceptance criteria:**
	- AC-016.1 Given an HTTP 5XX alert, when the system categorizes it, then it assigns [NEEDS CLARIFICATION: Server issue or Application backend failure?].
	- AC-016.2 Given pod restarts or node pressure, when the system categorizes the alert, then it assigns Infrastructure.
	- AC-016.3 Given high latency only, when the system categorizes the alert, then it assigns Application.
	- AC-016.4 Given DNS, routing, or connection-refused indicators, when the system categorizes the alert, then it assigns Network.
	- AC-016.5 Given a fraud alert or unauthorized access, when the system categorizes the alert, then it assigns Security.
	- AC-016.6 Given a browser/client request failure, when the system categorizes the alert, then it assigns Client issue.
	- AC-016.7 Given missing context or unclear logs, when the system categorizes the alert, then it assigns Unknown.
	- AC-016.8 Given indicators from multiple categories, when the system categorizes the alert, then [NEEDS CLARIFICATION: which category takes precedence?]
	- AC-016.9 Given a latency spike, when the system categorizes it, then it assigns [NEEDS CLARIFICATION: Application performance or Infra bottleneck, and how does this correspond to the cause classification?]
	- AC-016.10 Given a disk usage alert, when the system categorizes it, then it assigns Infrastructure.
	- AC-016.11 Given a network error, when the system categorizes it, then it assigns Network / Connectivity.
	- AC-016.12 Given a backend stack trace, when the system categorizes the alert, then it assigns Server issue.
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § Categorization Decision Tree](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 1. 5XX Errors (API / Backend)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 2. Latency Spikes (API Latency > 2s)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 3. Pod Restart Loop (Kubernetes)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 4. Disk Usage Alerts](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca), [astra-alert-rules/page-1398800396 § 5. Network Errors (Timeout, Connection Refused)](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The decision table and alert-specific sections map HTTP 5XX, latency, pod restart, disk usage, and network indicators to categories; the 5XX and latency sections state alternative category labels.

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
- **Statement:** When alert data is insufficient, the system shall assign category Unknown and priority P5. [NEEDS CLARIFICATION: What minimum data is required before an alert is considered insufficient?]
- **Success criterion:** An alert deemed to have insufficient data receives category Unknown and priority P5; [NEEDS CLARIFICATION: what minimum data qualifies as insufficient?]
- **Acceptance criteria:**
	- AC-018.1 Given alert data that meets the source's definition of insufficient, when the system classifies the alert, then it assigns Unknown and P5. [NEEDS CLARIFICATION: what minimum data qualifies as insufficient?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § Global Rules](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source assigns Unknown and P5 when data is insufficient.

### REQ-019 Base priority on evidence
- **Statement:** When assigning an alert priority, the system shall use evidence and shall not use a guess. [NEEDS CLARIFICATION: What evidence sources are allowed, and what should the system do when available evidence is inconclusive?]
- **Success criterion:** [NEEDS CLARIFICATION: what evidence sources are allowed, and what observable result demonstrates that priority is evidence-based rather than guessed?]
- **Acceptance criteria:**
	- AC-019.1 Given evidence sufficient under the source's rules, when the system assigns priority, then it bases the priority on that evidence and not a guess. [NEEDS CLARIFICATION: which evidence sources are allowed?]
	- AC-019.2 Given inconclusive evidence, when the system assigns priority, then [NEEDS CLARIFICATION: what should the system do?]
- **Type:** functional
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1398800396 § Global Rules](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) — `.specify/harvest/raw/astra-alert-rules/page-1398800396.md`
- **Evidence:** The source says priority must never be based on a guess, only evidence.

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
- **Statement:** The Azure Bot resource's Messaging Endpoint shall be the backend application's public HTTPS URL `https://<public-domain>/api/messages`. [NEEDS CLARIFICATION: what public domain hosts the endpoint in each environment?] [NEEDS CLARIFICATION: must the backend reject requests to `/api/messages` that are not authenticated as coming from Azure Bot Service?]
- **Success criterion:** The Messaging Endpoint equals `https://<public-domain>/api/messages` and the backend application receives HTTPS requests at that URL from the public internet (yes/no); [NEEDS CLARIFICATION: what public domain applies?]
- **Acceptance criteria:**
	- AC-023.1 Given the Azure Bot resource, when its Configuration is inspected, then the Messaging Endpoint is `https://[NEEDS CLARIFICATION: public domain]/api/messages`.
	- AC-023.2 Given the backend application is deployed, when an HTTPS request is sent from the public internet to `https://[NEEDS CLARIFICATION: public domain]/api/messages`, then the backend application receives the request.
- **Type:** functional (integration)
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1514635295 § Prerequisites](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § Step 3: Configure Messaging Endpoint](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** A public HTTPS endpoint is a prerequisite; Step 3 sets the messaging endpoint to `https://<your-public-domain>/api/messages`.

### REQ-024 Configure bot credentials in the backend
- **Statement:** The backend application shall be configured with `MicrosoftAppId` set to the Application (Client) ID, `MicrosoftAppPassword` set to the client secret read from Azure Key Vault, and `MicrosoftAppTenantId` set to the Directory (Tenant) ID. [NEEDS CLARIFICATION: who may read the client secret in Azure Key Vault?]
- **Success criterion:** All 3 settings hold the values from the Azure App Registration, and the client secret is read from Azure Key Vault (yes/no).
- **Acceptance criteria:**
	- AC-024.1 Given the app registration's client ID, client secret and tenant ID, when the backend configuration is inspected, then `MicrosoftAppId`, `MicrosoftAppPassword` and `MicrosoftAppTenantId` hold those values.
	- AC-024.2 Given the deployed backend application, when the source of `MicrosoftAppPassword` is inspected, then the value is read from Azure Key Vault.
- **Type:** functional (configuration)
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1514635295 § Step 1.1: Create Client Secret](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § Step 7: Application Configuration](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Steps 1.1 and 7 map the client ID, client secret and tenant ID to these three setting names. Q-019: the client secret is stored in Azure Key Vault.

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

### REQ-028 Request Teams message-read permissions
- **Statement:** The Teams app shall request the `ChannelMessage.Read.Group` and `ChatMessage.Read.Chat` permissions to read messages in the teams and chats where it is installed, without storing message content.
- **Success criterion:** The app manifest declares both permissions, and no content of read messages is stored (yes/no).
- **Acceptance criteria:**
	- AC-028.1 Given the downloaded app manifest, when its permissions are inspected, then `ChannelMessage.Read.Group` and `ChatMessage.Read.Chat` are declared.
	- AC-028.2 Given the bot has read a channel or chat message in a team or chat where it is installed, when the system's data stores are inspected, then no content of that message is stored.
- **Type:** non-functional (security / permissions)
- **Status:** confirmed
- **Sources:** [astra-alert-rules/page-1514635295 § 5.4 Configure Bot](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** 5.4 lists these two permissions. Q-020: the bot may read all messages in the teams and chats where it is installed and stores no message content.

### REQ-029 Enable bot notifications
- **Statement:** When the system produces an alert result (validity, category and priority), the Teams bot shall send it to Teams as a one-way notification. [NEEDS CLARIFICATION: in which scope (Personal or Team) and to which recipients?]
- **Success criterion:** Send notifications is enabled, and each alert result appears in Teams as a bot notification (yes/no); [NEEDS CLARIFICATION: in which scope and for which recipients?]
- **Acceptance criteria:**
	- AC-029.1 Given the Teams app's bot configuration, when it is inspected, then Send notifications is enabled.
	- AC-029.2 Given an alert the system has validated, categorised and prioritised, when the result is produced, then the bot sends a Teams notification containing the alert's validity, category and priority to [NEEDS CLARIFICATION: which scope and recipients?].
	- AC-029.3 Given a user replies to or sends a command to the bot in Teams, when the bot receives it, then the bot does not act on it as a reply or command.
- **Type:** functional (notification)
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1514635295 § 5.4 Configure Bot](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** 5.4 says to enable Send notifications; no trigger or content is described. Q-016: the bot posts alert results to Teams one-way and does not accept replies or commands.

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
- **Statement:** The Azure App Registration's client secret shall have an expiry. [NEEDS CLARIFICATION: what expiry period applies, and what must happen before the secret expires?]
- **Success criterion:** The client secret has an expiry date set (yes/no).
- **Acceptance criteria:**
	- AC-031.1 Given the client secret under Certificates & Secrets, when it is inspected, then an expiry date is set.
	- AC-031.2 Given the client secret is [NEEDS CLARIFICATION: how long?] from expiry, when that point is reached, then [NEEDS CLARIFICATION: what rotation action occurs, and who performs it?].
	- AC-031.3 Given the client secret under Certificates & Secrets, when its expiry is inspected, then the expiry period is [NEEDS CLARIFICATION: what period?].
- **Type:** non-functional (security)
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1514635295 § Step 1.1: Create Client Secret](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Step 1.1 says to add a description and expiry; no period is given.

### REQ-032 Publish the Teams app through Teams Admin Center
- **Statement:** The Teams app package shall be submitted through Teams Admin Center. [NEEDS CLARIFICATION: which users or teams must be able to install the app, and who approves the submission?]
- **Success criterion:** The bot can be installed inside Microsoft Teams after submission (yes/no).
- **Acceptance criteria:**
	- AC-032.1 Given the app package downloaded from Developer Portal containing `manifest.json`, `color.png` and `outline.png`, when it is submitted through Teams Admin Center and [NEEDS CLARIFICATION: approved by whom?], then the bot can be installed inside Microsoft Teams.
- **Type:** functional (deployment)
- **Status:** needs-human
- **Sources:** [astra-alert-rules/page-1514635295 § Step 5: Create Teams App Manifest](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § 5.5 Generate and Download manifest.json](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams), [astra-alert-rules/page-1514635295 § Step 6: Upload/Submit the App to Teams](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) — `.specify/harvest/raw/astra-alert-rules/page-1514635295.md`
- **Evidence:** Step 5 is required to install the bot in Teams; 5.5 downloads the package; Step 6 submits it via Teams Admin Center.

## Conflicts
| Conflict | Requirements | Sources | Question ID |
|---|---|---|---|
| No direct contradictions found in the snapshot. Some priority boundaries and overlapping conditions are underspecified; see open questions. | — | — | — |

## Open questions (ranked)
| QID | Rank | Impact | Question | Affects | Source | State |
|---|---:|---|---|---|---|---|
| Q-001 | 1 | Scope | Which alerting system and alert population does this rule set govern? | REQ-001–REQ-022 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-002 | 1 | Scope | Which service names belong to the business-critical, production-business, and non-critical production groups, and how should “higher” priority be represented? | REQ-003, REQ-009, REQ-020 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-016 | 1 | Scope | Is the Teams bot the channel that delivers the alert validation, category and priority results of REQ-001–REQ-022? What messages does it send or receive? | REQ-023–REQ-032 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-017 | 1 | Scope | Which users or teams must be able to install the app, who approves the Teams Admin Center submission, and is the Group Chat scope required? | REQ-027, REQ-032 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-024 | 1 | Scope | Which users or teams must be able to install the app, and who approves the Teams Admin Center submission? (Remainder of Q-017.) | REQ-032 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | open |
| Q-003 | 2 | Security / privacy | The decision tree includes Security for fraud and unauthorized access, but gives no validation or priority rule. Should those alerts follow additional security-specific handling? Specify the handling. | REQ-016 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-018 | 2 | Security / privacy | Should the app registration be single-tenant or multi-tenant? | REQ-030 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-019 | 2 | Security / privacy | Where must the client secret be stored, who may read it, what expiry period applies, and how and when is it rotated? | REQ-024, REQ-031 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-020 | 2 | Security / privacy | `ChannelMessage.Read.Group` and `ChatMessage.Read.Chat` let the bot read messages in the teams and chats where it is installed. What message content may it read, and may it store that content (if so, for how long)? | REQ-028 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | answered |
| Q-023 | 2 | Security / privacy | Must the backend reject requests to `/api/messages` that are not authenticated as coming from Azure Bot Service? The page makes the endpoint public but states no request validation. | REQ-023 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | open |
| Q-025 | 2 | Security / privacy | Who may read the client secret in Azure Key Vault, what expiry period applies, and how and when is it rotated? (Remainder of Q-019.) | REQ-024, REQ-031 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | open |
| Q-026 | 2 | Security / privacy | Q-016 makes the bot one-way, yet Q-020 lets it read every message in the teams and chats where it is installed. What does the bot use those messages for? If nothing, should the two read permissions be dropped? | REQ-028, REQ-029 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | open |
| Q-021 | 3 | User experience | In which scope (Personal or Team) and to which recipients is each alert result posted? (Trigger and content answered by Q-016; Group Chat excluded by Q-017.) | REQ-029 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | open |
| Q-004 | 4 | Technical detail | Which message patterns indicate 5XX failure or noise beyond the examples, which outcome takes precedence when both kinds of cue are present, and what qualifies as intermittent and auto-recovered for P4? | REQ-001, REQ-002, REQ-003, REQ-022 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-005 | 4 | Technical detail | What threshold and measurement are meant by “below threshold” for 5XX alerts? | REQ-021 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | deferred |
| Q-006 | 4 | Technical detail | What interval and measurement source define a latency datapoint, and what duration and recovery evidence qualify as short-lived or self-recovered latency? | REQ-004, REQ-006 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-007 | 4 | Technical detail | What measurement window and boundary rules define CPU above 80%, memory above 75%, and healthy infrastructure? | REQ-005 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-008 | 4 | Technical detail | How should the disk policy classify usage above 84% but below 85%, how do the P4/P5 conditions interact with threshold-based P2/P3 priorities, and does a decommissioning flag suppress only new alerts or also clear existing alerts? | REQ-010, REQ-011 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-009 | 4 | Technical detail | What number of services and nodes constitutes “multiple,” and what evidence confirms a network error? | REQ-012 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-010 | 4 | Technical detail | What defines cluster-wide impact, temporary DNS failure, a false alarm, and single-retry success for network priority assignment? | REQ-013 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-011 | 4 | Technical detail | Are business-logic keywords exact matches, what defines order-processing degradation or an unused feature workflow, and what priority applies to “redis failure”? | REQ-014, REQ-015 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-012 | 4 | Technical detail | What minimum data is required, what evidence sources may be used, and what should happen when evidence is inconclusive? | REQ-018, REQ-019 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-014 | 4 | Technical detail | How should the system choose a category when an alert matches indicators from multiple decision-tree categories? | REQ-016 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-015 | 4 | Technical detail | For HTTP 5XX alerts, should the category be Server issue or Application backend failure? For latency spikes, how do Application performance and Infra bottleneck map to the cause classifications in REQ-005? | REQ-005, REQ-016 | [astra-alert-rules/page-1398800396](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1398800396/To+test+confluence+page+id+alert+rules+in+experian+rca) | open |
| Q-022 | 4 | Technical detail | What public domain hosts `/api/messages` in each environment? | REQ-023 | [astra-alert-rules/page-1514635295](https://ust-pace.atlassian.net/wiki/spaces/Astra/pages/1514635295/Azure+Bot+integration+with+MS+Teams) | open |

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