# Feature Specification: Studio Guardian — Autonomous Live Media Incident Director

**Feature Branch**: `001-media-incident-director`

**Created**: 2026-09-06

**Status**: Draft

**Input**: User description: "Specify the complete product requirements for Studio Guardian: Autonomous Live Media Incident Director"

## Clarifications

### Session 2026-09-06

- **Q: Which Google Cloud agent framework implementation should Studio Guardian use for defining and executing the specialist agents? (FR-005)** → **A:** Option C (Hybrid: Google Cloud Agent Development Kit / GenAI SDK in Python for in-repo code-defined specialist agent execution, combined with Vertex AI Search / Agent Builder for historical incident memory retrieval).
- **Q: How does the Observability Investigator interface with Grafana at runtime? (FR-009)** → **A:** The backend integrates a runtime Grafana Model Context Protocol (MCP) client using JSON-RPC/SSE protocol, exposing discrete tools (`query_prometheus_metrics`, `search_loki_logs`, `get_tempo_traces`, `list_grafana_alerts`) invoked during live investigation.
- **Q: What constitutes a genuine controlled remediation in the demo environment? (FR-019)** → **A:** The Remediation Agent dispatches actual HTTP/configuration requests against a live video routing proxy (e.g. shifting regional traffic weights from degraded transcoders to healthy standby clusters), which immediately alters service behavior and post-action telemetry.
- **Q: How is demo reproducibility guaranteed for hackathon evaluation? (SC-008)** → **A:** A deterministic Scenario Simulator controller on the UI allows evaluators to inject the "India vs Australia Final" degradation pattern with one click, guaranteeing complete autonomous closed-loop resolution in under 3 minutes.
- **Q: What is the boundary between real infrastructure and simulated environment? (Assumptions)** → **A:** Google Cloud + Gemini reasoning, Grafana MCP tool calls, multi-agent supervisory state machine, deterministic Safety Director, PostgreSQL persistence, and React/Three.js dashboard are 100% real. Millions of viewers and physical hardware transcoders are simulated via high-fidelity synthetic telemetry feeds.
- **Q: How are live metrics and agent states communicated to the Command Center UI? (FR-027)** → **A:** Server-Sent Events (SSE) / WebSocket stream from the FastAPI backend delivers 1 Hz telemetry metrics and immediate agent transition events to the browser.
- **Q: What is the precise scope of the 3D UX visualization? (FR-029)** → **A:** A lightweight React Three Fiber spatial globe displaying global broadcast distribution nodes (Australia, Singapore, US, EU) that glow amber/red under degradation and transition to green upon verified recovery, purposefully reinforcing operational hierarchy without visual clutter.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Live Streaming Incident Detection & Alerting (Priority: P1)

As a live media operations engineer, I want the system to continuously observe the live streaming event and detect degradation immediately, so that the operations team and autonomous systems know without delay that viewer experience is compromised.

**Why this priority**: Incident detection is the mandatory entry point to the entire autonomous lifecycle. Without reliable, immediate detection, no downstream investigation or remediation can occur.

**Independent Test**: Can be fully tested by triggering synthetic telemetry degradation (elevating playback error rate from 0.4% to 8.7%) and verifying that the live event transitions from `HEALTHY` to `INCIDENT`, generates an incident identifier, and highlights affected regions.

**Acceptance Scenarios**:

1. **Given** a live streaming event with 12.4M concurrent viewers and healthy baseline telemetry (playback error rate 0.4%), **When** playback error rates spike past the operational threshold to ~8.7% and GPU allocation failures occur, **Then** the system status transitions from `HEALTHY` to `INCIDENT`, assigns a unique incident ID, and highlights affected services and regions (Australia, Singapore).
2. **Given** an ongoing live streaming event, **When** telemetry remains within expected operational bounds, **Then** the event remains in `HEALTHY` status and no false-positive incident is triggered.

---

### User Story 2 - Hierarchical Multi-Agent Investigation Execution (Priority: P1)

As an operations engineer, I want to watch a coordinated team of specialist agents execute an orderly investigation under an Incident Commander, so that I can observe each agent's explicit role, status, and findings in real time.

**Why this priority**: Transparent agent collaboration is essential for operator trust in an autonomous system. Distinct specialist agents prevent monolithic black-box decisions.

