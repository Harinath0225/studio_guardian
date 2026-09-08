# Feature Specification: Predictive Media Protection & Black Swan Defense

**Feature Branch**: `003-predictive-defense`  
**Created**: 2026-09-08  
**Last Updated**: 2026-09-08  
**Status**: Clarified Draft  
**Input**: User description: "PREDICTIVE MEDIA PROTECTION & BLACK SWAN DEFENSE: Autonomous reliability and revenue-protection system for live media (Predict -> Prevent -> Prove and Detect -> Investigate -> Remediate -> Verify)"

---

## Clarifications

### Session 2026-09-08

- **Q: Which Google-supported Vertex AI agent architecture will be used as the actual agent runtime?**  
  → **A:** The system uses the Google Vertex AI Agent Engine / Google GenAI SDK Agent Runtime architecture. The runtime provides genuine session management, execution trace frames, and a visible multi-agent delegation path: `Application → Vertex AI Agent Runtime → Incident Commander → Specialist Agents → Tools/MCP → Decisions/Actions`. The UI exposes truthful runtime metadata (agent runtime, agent name, current specialist, session identifier, agent state, tool execution events).

- **Q: What is the exact Grafana MCP transport, authentication method, available tools, and persistence mechanism?**  
  → **A:** Transport is `streamable-http` at `http://localhost:8001/mcp` with `Mcp-Session-Id` header session management. Authentication is unauthenticated for local Docker or Bearer token (`GRAFANA_SERVICE_ACCOUNT_TOKEN`) for managed Grafana. Required tools are `query_prometheus`, `query_loki_logs`, `alerting_manage_rules`, and `tempo_get-trace`. Datasources are Prometheus, Loki, and Tempo. Raw tool responses and telemetry snapshots are persisted into relational storage (SQLite/PostgreSQL) and audit frames.

- **Q: What are the exact mathematical normalized ranges, baselines, weights, thresholds, trend calculation, and confidence representations?**  
  → **A:** 
  - *Normalized Ranges*: Dimensionless values strictly bounded within `[0.0, 1.0]`.
  - *SLO Baselines (Floor/Ceiling)*: GPU (50.0% / 95.0%), Latency (150.0ms / 500.0ms), Queue Depth (5.0 / 50.0), Playback Error Rate (0.30% / 1.50%), Regional Saturation (60.0% / 95.0%), Active Viewers (5M / 15M).
  - *Risk Weights*: GPU Pressure (0.25), Queue Growth (0.20), Latency Pressure (0.20), Playback Error Growth (0.15), Viewer Growth (0.10), Deployment Recency Risk (0.10).
  - *Risk Tiers*: `HEALTHY` (<0.30), `WATCH` (0.30–0.59), `ELEVATED_RISK` (0.60–0.79), `HIGH_RISK` (0.80–0.89), `IMMINENT_RISK` (≥0.90).
  - *Trend Calculation*: 60-second sliding regression slope (`dy/dt` per minute) and 2nd derivative acceleration (`d²y/dt²`).
  - *Prediction Window*: Deterministic time-to-threshold calculation bounded between 3 and 15 minutes: `(0.90 - risk_score) / rate` with `[0.8x, 1.3x]` uncertainty intervals.
  - *Confidence Representation*: Independent `[0.0, 1.0]` score combining telemetry freshness (35%), sensor completeness (35%), and multi-signal directional concordance (30%).

- **Q: How are SCTE-35 timing thresholds and perceptual media quality bounded?**  
  → **A:** SCTE-35 timing drift is evaluated against configured operational tolerances (e.g. alignment tolerance ±200ms operational threshold) without making unsupported regulatory or standards compliance claims. Perceptual media quality is strictly limited to 4 lightweight measurable signals: audio/video synchronization offset (ms), loudness deviation (LUFS/LKFS), dropped frames ratio (%), and black-frame ratio (%). Professional broadcast QC platform emulation is strictly out of scope.

