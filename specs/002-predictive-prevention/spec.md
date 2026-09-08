# Feature Specification: Predictive Prevention & Proactive Remediation

**Feature Branch**: `002-predictive-prevention`

**Created**: 2026-09-07

**Status**: Draft

**Input**: User description: "Extend Studio Guardian so it does not only react to incidents after degradation begins. It must continuously analyze operational signals and detect when a live media system is approaching an unsafe operating condition. The system should predict an emerging incident, explain the evidence, recommend preventative action, apply governance, execute a controlled preventive remediation when safe, and independently verify that the predicted incident was avoided. This feature must sit on top of the existing Studio Guardian multi-agent architecture."

---

## Clarifications

### Session 2026-09-07

- Q: How should the backend normalize raw operational telemetry and calculate rate-of-change signals from Grafana MCP into 0.0–1.0 model inputs? → A: Option A (SLO Min-Max Clamping + 60s Sliding Slope: Static gauges clamped between baseline SLO and critical ceiling [0.0, 1.0]; growth signals computed as linear slope over 60s window).
- Q: How should the system calculate prediction confidence independently from the risk score to gate autonomous safety policy decisions? → A: Option A (Data Completeness + Signal Concordance: Confidence score [0.0–1.0] computed from telemetry freshness <15s old, sample density >= 90%, and directional agreement across at least 2 independent signals).
- Q: How should the Command Center UI surface the Vertex AI Agent Runtime and real Grafana MCP tool executions to operators and judges? → A: Option A (Unified Runtime Ledger with Expandable Tool Payloads: Chronological execution cards tagged by runtime origin [Vertex AI Agent Engine, Grafana MCP, Safety Policy], with one-click expansion to inspect exact PromQL queries, latencies, and sanitized result payloads).
- Q: Which Grafana MCP telemetry source is authoritative for the deterministic risk score calculation when metric time series and log streams diverge? → A: Grafana usage prioritized: Prometheus metrics via Grafana MCP drive deterministic risk calculation, while Loki log queries and Grafana alert evaluations via Grafana MCP provide authoritative diagnostic corroboration and failure mode classification.
- Q: How should the Incident Commander transfer operational context from the predictive session to the reactive workflow when leading signals fail to prevent degradation? → A: Option A (Seamless Context Inheritance: When playback errors exceed 2.0%, the Incident Commander escalates to reactive response [TRIGGERED → INVESTIGATING], directly transferring pre-collected Grafana metrics, logs, and root-cause hypotheses into the reactive incident record).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autonomous Proactive Prevention of Transcoder Saturation (Priority: P1)

Broadcast operations directors and site reliability engineers monitoring a marquee live streaming event need the system to detect early saturation indicators (such as upward trending GPU pressure and queue latency) and automatically execute a pre-authorized capacity expansion before viewer-visible stream stuttering occurs.

**Why this priority**: Delivering end-to-end autonomous prevention before customer impact is the core value proposition of the "Predict → Prevent → Prove" model.

**Independent Test**: Can be fully tested in isolation by sending telemetry exhibiting accelerating transcoder utilization into the monitoring loop. When the deterministic risk score exceeds 0.80 and confidence exceeds 0.85 with low blast radius (<= 20%), the system automatically scales the transcoder pool, brings utilization down to safe operational baselines, and verifies stream continuity without human intervention.

**Acceptance Scenarios**:

1. **Given** a live media stream running in `HEALTHY` operating state, **When** telemetry indicates rising GPU pressure (>85%), increasing queue depth, and rising segment fetch latency over a 5-minute sampling window, **Then** the system transitions to `RISK_DETECTED` and `PREDICTING`, executes a deterministic risk calculation, and classifies the condition as `HIGH RISK` or `IMMINENT RISK` with a 5–15 minute failure horizon.
2. **Given** a calculated risk score >= 0.80, model confidence >= 0.85, blast radius <= 20%, and an allowlisted action (`scale_transcoder_pool`), **When** safety policy evaluation executes, **Then** the Safety Director automatically approves the action (`AUTO PREVENT`), executes the controlled capacity scaling, and transitions to `PREVENTIVE_REMEDIATION`.
3. **Given** successful execution of the preventive scaling, **When** the post-action verification window elapses, **Then** independent telemetry comparison confirms GPU saturation drop below 65%, queue stabilization, and risk score reduction below 25, transitioning the state to `PREVENTED` with zero customer playback degradation.

