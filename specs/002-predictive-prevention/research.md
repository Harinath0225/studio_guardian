# Phase 0 Research: Predictive Prevention & Proactive Remediation

**Feature**: [`specs/002-predictive-prevention/spec.md`](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/002-predictive-prevention/spec.md)
**Status**: Completed

---

## 1. Feature Normalization & Deterministic Trend Model

### Context & Problem
We need to convert disparate raw telemetry dimensions (GPU percentages, latencies in milliseconds, queue depths in items, viewer concurrency in millions) into dimensionless $[0.0, 1.0]$ signals that feed a weighted linear risk formula, without resorting to black-box machine learning or statistical instability.

### Decision
Implement a pure Python deterministic normalizer (`backend/src/prediction/feature_normalizer.py`):
1. **Static Gauge Normalization**: Use an explicit SLO-bounded min-max clamp:
   $$\text{normalized}(x, \text{floor}, \text{ceil}) = \min\left(1.0, \max\left(0.0, \frac{x - \text{floor}}{\text{ceil} - \text{floor}}\right)\right)$$
   - GPU utilization: floor 50%, ceiling 95%
   - Transcoder latency: floor 150ms, ceiling 500ms
   - Regional saturation: floor 60%, ceiling 95%
2. **Velocity & Acceleration (Rate of Change)**: Maintain a 60-second in-memory ring buffer (6 samples at 10s intervals). Calculate the linear regression slope $\beta$:
   $$\beta = \frac{\sum (t_i - \bar{t})(y_i - \bar{y})}{\sum (t_i - \bar{t})^2}$$
   Normalize positive slope against maximum acceptable velocity (e.g., queue growth $> 50\text{ items/min} \to 1.0$, error growth $> 0.5\%/\text{min} \to 1.0$). Negative slopes clamp to $0.0$.
3. **Deterministic Time-to-Threshold Window**:
   $$\text{time\_to\_threshold} = \frac{\text{critical\_threshold} - \text{current\_value}}{\text{positive\_rate}}$$
   Compute a min/max confidence interval:
   $$\text{window\_min} = \max\left(3, \lfloor\text{time\_to\_threshold} \times 0.8\rfloor\right)$$
   $$\text{window\_max} = \max\left(\text{window\_min} + 2, \lceil\text{time\_to\_threshold} \times 1.2\rceil\right)$$
   Bound the output to a 5–15 minute horizon.

### Alternatives Considered
- *Holt-Winters Exponential Smoothing*: Rejected due to parameter sensitivity and overshoot on sudden bursty traffic.
- *ARIMA / Prophet Forecasting*: Rejected due to high computational latency, heavy C-extensions, and lack of explainability.
- *Instantaneous Thresholds Only*: Rejected because it ignores velocity, triggering late or false-alarming on momentary blips.

---

## 2. Vertex AI Agent Engine & Google Cloud ADK Runtime Pattern

### Context & Problem
The architecture must genuinely run within Google Cloud's Agent Engine / Google GenAI SDK framework, exposing real runtime session identifiers, specialist execution states, and token metrics to the UI without fabricating identifiers or violating the Constitution (Principle 4: "Google Cloud is Part of the Real Runtime").

### Decision
1. **Google GenAI SDK Integration**: Leverage the existing `GoogleGenAIClient` running with `genai.Client(vertexai=True, project=..., location=...)` configured in `src/integrations/google_genai.py`.
2. **Runtime Execution Envelope**: Each agent invocation generates a traceable execution frame:
   - `runtime_type`: `"Vertex AI Agent Engine (gemini-2.5-flash)"`
   - `session_id`: Deterministic run ID `sg-pred-<timestamp>-<uuid4_short>`
   - `agent_role`: `"Predictive Risk Agent"`
   - `system_instruction`: Structured domain boundaries enforcing media SRE role
   - `response_schema`: Pydantic structured schema with `_strip_additional_properties`
3. **Gemini Responsibility Boundary**:
   - **Allowed**: Evidence correlation, failure hypothesis formulation, natural language risk synthesis, mitigation strategy comparison, and uncertainty calibration.
   - **Strictly Forbidden**: Raw mathematical risk calculation, financial cost/exposure arithmetic, authorization logic, and direct infrastructure mutation.

### Alternatives Considered
- *Unstructured LLM Free-Text Outputs*: Rejected because deterministic state machines require strict schema validation (`Pydantic`).
- *Direct Model Function Calling for Infrastructure*: Rejected by Constitution Principle 10 ("Safety By Design"); all mutations must pass through the deterministic Python `SafetyDirector`.

---

## 3. Grafana MCP Telemetry Query Architecture

### Context & Problem
The Predictive Risk Agent must query real telemetry through the Model Context Protocol (MCP) server across Prometheus metrics and Loki logs, maintaining transparent fallback to high-fidelity mock data when Docker/network is unavailable.