**Independent Test**: Can be tested by triggering an incident and validating that the Incident Commander supervisor invokes the Observability Investigator and Business Impact Agent in order, records their execution state, and updates the shared workflow timeline.

**Acceptance Scenarios**:

1. **Given** an active incident, **When** the autonomous workflow triggers, **Then** the Incident Commander activates first, delegates telemetry investigation to the Observability Investigator, delegates impact quantification to the Business Impact Agent, and updates agent states in real time.
2. **Given** active specialist agents running their tasks, **When** each specialist completes or fails, **Then** its run duration, tool calls, and structured outputs are persisted to durable storage and surfaced on the operational timeline.

---

### User Story 3 - Evidence-Based Root Cause Hypothesis & Correlation (Priority: P1)

As an operator, I want the system to correlate operational telemetry into a clear root-cause hypothesis with confidence scores and causal chains, so that I understand why the incident occurred without parsing thousands of raw logs.

**Why this priority**: Accurate diagnosis is required before any safe remediation can be selected. Operators must see supporting evidence and confidence rather than ungrounded guesses.

**Independent Test**: Can be tested by providing degraded transcoder metrics, GPU allocation failures, and a recent deployment event, and verifying that the system outputs a ranked hypothesis pointing to the faulty transcoder deployment with supporting evidence.

**Acceptance Scenarios**:

1. **Given** telemetry indicating elevated transcoder latency, GPU allocation errors, and a recent transcoder service deployment, **When** the Observability Investigator completes analysis, **Then** the system outputs a primary root cause identifying the transcoder deployment, an associated confidence score (e.g., 94%), the affected services/regions, and correlated supporting signals.
2. **Given** an explanation of the root cause, **When** displayed to the operator, **Then** it shows concise evidence-based explanations without revealing raw internal model chain-of-thought tokens.

---

### User Story 4 - Live Media Business Impact & Exposure Assessment (Priority: P2)

As a media executive or operations leader, I want technical telemetry translated into live media business impact, so that incident severity reflects audience disruption, VIP viewer impact, and financial/SLA exposure.

**Why this priority**: Technical metrics alone do not reflect business urgency. Quantifying viewer loss, ad window disruption, and SLA penalties enables appropriate escalation and governance.

**Independent Test**: Can be tested by supplying affected region metrics during a high-profile sports final and verifying that the Business Impact Agent calculates affected viewer counts, ad risk, and an overall business impact score.

**Acceptance Scenarios**:

1. **Given** degraded playback across Australia and Singapore during an active advertising window, **When** the Business Impact Agent evaluates the event, **Then** it calculates estimated affected viewers (e.g., 1.8M), premium/VIP viewers impacted, business impact score (e.g., 88/100), high-risk ad windows, and projected financial exposure.
2. **Given** an incident occurring during non-critical broadcast segments, **When** evaluated, **Then** the business impact score scales proportionally to viewer concurrency and contractual SLA commitments.

---

### User Story 5 - Deterministic Safety Evaluation & Governance Gate (Priority: P1)

As an operations director, I want all candidate remediations evaluated by a deterministic safety policy before execution, so that no AI agent can execute arbitrary or high-blast-radius actions without policy clearance or human sign-off.

**Why this priority**: Safety is non-negotiable in live broadcast environments where millions of viewers are active. Autonomous actions must be bounded by deterministic policy.

**Independent Test**: Can be tested by proposing low-risk vs high-risk remediation actions and verifying that low-risk actions pass as `AUTO_EXECUTE` while high-risk or low-confidence actions require `HUMAN_APPROVAL_REQUIRED`.

**Acceptance Scenarios**:

1. **Given** a proposed remediation with high confidence, low blast radius, and pre-authorized action type (e.g., shifting regional traffic to standby encoders), **When** evaluated by the Safety Director, **Then** the action is designated as `AUTO_EXECUTE` with safety reasoning logged.
2. **Given** a proposed remediation with high blast radius (e.g., global service restart) or confidence below safe threshold, **When** evaluated by the Safety Director, **Then** the workflow pauses in `HUMAN_APPROVAL_REQUIRED` state and alerts operators for explicit approval.

---

### User Story 6 - Controlled Remediation Execution (Priority: P1)

As an operations engineer, I want the system to execute the approved remediation against the actual live streaming infrastructure, so that recovery happens in seconds without manual infrastructure commands.