---

### User Story 2 - Governed Preventive Remediation with Human Approval (Priority: P2)

When an emerging failure pattern requires a higher-impact preventive action (e.g., regional traffic shift exceeding 20% blast radius, or an action with moderate confidence), operations engineers must receive an unambiguous prediction briefing, economics trade-off, and an interactive one-click approval gate to authorize or reject the preventive measure.

**Why this priority**: Enterprise safety and governance mandate that non-trivial blast radius actions remain human-gated while providing complete situational clarity.

**Independent Test**: Trigger an emerging bottleneck scenario where the proposed remediation is a regional traffic reroute affecting 30% of traffic. The system must halt at `WAITING_HUMAN_APPROVAL`, display the expected loss without action vs. cost of prevention, and execute only upon explicit operator confirmation.

**Acceptance Scenarios**:

1. **Given** a predicted risk score of 0.85 but a proposed preventive traffic reroute affecting >20% blast radius, **When** safety policy evaluation completes, **Then** the system transitions to `WAITING_HUMAN_APPROVAL`, disables autonomous execution, and presents an interactive decision modal detailing predicted exposure ($46,000) versus prevention cost ($340).
2. **Given** a pending preventive approval modal, **When** the operator clicks "Authorize Preventive Action", **Then** the system immediately transitions to `PREVENTIVE_REMEDIATION`, dispatches the action through the approved infrastructure adapter, and commences verification.
3. **Given** a pending preventive approval modal, **When** the operator rejects or ignores the recommendation and stream degradation actually begins, **Then** the system automatically transitions to `ESCALATED` and seamlessly transfers control to the reactive incident workflow (`TRIGGERED` → `INVESTIGATING`).

---

### User Story 3 - Independent Post-Prevention Verification and Counterfactual Accounting (Priority: P3)

Following any preventive action, operations leadership needs auditable proof that the intervention genuinely averted degradation, including before-and-after telemetry differentials and estimated counterfactual business impact (viewers protected and exposure avoided).

**Why this priority**: Proving that an incident was averted—when no customer-visible outage occurred—is essential for executive trust, compliance reporting, and continuous learning.

**Independent Test**: After a preventive action completes, verify that the Verification Agent queries fresh telemetry independently, computes numerical delta baselines, persists the verified fingerprint to memory, and displays the avoided loss without claiming absolute certainty.

**Acceptance Scenarios**:

1. **Given** completion of a preventive action, **When** independent verification queries post-action telemetry, **Then** the system generates a side-by-side comparison (e.g., GPU 93% → 61%, queue growth +38%/min → +2%/min, risk score 87 → 18, playback errors 0.6% → 0.4%) and outputs `PREVENTION VERIFIED`.
2. **Given** a verified prevention, **When** the business summary is presented, **Then** the interface displays "Projected incident risk reduced from 87 to 18", along with explicitly labeled estimates of protected viewers and avoided commercial exposure ($45,660 net avoided loss).
3. **Given** a successful verified prevention, **When** the event completes, **Then** the system indexes the operational fingerprint (service, signature signals, and successful preventive action) into persistent memory for future predictive matching.

---

### User Story 4 - Seamless Fallback from Predictive Watch to Reactive Incident Management (Priority: P4)

In scenarios where leading signals do not provide sufficient lead time, or an unpredicted sudden failure occurs, the operations team must experience a seamless transition from Predictive Monitoring to Reactive Incident Director mode without lost state or conflicting agent decisions.

