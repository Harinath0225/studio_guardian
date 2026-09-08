# Studio Guardian — System Architecture

**Autonomous Live Media Incident Director & Predictive Defense System**  
Built for the **Google Cloud & Grafana Labs Hackathon**

---

## 1. System Topology Overview

Studio Guardian operates as an autonomous, multi-agent operational supervisor designed specifically for high-stakes, large-scale live media broadcasts (World Cup finals, live sporting championships, global concert streams).

```mermaid
flowchart TD
    subgraph LiveMediaEnvironment ["Simulated Live Media Infrastructure"]
        VideoProxy["Regional Video Proxy (/route)"]
        TranscoderCluster["Primary Transcode Cluster (Sydney/Singapore)"]
        StandbyCluster["Warm Standby Cluster (US-West)"]
        ChaosEngine["Black Swan Chaos Engine (Surge / SCTE / Reset)"]
        
        VideoProxy --> TranscoderCluster
        VideoProxy -.->|Controlled Traffic Shift| StandbyCluster
        ChaosEngine -.->|Inject SCTE Drift / Load Spikes| TranscoderCluster
    end

    subgraph ObservabilityStack ["Telemetry & Observability Layer"]
        PrometheusExp["Prometheus Scrape Endpoint (/metrics)"]
        SSEStream["SSE Event & Loki Stream (/stream/events)"]
        LokiShipper["Grafana Cloud Loki Shipper (POST /loki/api/v1/push)"]
        GrafanaCloud["Grafana Cloud (whitepenguin2589.grafana.net)"]
        
        TranscoderCluster --> PrometheusExp
        TranscoderCluster --> SSEStream
        SSEStream --> LokiShipper
        LokiShipper -.->|Basic Auth glc_...| GrafanaCloud
    end

    subgraph MCPClientLayer ["Model Context Protocol (MCP)"]
        GrafanaMCP["Grafana MCP Client Adapter (Port 8001 / Mock)"]
        GrafanaMCP -->|query_prometheus| PrometheusExp
        GrafanaMCP -->|query_loki_logs| SSEStream
        GrafanaMCP -->|alerting_manage_rules| GrafanaCloud
    end

    subgraph AgentRuntime ["Google Cloud Multi-Agent Runtime"]
        IC["Incident Commander (Supervisor State Machine)"]
        PredAgent["Predictive Risk Agent (Leading Saturation Engine)"]
        SCTESentinel["SCTE-35 Ad Integrity Sentinel"]
        PerceptualSentinel["Perceptual Quality Sentinel"]
        ObsAgent["Observability Investigator Agent"]
        ImpactAgent["Business Impact Agent (Audience & Loss Models)"]
        SafetyDir["Safety Director (Deterministic Policy Engine)"]
        RemAgent["Remediation Agent (Traffic Shift & Pool Scaling)"]
        VerAgent["Verification Agent (Independent Telemetry Delta)"]

        IC --> PredAgent
        PredAgent -->|Continuous Risk & Hypotheses| IC
        IC --> SCTESentinel
        IC --> PerceptualSentinel
        IC --> ObsAgent
        ObsAgent -->|Reactive Evidence & Root Cause| IC
        IC --> ImpactAgent
        ImpactAgent -->|Audience & Prevention Economics| IC
        IC --> SafetyDir
        SafetyDir -->|AUTO_EXECUTE / APPROVAL| RemAgent
        RemAgent -->|Capacity Scale / Traffic Shift| VideoProxy
        IC --> VerAgent
        VerAgent -->|Independent Telemetry Verdict| IC
    end

    subgraph PersistenceAndDelivery ["Storage & Event Delivery"]
        Postgres[(PostgreSQL / SQLite Storage)]
        ProvenanceEngine["Mathematical Provenance Engine (/provenance)"]
        CommandCenter["5-View React Command Center"]

        IC --> Postgres
        IC --> ProvenanceEngine
        SSEStream --> CommandCenter
        ProvenanceEngine --> CommandCenter
    end

    PredAgent -.->|Leading Telemetry Queries| GrafanaMCP
    SCTESentinel -.->|SCTE Drift & Splice Checks| GrafanaMCP
    PerceptualSentinel -.->|Loudness & Lip-Sync Checks| GrafanaMCP
    ObsAgent -.->|Tools: query_metrics, search_logs, get_traces| GrafanaMCP
    VerAgent -.->|Independent Metric Sample| GrafanaMCP
```

---

## 2. Multi-Agent Boundaries & Responsibilities