- **Q: How is counterfactual ROI represented to ensure financial honesty?**  
  → **A:** Financial outcomes from successful prevention are strictly labeled as **Estimated Exposure Avoided** (e.g., "Estimated exposure avoided: $142,500") rather than observed savings, explicitly maintaining the distinction between `OBSERVED`, `PREDICTED`, `ESTIMATED`, and `VERIFIED`.

- **Q: Which controlled remediation and Black Swan scenarios are prioritized for implementation?**  
  → **A:** The primary predictive remediation is **TRANSCODER CAPACITY SCALE** (`scale_transcoder_pool`), doubling worker capacity to absorb load surges before viewer degradation. Black Swan demonstration scenarios are strictly limited to two deterministic scenarios: (1) **Transcoder Capacity Surge** and (2) **SCTE-35 Corruption**.

- **Q: What technologies and architectural components are explicitly out of scope?**  
  → **A:** Custom ML model training/fine-tuning, dedicated ML infrastructure (Kubeflow, MLflow), Kubernetes orchestration, Kafka/event-streaming clusters, vector databases, and broadcast-grade QC hardware/software are strictly excluded. The implementation uses deterministic simulation plus genuine Grafana MCP telemetry.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Predictive Risk Prevention via Capacity Scaling (Priority: P1)

As a broadcast operations engineer, I want the system to continuously monitor live telemetry via Grafana MCP to predict infrastructure exhaustion before viewers experience buffering, calculate the estimated business exposure, and autonomously execute verified capacity scaling.

**Why this priority**: Predictive prevention is the flagship "Predict → Prevent → Prove" lifecycle. It shifts operations from reactive firefighting to proactive mitigation, delivering measurable enterprise value.

**Independent Test**: Can be fully tested by simulating early warning signals (transcoder GPU climbing to 93%, queue depth rising to 48) and verifying that the system predicts failure within 3–10 minutes, calculates estimated exposure avoided, triggers Transcoder Capacity Scaling (`scale_transcoder_pool`), and verifies risk reduction ("PREDICTED RISK MITIGATED") using fresh Grafana telemetry.

**Acceptance Scenarios**:

1. **Given** a live streaming event with rising leading indicators (GPU >85%, queue buildup), **When** the Predictive Risk Agent analyzes the telemetry, **Then** it must output a risk score in the `IMMINENT_RISK` tier (≥0.90), identify `transcoder_capacity_exhaustion` as the predicted failure mode, and estimate a 3–10 minute prediction window.
2. **Given** a confirmed prediction with risk ≥0.80 and confidence ≥0.85, **When** the Safety Director approves preventive remediation, **Then** the system must execute Transcoder Capacity Scaling, re-query Grafana MCP telemetry, and demonstrate a measurable reduction in risk before playback error rates rise.

---

### User Story 2 - Reactive Incident Fallback (Priority: P1)

As an operations director, I need the system to cleanly fall back to reactive incident response if prediction fails or an abrupt failure occurs, fully investigating observability signals and safely executing remediation.

**Why this priority**: Black swan events and sudden infrastructure drops cannot always be anticipated. A closed-loop system must handle actual incidents with equal autonomy.

**Independent Test**: Can be fully tested by injecting an instant playback error spike (e.g., error rate 8.7%, latency 485ms), ensuring the system transitions to Detect → Investigate → Remediate → Verify, shifts traffic to a healthy standby cluster, and verifies recovery.

**Acceptance Scenarios**:

1. **Given** an active incident with playback errors exceeding the operational threshold (>2.0%), **When** the reactive workflow activates, **Then** specialist agents must investigate metrics/logs/traces via Grafana MCP, identify root cause, execute traffic shifting, and verify stream recovery.

---

### User Story 3 - Semantic Media Quality & Ad Integrity Sentinel (Priority: P2)