### Decision
1. **Authoritative Metric Mapping**:
   - `media_transcode_rendition_error_rate`: GPU error rate and hardware allocation failure
   - `media_origin_segment_fetch_latency_ms`: Ingest & origin fetch latency
   - `media_playback_buffer_ratio`: Client buffer health
   - `media_stream_active_viewers`: Concurrency count
2. **MCP Tool Invocation Pipeline**:
   - Invokes `query_prometheus_metrics(query="avg(media_transcode_rendition_error_rate)...")`
   - Invokes `search_loki_logs(query='{service="transcoder"} |= "dropped frame"', limit=10)`
   - Invokes `list_grafana_alerts()`
3. **Traceability Logging**: Record each query's exact PromQL/LogQL expression, latency (ms), timestamp, and sanitized result into the `prediction_evidence` table.
4. **Provider Transparency**: The runtime explicitly emits whether the data source was `LIVE_GRAFANA_MCP` or `MOCK_GRAFANA_MCP` in both API responses and SSE event streams.

### Alternatives Considered
- *Direct Prometheus HTTP REST API*: Rejected because hackathon track requires demonstrating real Grafana MCP integration.
- *Background Polling without On-Demand Tool Calls*: Rejected because agents must autonomously invoke tools via JSON-RPC.

---

## 4. Database Persistence & Traceability Schema

### Context & Problem
The system of record (PostgreSQL / SQLite fallback) must capture the complete end-to-end audit chain from initial telemetry poll through prediction, decision, execution, and verification.

### Decision
Define six specialized relational tables with foreign-key relationships:
1. `predictive_snapshots`: Raw and normalized telemetry vector, sliding-window slope values.
2. `prediction_evidence`: Tool query expressions, raw payloads, and execution latency from Grafana MCP.
3. `prediction_decisions`: Composite risk score, contributor weights, Gemini hypothesis, confidence factors, and failure window.
4. `prevention_actions`: Proposed vs. approved action, blast radius, economics (loss without action vs. cost), operator ID, dispatch status.
5. `prevention_verifications`: Before vs. after telemetry deltas, verification verdict, and counterfactual avoided loss.
6. `prediction_fingerprints`: Indexed service, signal signature, and proven preventive action for memory recall.

### Alternatives Considered
- *Single Large JSON Blob*: Rejected because relational queries, historical indexing, and metric diffing require indexed columns.
- *In-Memory Only State*: Rejected by Constitution Principle 11 ("Persistent System of Record").

---

## 5. Frontend & 3D Visualization Architecture

### Context & Problem
The Command Center must offer a dual-mode operations dashboard (Predictive vs. Reactive) with animated risk progression and a 3D topology that visualizes risk stress before failure occurs.

### Decision
1. **Mode State Machine**: Global UI state enum `DashboardMode: "PREDICTIVE" | "REACTIVE"`.
   - In Predictive mode: Displays the **Predictive Operations** view (Risk Gauge, Trajectory Chart, Signal Contributors, Prevention Economics, Unified Runtime Ledger).
   - In Reactive mode: Displays the traditional **Incident Director** view (Incident Timeline, Diagnostics, Remediation).
   - Instant toggle (<500ms) with zero background SSE event loss.
2. **Unified Agent Runtime & Tool Trace Ledger**:
   - Timeline cards tagged `[Vertex AI Agent Engine]`, `[Grafana MCP]`, `[Safety Policy]`, `[FastAPI Core]`.
   - Collapsible drawer for viewing exact PromQL queries and sanitized response JSON.
3. **3D Topology Dynamic State**:
   - When risk increases (0.60–0.89): Transcoder node pulses amber (`#f59e0b`).
   - When risk reaches IMMINENT (>= 0.90): Node pulses high-frequency red/coral (`#ef4444`).
   - When preventive scaling executes: Scaling particles burst outward and node radius increases by 40% (visualizing pool capacity expansion).
   - When verified: Node transitions smoothly back to calm emerald green (`#10b981`).

---

## 6. Verification & Avoided-Impact Economics

### Context & Problem
Preventive actions averting incidents cannot claim absolute certainty. The system must formulate economic and operational savings transparently as probabilistic models.

### Decision
1. **Deterministic Economic Formulation**:
   $$\text{expected\_loss\_without\_action} = \text{active\_viewers} \times \text{projected\_churn\_rate} \times \text{customer\_LTV\_exposure}$$
   $$\text{cost\_of\_prevention} = \text{additional\_workers} \times \text{hourly\_rate} \times \text{provisioning\_duration}$$
   $$\text{expected\_avoided\_exposure} = \text{expected\_loss\_without\_action} - \text{cost\_of\_prevention}$$
2. **Verification Gate**:
   - Query Grafana MCP 30 seconds and 60 seconds post-scaling.
   - Requirement: $\Delta \text{GPU} \le -25\%$ AND $\text{risk\_after} < 0.25$ AND $\text{error\_rate} < 0.5\%$.
   - Output explicitly stamped: `PREVENTION VERIFIED` or `PREVENTION FAILED`.
   - UI display: "Projected incident risk reduced from 87 to 18 after intervention (Estimated exposure avoided: $45,660)."