The logical agent hierarchy consists of the **Incident Commander** supervising specialized functional agents, media sentinels, and a deterministic safety policy director:

```
Incident Commander (Supervisor)
├── Predictive Risk Agent (Leading Telemetry & Saturation Projection)
├── SCTE-35 Ad Integrity Sentinel (Ad Timing Drift & Splice Mismatch)
├── Perceptual Quality Sentinel (EBU R128 Loudness & Lip-Sync)
├── Observability Investigator (Root Cause Multi-Signal Correlation)
├── Business Impact Agent (Audience Blast, Ad Burn & Prevention Economics)
├── Safety Director (Deterministic Gating & 20% Blast Radius Ceiling)
├── Remediation Agent (Traffic Shift & Capacity Scaling)
└── Verification Agent (Independent Telemetry Delta Validation)
```

| Specialist Agent | Core Responsibility | Runtime Model / Framework | Telemetry & Partner Integration |
| :--- | :--- | :--- | :--- |
| **Incident Commander** | Hierarchical supervisor; orchestrates dual-mode predictive and reactive lifecycles, database persistence, and SSE event streaming. | Google Cloud Agent Runtime | Cloud SQL PostgreSQL / SQLite |
| **Predictive Risk Agent** | Evaluates leading indicators (GPU saturation, worker queue depth, segment packaging latency) to forecast saturation 5–15 min in advance. | Deterministic Math + Gemini 2.5 | **Grafana MCP Client** |
| **SCTE-35 Ad Integrity Sentinel** | Audits ad splice cues for timing drift relative to PTS (±200ms bounds), splice alignment error, and ad pod drop ratios. | Rule-based Sentinel + Gemini 2.5 | **Loki Log Query & SCTE Parser** |
| **Perceptual Quality Sentinel** | Verifies broadcast compliance: EBU R128 loudness (-24 LUFS), A/V lip-sync drift, and video frame drop ratios. | EBU R128 Standard + Gemini 2.5 | **Media Environment Telemetry** |
| **Observability Investigator** | Multi-signal correlation; queries metrics, logs, traces, and firing alert rules to diagnose active root causes. | Gemini 2.5 via Google GenAI SDK | **Grafana MCP Client** |
| **Business Impact Agent** | Commercial impact & prevention economics; calculates audience at risk, ad burn rate, and counterfactual avoided loss. | Deterministic Math + Gemini 2.5 | Live Media Simulator |
| **Safety Director** | Deterministic policy engine; strictly enforces action allowlist, 20% predictive blast radius cap, and 85% confidence threshold. | Deterministic Policy Rules | Cryptographic Audit Ledger |
| **Remediation Agent** | Formulates minimal blast-radius operational fix (`scale_transcoder_pool`, `traffic_shift`). | Gemini 2.5 Structured Output | Video Routing Proxy (`/route`) |
| **Verification Agent** | Post-remediation validator; independently re-samples Grafana MCP to compute telemetry deltas ($\Delta\text{GPU} \le -25\%$). | Gemini 2.5 Evaluation | **Grafana MCP PromQL** |

---

## 3. Dual-Mode Operational State Machine

Studio Guardian operates in dual modes: **Predictive Operations** (proactive defense) and **Reactive Incident Director** (emergency triage).

```mermaid
stateDiagram-v2
    [*] --> MONITORING
    
    state "Predictive Prevention Track" as PredictiveTrack {
        MONITORING --> RISK_DETECTED: Leading Signals Elevate (Risk >= 0.30)
        RISK_DETECTED --> PREDICTING: Deterministic Risk & Confidence Evaluated
        PREDICTING --> POLICY_CHECK: High Risk Saturation (Risk >= 0.75)
        
        state POLICY_CHECK {
            [*] --> CheckCriteria
            CheckCriteria --> AutoExecute: Risk >= 0.80 & Conf >= 0.85 & Blast <= 20% & Allowlisted
            CheckCriteria --> RequireApproval: Blast > 20% or Conf < 0.85
            CheckCriteria --> Disallowed: Non-Allowlisted Action
        }
        
        POLICY_CHECK --> PREVENTING: Decision == AUTO_EXECUTE
        POLICY_CHECK --> WAITING_HUMAN_APPROVAL: Decision == HUMAN_APPROVAL
        WAITING_HUMAN_APPROVAL --> PREVENTING: Operator Approves
        WAITING_HUMAN_APPROVAL --> MONITORING: Operator Rejects
        
        PREVENTING --> VERIFYING: scale_transcoder_pool Dispatched
        VERIFYING --> PREVENTED: Telemetry Delta Confirmed (Delta GPU <= -25%)
        PREVENTED --> MONITORING: Pipeline Stabilized
    }

    state "Reactive Fallback Track" as ReactiveTrack {
        MONITORING --> INVESTIGATING: Acute Degradation (Error > 2.0%)
        PREDICTING --> FALLBACK_REACTIVE: Acute Degradation (Error > 2.0%)
        FALLBACK_REACTIVE --> INVESTIGATING: Promote Predictive Context & Hypotheses (<500ms)
        
        INVESTIGATING --> CORRELATING: Metrics, Logs & Traces Sampled
        CORRELATING --> ASSESSING_IMPACT: Root Cause Ranked
        ASSESSING_IMPACT --> EVALUATING_POLICY: Commercial Blast Quantified
        EVALUATING_POLICY --> REMEDIATING: Traffic Shift Auto-Approved
        REMEDIATING --> VERIFYING_REACTIVE: Standby Cluster Shifted
        VERIFYING_REACTIVE --> RESOLVED: Stabilization Confirmed
        RESOLVED --> MONITORING
    }
```

