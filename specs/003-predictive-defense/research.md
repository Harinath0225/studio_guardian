# Research: Predictive Media Protection & Black Swan Defense

**Feature**: Predictive Media Protection & Black Swan Defense  
**Branch**: `003-predictive-defense`  
**Date**: 2026-09-08  
**Status**: Completed  

---

## 1. Vertex AI Agent Architecture & Agent Engine Runtime

### Decision
Implement the agent runtime using Google Cloud **Vertex AI Agent Engine** integrated through the modern **Google GenAI SDK** (`google-genai` SDK with `vertexai=True`, `project`, and `location`). 
The agent orchestration follows a hierarchical multi-agent delegation model:
- **Root Incident Commander** acts as the primary orchestrator for incident sessions and predictive escalations.
- **Specialist Agents** (Predictive Risk Agent, Observability Investigator, Business Impact Agent, Ad Integrity Agent, Perceptual Quality Sentinel, Remediation Agent, Verification Agent) are invoked by the Commander or run autonomously in periodic assessment cycles.
- Session state is managed via Vertex AI session contexts and persisted execution frames containing timestamps, stage indicators, session IDs, and tool execution traces.
- The **Safety Director** remains a deterministic application policy engine outside the LLM reasoning loop to enforce hard boundaries.

### Rationale
- Complies strictly with Constitution Principle 1 ("Vertex AI is the Agent Runtime") and Principle 18 ("Hackathon Compliance").
- Provides genuine Google Cloud agent runtime integration where agent identity, session identifiers, tool calls, and state transitions are authentic and exposed via the UI.
- Prevents the architecture from degenerating into a naive FastAPI backend with generic LLM chat calls.
- Preserves deterministic safety by ensuring all mutation proposals must pass through the deterministic Safety Director before execution.

### Alternatives Considered
- *Custom LangChain / CrewAI multi-agent framework*: Rejected because it introduces external dependencies, fails to utilize the official Google Cloud Vertex AI Agent platform, and violates the requirement for Google Cloud hackathon compliance.
- *Decoupled Agent Microservices (one container per agent)*: Rejected per explicit architectural principle: "Keep a modular monolith for the application backend. Do NOT create one deployable microservice per agent."

---

## 2. Grafana MCP Transport, Tool Allowlists & Evidence Persistence

### Decision
- **Transport**: `streamable-http` on endpoint `http://localhost:8001/mcp` with standard JSON-RPC 2.0 and session management via `Mcp-Session-Id` header.
- **Authentication**: Unauthenticated for local Docker container (`USE_MOCK_GRAFANA_MCP=true` or local container); Bearer token via `GRAFANA_SERVICE_ACCOUNT_TOKEN` for managed Grafana Cloud instances.
- **Tool Allowlists**:
  - *Predictive Tools*: `query_prometheus` (metrics), `query_loki_logs` (leading warning logs), historical fingerprint lookups.
  - *Reactive Tools*: `query_prometheus` (degradation metrics), `query_loki_logs` (stack traces), `alerting_manage_rules` (active firing alerts), `tempo_get-trace` (distributed span latency).
  - *Verification Tools*: Fresh execution of `query_prometheus`, `query_loki_logs`, and `tempo_get-trace` to verify stabilization.
- **Evidence Persistence**: Every tool invocation records an entry in `runtime_evidence` / `prediction_evidence` containing `tool_name`, `query_metadata`, `timestamp`, `raw_result` (JSON), `datasource`, `agent`, and `incident_id` (or `snapshot_id`). Credentials and tokens are stripped prior to storage.

### Rationale
- Conforms to Model Context Protocol (MCP) standard specification and official Grafana MCP server capabilities.
- Transparent fallback to mock Grafana MCP ensures deterministic local development and flawless offline gameday demonstrations without external network fragility.
- Audit logging of raw tool responses guarantees mathematical provenance and evidentiary transparency.

### Alternatives Considered
- *Direct Prometheus/Loki REST API calls bypassing MCP*: Rejected because Grafana MCP is the non-negotiable partner track integration and operational source of truth.
- *Stdio MCP Transport*: Rejected because streamable-http allows persistent background server execution, shared connections across agents, and easier health monitoring.

---

## 3. Telemetry Pipeline & Realistic Media Simulator

### Decision
Extend `MediaEnvironment` and `MetricsGenerator` in `backend/src/simulator/` to generate multi-dimensional live broadcast telemetry reflecting real-world streaming infrastructure:
- **Transcoder Metrics**: `gpu_utilization_pct`, `transcoder_latency_ms`, `queue_depth`, `gpu_allocation_failure_pct`.
- **Playback Metrics**: `playback_error_rate_pct`, `rebuffer_ratio_pct`, `bitrate_kbps`.
- **Audience Metrics**: `concurrent_viewers`, `regional_saturation_pct` across AU, SG, IN, US.
- **SCTE-35 Ad Metrics**: `scte_timing_drift_ms`, `splice_alignment_error_ms`, `ad_pod_drop_pct`.
- **Perceptual Quality Metrics**: `av_sync_drift_ms`, `loudness_deviation_lufs`, `frame_drop_ratio_pct`, `black_frame_ratio_pct`.
- Telemetry is exposed to Prometheus (`/metrics` or Grafana MCP queries) and changes deterministically across defined scenario steps.

