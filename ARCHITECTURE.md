# Studio Guardian — System Architecture

**Autonomous Live Media Incident Director**  
Built for the **Google Cloud & Grafana Labs Hackathon**

---

## 1. System Topology Overview

Studio Guardian operates as an autonomous, multi-agent operational supervisor designed specifically for high-stakes, large-scale live media broadcasts (such as global cricket finals, live sporting championships, and concert streams).

```mermaid
flowchart TD
    subgraph LiveMediaEnvironment ["Live Media Infrastructure"]
        EdgeProxy["Regional Video Proxy (/route)"]
        TranscoderCluster["Transcode Cluster (Sydney/Singapore)"]
        StandbyCluster["Warm Standby Cluster (US-West)"]
        EdgeProxy --> TranscoderCluster
        EdgeProxy -.->|Controlled Traffic Shift| StandbyCluster
    end

    subgraph ObservabilityStack ["Grafana Labs Telemetry Stack"]
        Prometheus["Prometheus (Buffer Ratio / Rates)"]
        Loki["Loki (Transcoder Crash Logs)"]
        Tempo["Tempo (Distributed Segment Traces)"]
        Alertmanager["Grafana Alerting (Firing Rules)"]
    end

    subgraph MCPClientLayer ["Model Context Protocol (MCP)"]
        GrafanaMCP["Grafana MCP Client Adapter"]
        GrafanaMCP --> Prometheus
        GrafanaMCP --> Loki
        GrafanaMCP --> Tempo
        GrafanaMCP --> Alertmanager
    end

    subgraph AgentRuntime ["Google Cloud Multi-Agent Runtime"]
        IC["Incident Commander (Supervisor State Machine)"]
        ObsAgent["Observability Investigator Agent"]
        ImpactAgent["Business Impact Agent"]
        SafetyDir["Safety Director (Deterministic Policy Engine)"]
        RemAgent["Remediation Agent"]
        VerAgent["Verification Agent"]

        IC --> ObsAgent
        ObsAgent -->|Evidence & Hypotheses| IC
        IC --> ImpactAgent
        ImpactAgent -->|Audience & Ad Burn| IC
        IC --> SafetyDir
        SafetyDir -->|AUTO_EXECUTE / APPROVAL| RemAgent
        RemAgent -->|Traffic Shift Command| EdgeProxy
        IC --> VerAgent
        VerAgent -->|Independent Telemetry Verdict| IC
    end

    subgraph PersistenceAndDelivery ["Storage & Event Delivery"]
        Postgres[(Cloud SQL PostgreSQL)]
        EventBus["Async Event Bus (SSE /stream/events)"]
        Frontend["React + Three.js Command Center"]

        IC --> Postgres
        IC --> EventBus
        EventBus --> Frontend
    end

    ObsAgent -.->|Tools: query_metrics, search_logs, get_traces| GrafanaMCP
    VerAgent -.->|Independent Metric Sample| GrafanaMCP
```

---

## 2. Multi-Agent Boundaries & Responsibilities

| Specialist Agent | Core Responsibility | Runtime Model / Framework | Partner Integration |
| :--- | :--- | :--- | :--- |
| **Incident Commander** | Hierarchical supervisor; enforces state transitions, tracks retries, manages database persistence. | Google Cloud Agent Runtime | Cloud SQL PostgreSQL |
| **Observability Investigator** | Multi-signal correlation; queries metrics, logs, traces, and firing alerts to diagnose root cause. | Gemini 2.5 via Google GenAI SDK | **Grafana MCP Client** |
| **Business Impact Agent** | Commercial impact calculation; calculates impacted audience, VIP tiers, ad revenue burn, and SLA liability. | Deterministic Math + Gemini 2.5 | Live Media Simulator |
| **Safety Director** | Policy engine; strictly enforces action allowlist, 25% blast radius cap, and 85% confidence threshold. | Deterministic Policy Rules | Audit Logging |
| **Remediation Agent** | Formulates minimal blast-radius operational fix and dispatches traffic shift to video routing proxy. | Gemini 2.5 Structured Output | Video Routing Proxy |
| **Verification Agent** | Post-remediation validator; independently re-samples Grafana MCP to compute metric deltas and stability. | Gemini 2.5 Evaluation | **Grafana MCP PromQL** |

---

## 3. Operational State Machine

```mermaid
stateDiagram-v2
    [*] --> TRIGGERED
    TRIGGERED --> INVESTIGATING: Alert Fired
    INVESTIGATING --> CORRELATING: Metrics, Logs & Traces Sampled
    CORRELATING --> ASSESSING_IMPACT: Root Cause Ranked
    ASSESSING_IMPACT --> EVALUATING_POLICY: Commercial Blast Quantified
    
    state EVALUATING_POLICY {
        [*] --> CheckAllowlist
        CheckAllowlist --> CheckBlastRadius: Allowlisted Action
        CheckBlastRadius --> CheckConfidence: Blast Radius <= 25%
        CheckConfidence --> AutoExecute: Confidence >= 85%
        CheckBlastRadius --> GateHuman: Blast Radius > 25%
        CheckConfidence --> GateHuman: Confidence < 85%
        CheckAllowlist --> Reject: Disallowed Mutation
    }

    EVALUATING_POLICY --> REMEDIATING: Decision == AUTO_EXECUTE
    EVALUATING_POLICY --> WAITING_HUMAN_APPROVAL: Decision == HUMAN_APPROVAL
    EVALUATING_POLICY --> ESCALATED_HUMAN_TAKEOVER: Decision == REJECTED

    WAITING_HUMAN_APPROVAL --> REMEDIATING: Operator Approves
    WAITING_HUMAN_APPROVAL --> ESCALATED_HUMAN_TAKEOVER: Operator Rejects

    REMEDIATING --> VERIFYING: Video Proxy Shift Dispatched
    VERIFYING --> RESOLVED: Stabilization Confirmed (Delta > 8%)
    VERIFYING --> REINVESTIGATING: Metrics Flapping / Degraded
    REINVESTIGATING --> INVESTIGATING: Retries < 2
    REINVESTIGATING --> ESCALATED_HUMAN_TAKEOVER: Retries Exceeded (>= 2)

    RESOLVED --> [*]
    ESCALATED_HUMAN_TAKEOVER --> [*]
```

---

## 4. Controlled Remediation vs Real Infrastructure

Studio Guardian enforces a strict separation between read-only observability and controlled remediation:
1. **Telemetry Ingestion**: The agent queries Grafana MCP using real tool definitions (`query_prometheus_metrics`, `search_loki_logs`, `get_tempo_traces`, `list_grafana_alerts`).
2. **Safety Gating**: Actions outside `{TRAFFIC_SHIFT, CONTAINER_RESTART, SCALE_REPLICAS}` are immediately rejected.
3. **Execution**: The Remediation Agent communicates directly with the video routing controller endpoint (`/route`) to divert regional HLS/DASH traffic away from the degraded cluster.
4. **Verification**: The Verification Agent independently evaluates stabilization without trusting the Remediation Agent's status.