**Why this priority**: A diagnosis without action fails to resolve the outage. The system must perform genuine remediation (traffic routing, scaling, restarting) to restore service.

**Independent Test**: Can be tested by approving a traffic shift or container restart and verifying that an actual infrastructure command or mock environment operation is executed, audited, and logged.

**Acceptance Scenarios**:

1. **Given** an approved remediation plan (e.g., shift Australia/Singapore traffic to healthy backup transcoders via routing proxy API), **When** the Remediation Agent executes the action, **Then** the controlled operation is dispatched, execution start/finish timestamps are recorded, and the audit trail is updated.
2. **Given** an infrastructure failure or timeout during remediation execution, **When** the action fails, **Then** the Remediation Agent catches the error, marks the action as `FAILED`, records the error detail, and routes back to the Incident Commander.

---

### User Story 7 - Independent Telemetry Verification (Priority: P1)

As an operations engineer, I want an independent Verification Agent to re-query telemetry after remediation, so that the incident is never resolved based solely on command exit codes.

**Why this priority**: In live streaming, HTTP 200 from a command does not guarantee viewer video packets are flowing cleanly. Verification must measure post-remediation telemetry.

**Independent Test**: Can be tested by executing remediation and checking that the Verification Agent queries metrics, compares before/after error rates, and only marks the incident `RESOLVED` if telemetry returns to normal.

**Acceptance Scenarios**:

1. **Given** a completed remediation action, **When** the Verification Agent queries post-action telemetry, **Then** it compares error rates against pre-incident baselines (e.g., error rate drops from 8.7% to 0.5%) and declares recovery verified.
2. **Given** a completed remediation action where telemetry remains degraded (e.g., error rate remains > 5.0%), **When** the Verification Agent tests the stream, **Then** it declares recovery failed, keeps the incident active, and reports failure to the Incident Commander.

---

### User Story 8 - Automated Closed-Loop Re-investigation (Priority: P2)

As an operator, I want the system to automatically re-investigate if initial remediation fails verification, so that the autonomous loop can attempt alternative remediations within safe retry limits.

**Why this priority**: Single-shot remediation systems fail whenever initial assumptions are incomplete. Closed-loop re-evaluation provides true operational resilience.

**Independent Test**: Can be tested by simulating verification failure on attempt 1, verifying that the Incident Commander triggers a re-investigation cycle, and caps attempts at the configured threshold (e.g., 2 attempts).

**Acceptance Scenarios**:

1. **Given** a verification failure on the first remediation attempt, **When** maximum retry attempts have not been reached, **Then** the workflow transitions to `REINVESTIGATING`, generates an alternative hypothesis or fallback remediation, and re-enters the safety evaluation gate.
2. **Given** repeated verification failures reaching the maximum retry limit, **When** the threshold is exceeded, **Then** the Incident Commander escalates the incident to `ESCALATED_HUMAN_TAKEOVER` and halts autonomous execution.

---

### User Story 9 - Incident Memory & Historical Fingerprint Matching (Priority: P2)

As an operations engineer, I want the system to match active incidents against historical incident fingerprints, so that proven past remediations accelerate current resolution and build institutional memory.

**Why this priority**: Live sports and entertainment events often encounter recurring failure modes (e.g., GPU driver crash under 4K HDR load). Surfacing historical precedent builds operator trust and shortens resolution time.

**Independent Test**: Can be tested by injecting an incident with symptoms matching a stored historical incident and verifying that the system displays the match, match confidence, past root cause, and past successful remediation retrieved via Vertex AI Search / Agent Builder.

**Acceptance Scenarios**:

1. **Given** an active incident with symptoms matching a previously recorded event, **When** the Incident Commander inspects incident memory, **Then** it retrieves the matching historical incident via Vertex AI Search / Agent Builder, shows similarity score (e.g., 92%), previous root cause, and previously successful remediation action.
2. **Given** a successfully resolved incident, **When** the post-incident workflow concludes, **Then** a structured incident fingerprint is persisted into PostgreSQL and indexed for future matching.

---

### User Story 10 - Multi-Stakeholder Automated Incident Reporting (Priority: P3)

As an incident manager, executive, or communications lead, I want tailored reports generated automatically upon resolution, so that engineering, executive leadership, and customer teams have clear, role-specific communications without manual copywriting.