### Rationale
- High-concurrency live sports broadcasts fail in compound ways: hardware bottlenecks lead to queuing, which leads to manifest segment delivery delay, which causes player-side buffer underrun.
- Media-specific indicators (SCTE-35 drift, AV sync offset) can degrade even when server CPU is normal, validating Constitution Principle 8 ("Semantic Media Quality").

### Alternatives Considered
- *Random stochastic metric generator*: Rejected because non-deterministic metrics make automated testing and gameday live demonstrations unreliable.

---

## 4. Deterministic Predictive Engine

### Decision
Structure the predictive engine under `backend/src/prediction/`:
- `normalizer.py`: Clamps multi-sensor metrics into dimensionless `[0.0, 1.0]` features using operational SLO baselines.
- `features.py`: Computes derived features, baseline deviations, and interaction terms.
- `trend.py`: Computes 60-second sliding regression velocity (`dy/dt`) and 2nd derivative acceleration (`d²y/dt²`).
- `thresholds.py`: Defines risk tiers (`HEALTHY`, `WATCH`, `ELEVATED_RISK`, `HIGH_RISK`, `IMMINENT_RISK`) and auto-remediation triggers.
- `risk_model.py`: Calculates weighted composite risk score (`0.25*GPU + 0.20*Queue + 0.20*Latency + 0.15*Error + 0.10*Viewer + 0.10*Deploy`) with compound saturation boosting.
- `provenance.py`: Generates mathematical lineage records tracking every raw input, formula, coefficient, and intermediate value.

### Rationale
- Fulfills Constitution Principle 4 ("Mathematically Traceable Data").
- Ensures complete transparency: operators and judges can inspect the formula and reproduction steps without any AI hallucinations.

### Alternatives Considered
- *Black-box ML Regressor (XGBoost / LSTM)*: Rejected per explicit constraint ("No custom ML training, no new ML infrastructure"). Deterministic mathematical models provide instant auditability and zero training overhead.

---

## 5. Media Specialist Engines: Ad Integrity & Perceptual Quality

### Decision
Create dedicated deterministic analysis modules under `backend/src/media/`:
- `ad_integrity.py`:
  - Analyzes SCTE-35 cue timing drift against configured operational tolerance (e.g., nominal 0ms, tolerance ±200ms, critical >500ms).
  - Evaluates splice alignment, ad pod duration mismatch, and tracking beacon error ratio.
  - Outputs deterministic risk indicators to `ad_integrity_events`.
- `perceptual_quality.py`:
  - Evaluates AV sync offset (nominal ±25ms, warning >100ms, critical >250ms).
  - Evaluates audio loudness deviation against target -24 LUFS / LKFS (tolerance ±2.0 LUFS, critical >4.0 LUFS).
  - Evaluates video dropped frame ratio (nominal <0.5%, warning >2.0%, critical >5.0%) and black frame percentage (critical >1.5%).
  - Outputs deterministic signals to `media_quality_events`.
- Gemini reasoning agents receive these structured metrics and generate operational summaries without inventing values.

### Rationale
- Fulfills Constitution Principle 9 ("Ad Integrity Is Business Critical") and Principle 10 ("Perceptual Quality is a Signal, Not a Full QC System").
- Bounds perceptual QC to a lightweight, measurable set of signals, preventing scope creep.

### Alternatives Considered
- *Integrating full FFmpeg deep-packet inspection or video AI CV models*: Rejected as overkill for this demo and contrary to hackathon delivery scope.

---

## 6. Business Impact & Counterfactual ROI Engine

### Decision
Implement `backend/src/business/impact_model.py`:
- **Disrupted Viewers**: `total_viewers * (playback_error_rate / 100) * regional_weight`.
- **Ad Exposure**: `(disrupted_viewers * (ads_per_hour * hours_exposed) / 1000) * cpm_usd`.
- **SLA Exposure**: Tiered penalties based on duration and error severity exceeding contract thresholds.
- **Preventive Cost**: `nodes_scaled * hourly_node_cost * estimated_duration_hours`.
- **Expected Avoided Exposure**: `max(0, expected_loss_without_intervention - expected_loss_after_intervention - cost_of_prevention)`.
- All proactive values are labeled as `ESTIMATED` with formula versioning (e.g., `v2.1-cricket-cpm28.50`).

### Rationale
- Fulfills Constitution Principle 12 ("Business Value Must Be Calculable") and Principle 14 ("Counterfactual Honesty").
- Distinguishes between what was actually observed during an outage versus what was avoided via proactive intervention.