As an ad operations and quality control manager, I need the system to detect semantic media failures like SCTE-35 splice timing drift and perceptual quality anomalies, even when traditional infrastructure (CPU/Memory) appears healthy.

**Why this priority**: Infrastructure health does not guarantee media health. High-value revenue can be lost to ad splice failures while servers report nominal CPU and memory.

**Independent Test**: Can be fully tested by simulating SCTE-35 splice timing drift beyond configured operational tolerance (±200ms) without altering CPU/Memory metrics, and verifying the Ad Integrity specialist detects the business risk and recommends fallback.

**Acceptance Scenarios**:

1. **Given** healthy server CPU and memory metrics but degraded SCTE-35 ad splice timing exceeding the configured operational tolerance, **When** the Ad Integrity Sentinel inspects the stream, **Then** it must detect the timing drift, calculate estimated ad revenue exposure, and recommend ad pod mitigation.
2. **Given** a stream exhibiting AV sync offset (>150ms), loudness deviation (>3.0 LUFS), frame drop (>5%), or black frames (>2%), **When** the Perceptual Quality Sentinel evaluates the stream, **Then** it must flag the anomaly as a leading signal without requiring full broadcast QC tooling.

---

### User Story 4 - Deterministic Black Swan Gameday (Priority: P3)

As a demonstrator or chaos engineer, I want a deterministic chaos panel to intentionally inject failure scenarios to prove the autonomous system works reliably during live demonstrations.

**Why this priority**: Provides reproducible proof of the system's predictive and reactive capabilities for live demonstrations, evaluations, and resilience testing.

**Independent Test**: Can be fully tested by triggering the two deterministic scenarios from the UI and verifying that the exact telemetry cascade and agent response flow execute.

**Acceptance Scenarios**:

1. **Given** the chaos panel, **When** the user triggers **Transcoder Capacity Surge**, **Then** the system must simulate the leading metric cascade (rising GPU and queue depth) and trigger predictive capacity scaling.
2. **Given** the chaos panel, **When** the user triggers **SCTE-35 Corruption**, **Then** the system must simulate ad cue splice drift and corrupt splice inserts, triggering ad integrity alerts and estimated exposure calculation.

---

### Edge Cases