**Why this priority**: After high-visibility incidents, manual reporting creates communication bottlenecks and inconsistencies between technical and business teams.

**Independent Test**: Can be tested by resolving an incident and verifying that three distinct reports are generated: Engineering Root-Cause Analysis, Executive Brief, and Customer-Facing Status Statement.

**Acceptance Scenarios**:

1. **Given** a resolved or escalated incident, **When** reports are requested, **Then** the system generates an Engineering RCA Report (technical timeline, telemetry deltas, causal chain), an Executive Summary (viewer impact, financial exposure, downtime duration), and a Customer Communication Draft (empathetic, non-technical status update).
2. **Given** report generation, **When** rendered, **Then** reports reflect verified facts from the persistent system of record without hallucinating unobserved metrics.

---

### User Story 11 - Live Broadcast Operations Command Center UI (Priority: P1)

As a broadcast operations director, I want a unified cinematic operational command center, so that I can see the live event status, stream health, real-time agent progression, business impact, and safety controls in a single glance.

**Why this priority**: Operators under pressure need instant situational awareness. The dashboard must communicate critical status within 10 seconds.

**Independent Test**: Can be tested by viewing the web interface during a simulated incident run and confirming that event telemetry, agent states, root-cause cards, business impact dials, and action controls update live via SSE without page reloads.

**Acceptance Scenarios**:

1. **Given** an active live streaming event, **When** an operator opens the Command Center, **Then** they see live event status, stream telemetry graphs, agent hierarchy with active states, business impact metrics, and recent timeline events.
2. **Given** a pending human approval requirement, **When** the operator views the Command Center, **Then** an approval banner is prominently displayed with action details, blast radius, risk level, and one-click `APPROVE` / `REJECT` controls.
3. **Given** the visual presentation, **When** loaded, **Then** the interface presents a sleek, dark, cinematic broadcast operations aesthetic with a focused React Three Fiber spatial globe displaying live health across distribution regions.

---

### Edge Cases

- **Telemetry Partner Unavailable**: If Grafana MCP or the underlying telemetry source is unreachable, the system enters `DEGRADED_OBSERVABILITY` state, alerts operators, and blocks autonomous actions based on stale data.
- **Reasoning Model Rate Limit or Unavailability**: If Gemini is temporarily unavailable, deterministic fallback rules handle basic safety and alerting, and pending operations fail safely to human approval.
- **Conflicting Hypotheses**: When evidence supports multiple competing root causes with similar confidence (e.g., network vs encoder), the system flags ambiguity, lowers autonomous confidence, and requests operator review.
- **Unsafe Remediation Boundary**: If a candidate remediation affects more than 25% of total viewer concurrency or global services, the Safety Director hard-blocks auto-execution regardless of model confidence.
- **Operator Override / Abort**: At any point in the autonomous lifecycle, an operator can click `MANUAL TAKEOVER`, immediately aborting autonomous agent executions and freezing infrastructure commands.
- **Flapping Metrics**: If telemetry rapidly oscillates between healthy and degraded, the Verification Agent enforces a minimum stability window before declaring permanent resolution.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Core Incident Lifecycle & Workflow
- **FR-001**: System MUST maintain distinct lifecycle states: `HEALTHY`, `DETECTING`, `INVESTIGATING`, `ASSESSING_IMPACT`, `EVALUATING_SAFETY`, `AWAITING_APPROVAL`, `REMEDIATING`, `VERIFYING`, `REINVESTIGATING`, `RESOLVED`, `ESCALATED_HUMAN_TAKEOVER`.
- **FR-002**: System MUST assign a unique, persistent incident identifier to every detected incident.
- **FR-003**: System MUST execute the closed-loop autonomous cycle: Observe → Investigate → Correlate → Assess → Decide → Govern → Act → Verify → Resolve.
- **FR-004**: System MUST limit automatic re-investigation attempts to a configurable threshold (default: 2 attempts) before mandatory human escalation.