### Alternatives Considered
- *Unbounded estimation with generative LLM numbers*: Rejected because LLMs hallucinate financial metrics, violating auditability requirements.

---

## 7. Safety Director Policy Engine

### Decision
Implement deterministic policy rules in `backend/src/policy/`:
- **Auto-Prevent Policy**:
  - `risk_score >= 0.80`
  - `confidence >= 0.85`
  - `blast_radius <= 0.20` (20%)
  - `action in ["scale_transcoder_pool", "switch_packager_backup", "activate_ad_slate"]`
  - `circuit_breaker == CLOSED`
  - → Action verdict: `AUTO_EXECUTE`
- Otherwise: Action verdict: `REQUIRES_HUMAN_APPROVAL`.
- All decisions are recorded in `prevention_actions` and audit logs.

### Rationale
- Fulfills Constitution Principle 11 ("Safety Before Autonomy").
- AI recommends candidate actions, but deterministic code determines whether the system is authorized to act automatically.

---

## 8. Remediation Fabric & Verification Pipeline

### Decision
- **Remediation Fabric**: Controlled, allowlisted operations exposed via `VideoRoutingProxy` and `MediaEnvironment`:
  1. `scale_transcoder_pool`: Increases worker pool nodes (e.g., from 8 to 16) to absorb queue and GPU saturation.
  2. `shift_traffic`: Diverts regional traffic from failing cluster to warm standby.
  3. `activate_ad_slate`: Injects emergency backup slate upon SCTE-35 corruption to avoid dead air.
  4. `switch_packager`: Diverts origin packaging to redundant packager instance.
  - No arbitrary shell commands or untyped mutations.
- **Verification Pipeline**:
  - After dispatching remediation, wait a configured stabilization delay (5–10s simulation / 30s real).
  - Re-query Grafana MCP for fresh metrics (`gpu_utilization_pct`, `queue_depth`, `playback_error_rate_pct`, SCTE timing).
  - Recalculate risk score and delta.
  - Classify outcome: `VERIFIED` (risk dropped to <0.40 and bottleneck resolved), `PARTIALLY_RECOVERED`, or `FAILED`.
  - Record verification evidence in `prevention_verifications` and `verification_results`.

### Rationale
- Fulfills Constitution Principle 15 ("Closed-Loop Proof").
- Proves that autonomous remediation actually fixed the problem using independent, fresh operational data.

---

## 9. Black Swan Gameday Engine

### Decision
Implement `backend/src/demo/scenarios.py`:
1. `TRANSCODER_SURGE`: Simulates massive 4K/HDR audience influx causing GPU to spike to 94% and queue depth to 48 while error rate remains low (leading indicator phase), escalating to full degradation if unaddressed.
2. `SCTE35_CORRUPTION`: Simulates ad cue timing drift (>350ms) and corrupt splice payloads, causing ad pod drop and revenue burn while infrastructure metrics remain green.
- Provides UI chaos buttons: "Inject Transcoder Surge", "Inject SCTE-35 Corruption", and "Reset Environment".

### Rationale
- Fulfills Constitution Principle 13 ("Black Swan Game Day") and Principle 17 ("Demo-First Priority").
- Allows evaluators, judges, and operators to demonstrate the entire lifecycle in under 90 seconds.

---

## 10. Frontend Architecture, 3D Graph & Evidence Transparency

### Decision
- **Four Operational Views**:
  1. **PREDICT**: Live composite risk gauge, 60s trend velocity, failure horizon countdown, signal contributor breakdown, and Grafana MCP telemetry charts.
  2. **PROTECT**: Candidate preventive action, prevention cost vs. avoided exposure economics, Safety Director policy verdict, and one-click execution.
  3. **RESPOND**: Reactive incident workspace, root cause causal graph, remediation timeline, and BEFORE vs. AFTER verification diffs.
  4. **GAME DAY**: Deterministic chaos panel to trigger Black Swan scenarios and observe the live cascade.
- **Lightweight 3D System Graph** (`Canvas3D` with Three.js / React Three Fiber):
  - Nodes: Live Ingest, Transcoder Pool, Packager, Ad Decision Server (ADS), CDN Distribution, Regional Audiences, Specialist Agents, Grafana MCP, Vertex AI Runtime.
  - State Animations: Red pulse on bottlenecked nodes during stress; blue/cyan data particle flow during MCP queries; green pulse upon verified recovery.
- **Technical Evidence Panel**:
  - Displays real-time flow: `Vertex AI Runtime → Specialist Agent → Grafana MCP Tool → Raw Telemetry → Deterministic Engine → Gemini Reasoning`.
- **Data Provenance Drawer**:
  - Clicking any metric or risk score opens a slide-over showing source query, raw sensor value, timestamp, normalization formula, weights, and resulting contribution.

### Rationale
- Satisfies Constitution Principle 16 ("UX - Enterprise-Grade Broadcast Operations") and provides immediate visual proof of the system's autonomous capabilities.