---

## 4. Observability & Telemetry Pipeline

Studio Guardian implements a multi-tier telemetry architecture:

1. **Standard Prometheus Exposition (`/metrics`)**:
   Exposes both infrastructure and semantic media quality gauges:
   - `studio_guardian_playback_error_rate` (Customer-facing buffer ratio)
   - `studio_guardian_transcoder_latency_seconds` (Segment encode delay)
   - `studio_guardian_gpu_utilization_pct` (Leading compute saturation)
   - `studio_guardian_transcoder_queue_depth` (Pending video chunks)
   - `studio_guardian_scte_timing_drift_ms` (Ad splice timing drift)
   - `studio_guardian_splice_alignment_error_ms` (Splice boundary error)
   - `studio_guardian_concurrent_viewers` / `studio_guardian_affected_viewers`
   - `studio_guardian_av_sync_drift_ms` / `studio_guardian_loudness_deviation_lufs`

2. **Server-Sent Events (SSE) Live Stream (`/api/v1/stream/events`)**:
   Emits high-frequency (1 Hz) telemetry heartbeats and real-time Loki log batches (`LOKI_LOG_BATCH`) directly to connected browsers.

3. **Grafana Cloud Integration & Authentication Architecture**:
   - **Service Account Token (`glsa_...`)**: Authenticates against Grafana Cloud REST APIs (`whitepenguin2589.grafana.net/api/dashboards/db`) to publish and manage dashboard specifications.
   - **Cloud Access Policy Token (`glc_...`)**: Authenticates against the hosted Loki push endpoint (`https://logs-prod-026.grafana.net/loki/api/v1/push`) with `logs:write` scope to ingest structured broadcast logs into Grafana Cloud.

4. **In-Website Live Observability Console**:
   Provides an embedded, zero-configuration Grafana experience directly inside the command center (Tab 5) featuring Recharts-powered live streaming metric graphs and a dark-mode auto-scrolling Loki terminal console.

---

## 5. Mathematical Provenance & Verifiable Evidence

To satisfy stringent audit requirements in mission-critical broadcasting, Studio Guardian grounds all decisions in deterministic mathematics:

1. **Composite Risk Formula**:
   $$R(t) = \sum_{i=1}^{n} w_i \cdot s_i(t)$$
   Where:
   - $w_{\text{gpu}} = 0.25$ (GPU Compute Saturation)
   - $w_{\text{queue}} = 0.20$ (Transcoder Queue Buildup)
   - $w_{\text{latency}} = 0.20$ (Segment Packaging Latency)
   - $w_{\text{error}} = 0.15$ (Playback Buffer Ratio)
   - $w_{\text{viewer}} = 0.10$ (Audience Concurrency Surge)
   - $w_{\text{deploy}} = 0.10$ (Recent Deployment Proximity)

2. **Estimated Time-to-Impact**:
   $$T_{\text{impact}} = \frac{\text{Capacity Threshold} - \text{Current Value}}{\text{Rate of Change } (\Delta/\Delta t)}$$

3. **Verifiable Audit Trail**:
   Every risk calculation produces an immutable snapshot stored in `prediction_evidence` and `runtime_evidence` tables with:
   - Target datasource identifier (`PROMETHEUS_MUMBAI`, `LOKI_TRANSCODER`)
   - Exact PromQL / LogQL query expression
   - Query execution latency in milliseconds
   - Cryptographic SHA-256 hash verifying data integrity
   - Verifiable via `GET /api/v1/predictive/provenance`