#### Multi-Agent Architecture
- **FR-005**: System MUST implement distinct specialist agents defined with Google Cloud Agent Development Kit (ADK) / GenAI SDK in Python with non-overlapping responsibilities: Incident Commander (supervisor), Observability Investigator, Business Impact Agent, Remediation Agent, and Verification Agent.
- **FR-006**: Incident Commander MUST govern workflow progression and state transitions via deterministic supervisory logic.
- **FR-007**: Individual specialist agents MUST NOT invoke or bypass peer agents directly; all coordination must route through the Incident Commander and shared state.
- **FR-008**: System MUST record every agent execution, run duration, tool invocations, inputs, and structured outputs to durable PostgreSQL storage.

#### Observability & Evidence Correlation
- **FR-009**: Observability Investigator MUST integrate with Grafana at runtime via a Grafana Model Context Protocol (MCP) client, executing tools to query metrics, logs, traces, and alert rules.
- **FR-010**: System MUST correlate multiple telemetry signals (e.g., playback error rate, transcoding latency, GPU allocation errors, deployment history) to formulate ranked root-cause hypotheses.
- **FR-011**: System MUST compute a numerical confidence score (0–100%) for each generated hypothesis.
- **FR-012**: System MUST present concise, evidence-based natural language explanations without outputting private model chain-of-thought traces.

#### Business Impact Quantification
- **FR-013**: Business Impact Agent MUST quantify incident severity in live media terms: total affected viewers, premium/VIP viewer count, geographic regions impacted, active advertising window exposure, and SLA penalty risk.
- **FR-014**: System MUST compute a normalized Business Impact Score (1–100) combining audience scale, event prominence, and revenue exposure.

#### Safety Director & Governance Gate
- **FR-015**: System MUST route all candidate remediation actions through a deterministic Safety Director before execution.
- **FR-016**: Safety Director MUST evaluate action type, diagnostic confidence, estimated blast radius, operational risk, and authorization rules.
- **FR-017**: Remediation actions classified as high-risk, high blast radius, or low confidence MUST require explicit human approval (`HUMAN_APPROVAL_REQUIRED`).
- **FR-018**: System MUST provide an interactive human approval mechanism allowing operators to approve, reject, or modify proposed remediation actions via authenticated API calls.

#### Remediation Execution & Independent Verification
- **FR-019**: Remediation Agent MUST perform actual, verifiable operations against a live video routing proxy API (e.g., shifting regional traffic weights to standby transcoders) rather than updating UI labels or database flags.
- **FR-020**: Verification Agent MUST independently query telemetry after remediation completes to evaluate whether operational metrics have returned to healthy baselines.
- **FR-021**: System MUST forbid transitioning an incident to `RESOLVED` until post-remediation verification confirms metric recovery.
- **FR-022**: If post-remediation telemetry remains degraded, Verification Agent MUST declare verification failure and trigger re-investigation or escalation.

#### Persistence & Incident Memory
- **FR-023**: System MUST persist all incidents, state transitions, agent runs, hypotheses, business impact calculations, remediation audits, and verification records in a durable PostgreSQL relational store.
- **FR-024**: System MUST compute and store an incident fingerprint upon resolution, indexing it into Vertex AI Search / Agent Builder for semantic historical matching.
- **FR-025**: System MUST surface similar historical incidents from Vertex AI Search / Agent Builder, matching confidence, previous root causes, and previously successful remediations during active investigations.

#### Multi-Stakeholder Reporting
- **FR-026**: System MUST generate three distinct post-incident reports upon resolution: an Engineering Root-Cause Analysis (RCA), an Executive Summary, and a Customer-Facing Communication Draft.

#### Broadcast Operations Command Center UI
- **FR-027**: System MUST provide a responsive, real-time web command center displaying event telemetry, active agent states, root cause cards, business impact metrics, and operational audit timelines streamed via Server-Sent Events (SSE).
- **FR-028**: UI MUST support real-time updates of agent states and incident progress without manual page refreshes.
- **FR-029**: UI MUST incorporate a focused React Three Fiber 3D spatial globe displaying regional broadcast node health to enhance situational awareness without decorative clutter.
- **FR-030**: UI MUST provide an immediate emergency override button (`MANUAL TAKEOVER`) that freezes autonomous agent executions.

---

### Key Entities *(include if feature involves data)*