**Why this priority**: Guarantees system resilience; predictive capabilities augment the existing reactive engine without creating single points of failure.

**Independent Test**: Toggle between "Predictive Mode" and "Reactive Mode" on the primary dashboard, and inject a sudden catastrophic encoder failure while in predictive mode to verify automatic escalation into reactive incident resolution.

**Acceptance Scenarios**:

1. **Given** the system is in `MONITORING` or `WATCH` mode, **When** playback error rates abruptly surge past critical thresholds (>2.0%) before predictive thresholds trigger, **Then** the Incident Commander immediately bypasses predictive stages, flags `INCIDENT_CONFIRMED`, and activates the reactive multi-agent incident response.
2. **Given** an operator navigating the unified Command Center, **When** selecting the dashboard mode toggle, **Then** the UI cleanly switches between the "Predictive Operations" dashboard and the traditional "Reactive Incident Director" view while preserving live background telemetry feeds.

---

### Edge Cases

- **Flapping / Noisy Signals**: What happens when leading indicators spike momentarily (e.g., transient network glitch) and drop back down within 10 seconds? The predictive risk engine MUST require a sustained moving average window (minimum 3 consecutive evaluation cycles or 45 seconds) before promoting state beyond `WATCH`.
- **Preventive Action Ineffectiveness**: What happens if the preventive action executes (e.g., scaling instances) but cloud provider capacity is unavailable or delayed, and risk continues to climb? The Verification Agent MUST detect non-recovery within the verification timeout (90 seconds), mark the intervention as `PREVENTION_FAILED`, and immediately escalate to the reactive incident workflow.
- **Concurrent Degradation**: What happens if an unrelated subsystem (e.g., CDN origin routing) experiences sudden failure while a transcoder scaling preventive action is in flight? The Incident Commander MUST prioritize active service-impacting degradation over pending predictive optimizations, maintaining safety and service continuity.
- **Telemetry Query Failure**: How does the predictive engine behave if the external telemetry provider (Grafana MCP) becomes temporarily unreachable? The system MUST fall back to local high-fidelity metric synthesis, notify operators via a degraded-mode indicator, and refrain from auto-executing preventive actions under unverified telemetry conditions.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Predictive Ingestion & Risk Scoring
- **FR-001**: System MUST continuously ingest operational telemetry signals relevant to live media delivery, including GPU utilization, queue depth, transcoder latency, playback error rate growth, viewer growth rate, regional saturation, and recent deployment recency.
- **FR-002**: System MUST compute a deterministic, weighted predictive risk score (scale 0.0 to 1.0) using normalized input signals and configurable weights, exposing the exact contributing mathematical factors in the API payload and persistent record. Static gauge metrics (GPU utilization, latency, regional saturation) MUST be normalized via SLO min-max clamping $[0.0, 1.0]$ against operational SLO baselines (e.g., GPU 50%–95%, latency 150ms–500ms). Rate-of-change signals (queue depth growth, playback error rate acceleration) MUST be calculated as a linear regression slope over a 60-second sliding sample window and normalized into $[0.0, 1.0]$.
- **FR-003**: System MUST classify the operational state into distinct risk tiers: `HEALTHY` (score < 0.30), `WATCH` (0.30–0.59), `ELEVATED RISK` (0.60–0.79), `HIGH RISK` (0.80–0.89), and `IMMINENT RISK` (>= 0.90).
- **FR-004**: Predictions MUST estimate an actionable short-term failure horizon window (5 to 15 minutes) and express predictive outputs probabilistically (e.g., "High probability of degradation within 7–12 minutes") without claiming absolute certainty.
- **FR-005**: All operational telemetry used in predictive evaluations MUST prioritize real Grafana MCP queries: Prometheus time series queries (`query_prometheus_metrics`) provide authoritative numerical telemetry for mathematical risk scoring, while Loki log streams (`search_loki_logs`) and active alert evaluations (`list_grafana_alerts`) provide authoritative qualitative diagnostic evidence. The system MUST forbid artificial or hallucinated telemetry numbers.