- **Grafana MCP Unreachable / Timeout**: If Grafana MCP fails to respond within 5 seconds during telemetry collection or verification, the system must log an operational error, fall back to cached telemetry snapshots with a degraded confidence score (<0.50), and refuse autonomous remediation until live connectivity is re-established.
- **Conflicting Telemetry Signals**: If one metric indicates extreme degradation (e.g., GPU at 98%) while others indicate nominal health (error rate 0.38%), the system must apply multi-signal concordance weighting, downgrade confidence to ≤0.65, and flag the condition for human operator review before initiating automated remediation.
- **Safety Director Rejection**: If the Safety Director policy engine rejects a proposed preventive action (e.g., blast radius >20% or confidence <0.85), the system must abort execution, log the policy violation in the audit trail, and notify operators with the specific constraint that was violated.
- **Failed Remediation Verification**: If post-remediation verification telemetry reveals that metrics did not improve or worsened, the system must immediately escalate the incident to reactive status, notify operators, and prevent duplicate remediation loops.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST ingest telemetry exclusively via Grafana MCP over the `streamable-http` transport using official tools (`query_prometheus`, `query_loki_logs`, `alerting_manage_rules`, `tempo_get-trace`), maintaining session state with `Mcp-Session-Id`.
- **FR-002**: System MUST persist all raw Grafana MCP tool responses and telemetry snapshots into relational storage (SQLite/PostgreSQL) with execution audit frames.
- **FR-003**: System MUST normalize raw telemetry metrics into dimensionless `[0.0, 1.0]` features using deterministic min-max clamping against defined operational SLO bounds (GPU 50–95%, Latency 150–500ms, Queue 5–50, Playback Error 0.30–1.50%).
- **FR-004**: System MUST compute a deterministic composite risk score `[0.0, 1.0]` using configured weights (GPU 0.25, Queue 0.20, Latency 0.20, Error 0.15, Viewers 0.10, Deployment 0.10) and classify the stream into operational risk tiers (`HEALTHY`, `WATCH`, `ELEVATED_RISK`, `HIGH_RISK`, `IMMINENT_RISK`).
- **FR-005**: System MUST compute telemetry velocity using a 60-second sliding regression slope (`dy/dt`) and 2nd derivative acceleration (`d²y/dt²`) to detect accelerating bottlenecks.
- **FR-006**: System MUST estimate a deterministic prediction horizon window bounded between 3 and 15 minutes, and calculate an independent confidence score `[0.0, 1.0]` based on data freshness (35%), completeness (35%), and concordance (30%).
- **FR-007**: System MUST evaluate SCTE-35 ad cue timing against configured operational tolerances (±200ms alignment) and assess lightweight perceptual quality signals (AV sync offset, loudness deviation, dropped frames, black frames) without making unsupported broadcast standards compliance claims.
- **FR-008**: System MUST deterministically calculate estimated business exposure (viewer loss, ad revenue burn, SLA liability) and preventive value, explicitly labeling all figures as **Estimated Exposure Avoided** to maintain counterfactual honesty.
- **FR-009**: System MUST govern all automated remediation actions through a deterministic Safety Director policy engine enforcing confidence thresholds (≥0.85), blast radius limits (≤20%), and action allowlists before any mutation occurs.
- **FR-010**: System MUST support **TRANSCODER CAPACITY SCALE** (`scale_transcoder_pool`) as the primary controlled preventive remediation, doubling worker pool capacity to absorb impending load surges.
- **FR-011**: System MUST independently verify remediation efficacy by querying fresh Grafana MCP telemetry post-action and comparing BEFORE vs AFTER values, confirming risk reduction before marking the state as `PREDICTED RISK MITIGATED` or `RECOVERED`.
- **FR-012**: System MUST provide a deterministic chaos injection panel supporting two specific Black Swan scenarios: (1) Transcoder Capacity Surge and (2) SCTE-35 Corruption.
- **FR-013**: System MUST execute the Incident Commander and Specialist Agents within the Google Vertex AI Agent Engine / Google GenAI SDK Agent Runtime, exposing live runtime metadata (agent runtime, agent name, current specialist, session ID, agent state, tool events) in the UI.

### Explicit Out-of-Scope Declarations

- **OOS-001**: NO custom machine learning model training, offline model training pipelines, or fine-tuning workflows.
- **OOS-002**: NO dedicated ML infrastructure (e.g., Kubeflow, MLflow, Vertex Feature Store).
- **OOS-003**: NO Kubernetes cluster orchestration dependencies (local Docker and native Python processes only).
- **OOS-004**: NO Apache Kafka or external distributed message brokers.
- **OOS-005**: NO external vector database systems (incident memory is stored and indexed in relational PostgreSQL/SQLite).
- **OOS-006**: NO professional-grade broadcast QC hardware or software suites (perceptual analysis is strictly limited to AV sync, loudness, frame drops, and black frames).

---

## Data Model & Key Entities *(mandatory)*

### Normalized Signal Features
- `gpu_pressure`: Dimensionless `[0.0, 1.0]` (clamped against floor 50.0%, ceil 95.0%).
- `queue_growth`: Dimensionless `[0.0, 1.0]` (clamped against floor 5.0, ceil 50.0, with slope and acceleration booster).
- `latency_pressure`: Dimensionless `[0.0, 1.0]` (clamped against floor 150.0ms, ceil 500.0ms).
- `error_growth`: Dimensionless `[0.0, 1.0]` (clamped against floor 0.30%, ceil 1.50%).
- `viewer_growth`: Dimensionless `[0.0, 1.0]` (clamped against floor 5M, ceil 15M).
- `deployment_risk`: Dimensionless `[0.0, 1.0]` (0.60 penalty if deployment occurred within 300 seconds).