- **LiveEvent**: Represents the broadcast event being monitored (e.g., event ID, title, event type, scheduled start/end, baseline viewer count, current viewer count, operational status `HEALTHY` | `INCIDENT` | `DEGRADED`).
- **Incident**: Represents a detected streaming failure (incident ID, event ID, start time, end time, current status, severity level, primary affected service, affected regions, retry count).
- **AgentRun**: Represents a discrete execution of a specialist agent (run ID, incident ID, agent name, status `RUNNING` | `COMPLETED` | `FAILED`, start timestamp, completion timestamp, tool invocation summary, execution duration).
- **TelemetryEvidence**: Represents empirical observations collected from monitoring (evidence ID, incident ID, source system, metric name, baseline value, observed value, timestamp, anomaly score).
- **Hypothesis**: Represents a diagnostic conclusion formulated from evidence (hypothesis ID, incident ID, root cause description, primary component, confidence score, causal explanation, supporting evidence IDs).
- **BusinessImpact**: Represents quantified operational and financial disruption (impact ID, incident ID, affected viewer count, VIP viewer count, affected regions, ad window impacted, estimated financial exposure, impact score).
- **SafetyEvaluation**: Represents the deterministic policy assessment of a proposed action (evaluation ID, incident ID, candidate action ID, blast radius score, risk level, decision `AUTO_EXECUTE` | `HUMAN_APPROVAL_REQUIRED` | `BLOCKED`, policy rule applied).
- **RemediationAction**: Represents a controlled operational command (action ID, incident ID, action type, target resource, parameters, execution status `PENDING` | `IN_PROGRESS` | `SUCCEEDED` | `FAILED`, executed timestamp, execution output).
- **VerificationResult**: Represents independent post-action validation (verification ID, incident ID, remediation action ID, pre-action metric value, post-action metric value, recovery status `VERIFIED` | `UNVERIFIED` | `FAILED`, recovery confidence).
- **IncidentFingerprint**: Represents historical pattern data for correlation (fingerprint ID, incident ID, feature vector/signature, symptoms summary, resolved root cause, successful remediation action).
- **IncidentReport**: Represents stakeholder-specific post-incident summaries (report ID, incident ID, report type `ENGINEERING_RCA` | `EXECUTIVE_BRIEF` | `CUSTOMER_STATEMENT`, content markdown, generated timestamp).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System detects live streaming telemetry degradation and transitions event status to `INCIDENT` within 5 seconds of threshold breach.
- **SC-002**: Multi-agent investigation (Incident Commander, Observability Investigator, Business Impact Agent) completes initial diagnosis and impact assessment within 30 seconds of incident detection.
- **SC-003**: Root cause hypothesis accurately pinpoints the faulty component with evidence correlation and confidence rating exceeding 85% in standard test scenarios.
- **SC-004**: 100% of candidate remediation actions pass through deterministic safety evaluation before any infrastructure command is dispatched.
- **SC-005**: Autonomous end-to-end recovery (detection through verified resolution) executes in under 90 seconds for pre-authorized low-blast-radius scenarios.
- **SC-006**: Verification Agent independently validates operational telemetry recovery before any incident can transition to `RESOLVED`, eliminating false-positive resolution.
- **SC-007**: Operators can evaluate live event status, agent execution states, and business impact on the Command Center UI within 10 seconds of opening the dashboard.
- **SC-008**: An external evaluator or judge can trigger, observe, and verify a complete reproducible incident demonstration in under 3 minutes via the Scenario Simulator.

---

## Assumptions

- **Target Audience & Operation**: Primary users are broadcast engineers, SREs, and live streaming operations specialists with access to modern desktop browser environments.
- **Demo & Runtime Environment**: The primary demo scenario simulates a premier live sports final ("India vs Australia Final") with realistic telemetry, transcoders, and infrastructure hooks.
- **Telemetry Integration**: Operational telemetry (metrics, logs, traces) is accessible via a runtime Grafana MCP client interfacing with Prometheus, Loki, Tempo, and alert engines.
- **Reasoning Provider**: Gemini reasoning capabilities are leveraged via Python Agent Development Kit (ADK) / GenAI SDK with structured schemas, keeping API credentials secure on the server side.
- **Incident Memory Store**: Historical fingerprints are persisted in PostgreSQL and semantically searched using Vertex AI Search / Agent Builder.
- **Infrastructure Remediation**: Controlled remediation actions interact with a live mock video routing proxy API that exhibits real state changes and telemetry impact.
- **Persistent Storage**: Relational persistence is provided by PostgreSQL to maintain audit trails, state transitions, and incident fingerprints across server restarts.