#### Multi-Agent Workflow & Roles
- **FR-006**: System MUST incorporate a dedicated Predictive Risk Agent managed hierarchically by the Incident Commander, responsible for querying operational telemetry, executing risk models, and synthesizing structured prediction assessments.
- **FR-007**: Business Impact Agent MUST quantify prevention economics by calculating `expected_loss_without_action`, `cost_of_prevention`, and `expected_value_of_prevention` (`expected_loss_without_action - cost_of_prevention`).
- **FR-008**: Gemini reasoning components MUST interpret structured telemetry evidence and risk model outputs to produce concise, non-technical explanations and failure hypotheses without exposing internal chain-of-thought tokens.
- **FR-009**: Remediation Agent MUST support allowlisted preventive actions: `scale_transcoder_pool`, `shift_selected_traffic`, `increase_regional_capacity`, `prewarm_media_cache`, and `apply_traffic_rate_limit`. Unlisted or arbitrary infrastructure mutations MUST be strictly rejected.

#### Safety Governance & Policy
- **FR-010**: Safety Director MUST deterministically evaluate proposed preventive actions against four mandatory criteria: risk score threshold (>= 0.80), model confidence (>= 0.85), blast radius limit (<= 20%), and explicit allowlist membership. Confidence MUST be computed independently from risk score based on telemetry freshness (< 15 seconds old), sample completeness (>= 90% expected samples received), and directional concordance across at least 2 independent leading signals.
- **FR-011**: When all four safety criteria are satisfied, the system MUST permit autonomous execution (`AUTO PREVENT`); otherwise, the system MUST halt and demand human operator approval (`WAITING_HUMAN_APPROVAL`).
- **FR-012**: System MUST provide an interactive approval mechanism in the Command Center UI, allowing operators to review the prediction briefing, economic trade-off, and one-click authorization or rejection.

#### Independent Verification & Persistent Memory
- **FR-013**: Verification Agent MUST perform an independent post-action telemetry audit, comparing pre-prevention baseline metrics against post-prevention telemetry to confirm that risk has declined below acceptable operational thresholds (risk score < 0.25).
- **FR-014**: System MUST store complete historical audit records in persistent storage (PostgreSQL/durable database), including query source, raw telemetry values, normalized scores, contributor weights, risk scores, agent decisions, approval records, and verification deltas.
- **FR-015**: System MUST record successful preventive intervention fingerprints (service identifier, leading signal signature, and verified action) in durable memory to expedite future predictive matching.

#### User Interface & Experience
- **FR-016**: Command Center MUST offer a primary "Predictive Operations" dashboard mode featuring real-time risk score gauges, trend trajectory, contributing signal breakdowns, failure time horizon, and economic impact metrics.
- **FR-017**: Command Center MUST provide an interactive mode toggle between "Predictive Mode" and "Reactive Mode" to demonstrate dual-mode operational continuity. When customer-visible degradation breaches thresholds (playback error rate > 2.0%) or an operator rejects prevention, the system MUST execute seamless context inheritance: automatically transitioning the Incident Commander to reactive mode (`TRIGGERED` → `INVESTIGATING`) and carrying over all prior Grafana telemetry, calculated risk factors, and candidate root-cause hypotheses directly into the reactive incident record to accelerate MTTR.
- **FR-018**: 3D Event Graph MUST visually communicate risk progression by rendering node stress color shifts (green → amber → red), animated risk paths (Telemetry → Predicted Failure → Preventive Action → Verified Safe), and recovery state transitions.
- **FR-019**: UI MUST feature a Unified Agent Runtime & Tool Trace Ledger displaying real-time execution cards distinctly tagged by runtime origin (`[Vertex AI Agent Engine]`, `[Grafana MCP]`, `[Safety Policy]`, `[FastAPI Core]`). Each card MUST support one-click expansion to inspect exact PromQL/Loki query parameters, execution latency, and sanitized result payloads without exposing secret credentials or authentication tokens.
- **FR-020**: UI MUST present counterfactual impact reporting clearly labeled as estimates (e.g., "Estimated Viewers Protected: 1.2M", "Estimated Exposure Avoided: $45,660").