### Prediction State
- `risk_score`: Float `[0.0, 1.0]`.
- `risk_tier`: Enum (`HEALTHY`, `WATCH`, `ELEVATED_RISK`, `HIGH_RISK`, `IMMINENT_RISK`).
- `predicted_failure_mode`: String identifier (e.g., `transcoder_capacity_exhaustion`).
- `prediction_window`: Object with `min_minutes` and `max_minutes` (bounded within `[3, 15]`).
- `confidence`: Float `[0.0, 1.0]` (derived from freshness, completeness, concordance).
- `contributors`: List of signal contributors with raw values, normalized values, and points.

### Business Impact & Counterfactual ROI
- `projected_disrupted_viewers`: Integer estimated viewer count.
- `ad_revenue_at_risk_usd`: Float estimated ad burn (CPM $28.50, 12 ads/hr).
- `sla_penalty_exposure_usd`: Float estimated SLA liability (hourly penalty $75,000 at threshold).
- `cost_of_prevention_usd`: Float estimated compute cost of remediation (e.g., 8 nodes * $42.50/hr).
- `expected_avoided_exposure_usd`: Float net estimated savings (`expected_loss - cost_of_prevention`).
- `provenance_label`: String indicator (`ESTIMATED` for proactive avoided loss, `OBSERVED` only for real ongoing outages).

### Vertex AI Runtime Metadata
- `agent_runtime`: String (`Vertex AI Agent Engine`).
- `agent_name`: String (e.g., `PredictiveRiskAgent`, `IncidentCommander`).
- `current_specialist`: String (active sub-agent).
- `session_id`: String unique session identifier (`session-pred-...`).
- `agent_state`: String (`IDLE`, `INGESTING_TELEMETRY`, `CALCULATING_RISK`, `AWAITING_POLICY`, `REMEDIATING`, `VERIFYING`).
- `execution_frames`: List of audit trace events with timestamps, stages, and tool outputs.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The system autonomously predicts an impending capacity failure before playback error rates exceed nominal baseline (0.50%), reports an `IMMINENT_RISK` tier, and bounds the failure window within 3–15 minutes.
- **SC-002**: The system executes Transcoder Capacity Scaling (`scale_transcoder_pool`) under Safety Director policy approval, queries fresh Grafana MCP telemetry, and confirms GPU utilization falls below 70% and queue depth below 15, reporting "PREDICTED RISK MITIGATED".
- **SC-003**: 100% of numerical risk scores and financial estimates trace deterministically to raw Grafana telemetry and defined mathematical formulas without LLM mathematical hallucinations.
- **SC-004**: All telemetry queries and verification calls execute via genuine Grafana MCP `streamable-http` transport calls.
- **SC-005**: All financial prevention metrics in the UI and reports are explicitly labeled as "Estimated Exposure Avoided", satisfying counterfactual honesty.
- **SC-006**: The system demonstrates both prioritized Black Swan scenarios (Transcoder Capacity Surge and SCTE-35 Corruption) deterministically without code modifications.
- **SC-007**: The UI displays truthful Vertex AI Agent Engine runtime metadata (agent runtime, session ID, current specialist, agent state, execution frames) throughout both predictive and reactive workflows.

---

## Assumptions & Dependencies

- Grafana MCP server runs at `http://localhost:8001/mcp` providing access to Prometheus metrics, Loki logs, and Tempo traces.
- The Safety Director operates with deterministic allowlists and policy thresholds (confidence ≥0.85, blast radius ≤20%).
- Financial parameters (CPM $28.50, SLA liability tiers, node hourly costs) are configurable operational baselines.
- The simulated media environment produces realistic multi-metric telemetry cascades corresponding to injected Black Swan events.