---

### Key Entities

- **PredictiveSignalSnapshot**: Ingested and normalized point-in-time metrics representing operational pressure (GPU utilization, queue depth, transcode latency, error rate acceleration, concurrency growth, regional load, deployment risk).
- **PredictiveRiskAssessment**: The evaluated risk object containing the composite `risk_score`, `risk_level`, `predicted_failure_mode`, `estimated_window_minutes`, individual signal contributor breakdown, and calculation metadata.
- **PreventionProposal**: Action recommendation produced by the Predictive Risk and Business Impact agents, specifying the proposed action, target service, blast radius, expected loss without action, cost of prevention, and net avoided exposure.
- **PreventivePolicyDecision**: Deterministic verdict produced by the Safety Director (`AUTO_EXECUTE`, `REQUIRE_APPROVAL`, `REJECTED`), accompanied by explicit policy evaluation reasoning.
- **PreventiveActionExecution**: Immutable execution record capturing action dispatch timestamp, target environment, execution parameters, dispatch adapter status, and operator approval identity (if manual).
- **VerificationOutcome**: Independent before-and-after assessment detailing baseline telemetry vs. post-action telemetry, risk delta, verification verdict (`PREVENTION_VERIFIED` or `PREVENTION_FAILED`), and counterfactual metrics.
- **PredictiveMemoryFingerprint**: Durable signature capturing service context, primary leading indicators, and the proven preventive action for pattern recall during future operations.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Leading operational risk is detected and classified at least 5 minutes prior to customer-visible playback degradation in simulated high-load scenarios.
- **SC-002**: Automated preventive remediation executes and achieves verified risk reduction in under 90 seconds from policy approval.
- **SC-003**: 100% of preventive actions with blast radius > 20% or confidence < 85% successfully halt at human approval gates without unauthorized execution.
- **SC-004**: Post-intervention verification independently confirms GPU saturation drops by at least 25 percentage points and risk score declines below 25/100.
- **SC-005**: All displayed predictive metrics, weights, and economic valuations are mathematically traceable to stored database records with zero hallucinated numerical outputs.
- **SC-006**: Operators can switch between Predictive and Reactive dashboard modes in under 500 milliseconds without losing operational telemetry continuity.
- **SC-007**: 100% of predictive events, tool invocations, and policy evaluations are durably logged to the persistent database.
- **SC-008**: In edge-case failures where prevention is withheld or rejected, the system transitions to the reactive incident workflow in under 3 seconds after degradation threshold breach.

---

## Assumptions

- **Telemetry Polling Cadence**: Operational telemetry is sampled or pushed at a minimum cadence of 5 to 10 seconds, providing sufficient resolution for calculating short-term growth rates.
- **Action Latency**: Allowlisted infrastructure actions (e.g., transcoder pool expansion, DNS/traffic weight shift) can be signaled and begin taking effect within 30 to 60 seconds in the simulation/staging environment.
- **Cost Models**: Prevention cost estimates (e.g., compute cost of warming additional worker nodes) and customer exposure models are based on established enterprise media streaming benchmark averages.
- **Scope Boundary**: The predictive horizon is strictly focused on short-term operational windows (5–15 minutes); long-term seasonal forecasting (days/weeks) is out of scope for this feature.
- **Agent Architecture Alignment**: The feature leverages the existing Google Cloud Agent Engine / Vertex AI / Gemini runtime and Grafana MCP tool protocols ratified in the Studio Guardian Constitution.
