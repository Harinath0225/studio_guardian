# Technical Research & Architecture Decisions: Studio Guardian

**Feature**: `001-media-incident-director`  
**Date**: 2026-09-06  
**Status**: Completed  

---

## 1. Google Cloud Agent Architecture & Runtime

### Decision
Use **Google GenAI SDK (`google-genai`) / Agent Development Kit (ADK) in Python** for defining specialist agents with structured schemas and native tool-calling on Gemini 2.5 Pro / Flash, paired with **Vertex AI Search** for semantic historical incident fingerprint retrieval.

### Rationale
- **In-Repository Version Control**: Defining agents as Python modules with Pydantic v2 schemas ensures 100% of agent logic, prompts, and tool abstractions live in Git, enabling rapid local unit/integration testing without waiting for Cloud Console roundtrips.
- **Native Structured Outputs**: Gemini supports strict JSON schemas natively via `response_schema` in the Google GenAI SDK, guaranteeing valid Pydantic models from the Observability Investigator, Business Impact Agent, and Verification Agent.
- **Production Cloud Deployment**: The application packages as a standard Cloud Run container using Google Cloud Application Default Credentials (ADC) and IAM service accounts.

### Alternatives Considered
- *Vertex AI Agent Builder Console-only*: Rejected because managing agents via Cloud UI makes local CI/CD automated testing and git versioning difficult during a fast-paced 3-day hackathon.
- *LangChain / CrewAI*: Rejected because Constitution Principle 4 strictly mandates native Google Cloud agent framework participation rather than third-party abstractions.

---

## 2. Grafana MCP Integration Architecture

### Decision
Integrate with Grafana via a dedicated **Grafana Model Context Protocol (MCP) Client** implemented in Python using the standard `mcp` SDK over JSON-RPC (stdio for local containerized Grafana MCP server, and HTTP/SSE for remote Grafana Cloud).

### Tool Surface
The Grafana MCP integration exposes four core tools to the Observability Investigator:
1. `query_prometheus_metrics(query: str, start_time: str, end_time: str, step: str)`: Fetches time-series data for playback error rates, transcoder latency, and GPU allocations.
2. `search_loki_logs(query: str, limit: int, time_range: str)`: Queries streaming service log streams for deployment crash logs and out-of-memory errors.
3. `get_tempo_traces(trace_id: str, service_name: str)`: Inspects distributed trace spans for pipeline bottlenecks.
4. `list_grafana_alerts(state: str)`: Pulls firing alerts across production clusters.

### Local Development vs. Production Behavior
- **Local Dev / Offline**: A built-in high-fidelity Grafana MCP mock server serves deterministic Prometheus/Loki responses matching the "India vs Australia Final" incident when an external Grafana instance is not connected.
- **Live / Demo Mode**: Connects directly to a running Grafana instance or Grafana Cloud using API keys stored server-side via environment variables / Secret Manager.

### Alternatives Considered
- *Direct Grafana REST API queries*: Rejected because hackathon track rules and Constitution Principle 5 require authentic Model Context Protocol (MCP) tool integration.

---

## 3. Multi-Agent Orchestration & Supervisor Pattern

### Decision
Implement a deterministic **Supervisor / Incident Commander state machine** in FastAPI that sequentially triggers specialist agents with explicit state transitions and typed contracts, persisting every agent run and state transition to PostgreSQL.

```text
       [DETECTED]
           │
           ▼
     [INVESTIGATING]  ──► (Observability Investigator via Grafana MCP)
           │
           ▼
      [CORRELATING]   ──► (Gemini Root-Cause Hypothesis Generation)
           │
           ▼
    [BUSINESS_IMPACT] ──► (Business Impact Agent: Viewers, Ad Windows, SLA)
           │
           ▼
        [DECISION]    ──► (Candidate Remediation Selection)
           │
           ▼
     [POLICY_CHECK]   ──► (Deterministic Safety Director)
      ┌────┴────┐
      ▼         ▼
[AUTO_EXEC] [AWAIT_APPROVAL] ──► (Operator Approval Modal)
      └────┬────┘
           ▼
     [REMEDIATING]    ──► (Remediation Agent: Traffic Shift API)
           │
           ▼
      [VERIFYING]     ──► (Verification Agent: Telemetry Re-query)
      ┌────┴────┐
      ▼         ▼
  [SUCCESS]  [FAILED]
      │         │
      │         ▼
      │   [REINVESTIGATING] (Up to max attempts)
      │
      ▼
  [RESOLVED] ──► (Persist Incident Fingerprint & Generate Reports)
```

### Rationale
- Pure state machine supervisor eliminates unpredictable peer-to-peer agent loops.
- Satisfies Constitution Principle 2 (Hierarchical Supervisor) and Principle 3 (Deterministic business logic in code, LLM for reasoning).

---

## 4. Controlled Media Simulation & Incident Injection

### Decision
Build an in-process, lightweight **Media Streaming Simulator** within the modular monolith that maintains state for a simulated video broadcast pipeline:
- **Transcoder Clusters**: `transcoder-syd-01` (Australia), `transcoder-sin-01` (Singapore), `transcoder-us-01` (Backup standby).
- **Incident Injection**: `POST /api/v1/demo/incident` modifies simulator state to introduce:
  - Transcoder latency: 18ms → 480ms
  - GPU allocation failures: 0% → 14.2%
  - Playback error rate: 0.4% → 8.7%
  - Correlated event: deployment tag `v4.2.1-transcoder-patch` applied 3 minutes prior.
- **Remediation Action**: `POST /api/v1/simulator/route` updates regional routing weights (100% Australia/Singapore traffic shifted to `transcoder-us-01`), returning metrics back to baseline (0.4% error rate).

---

## 5. Frontend & 3D Visualization Strategy

### Decision
- **Core Framework**: React 18 + TypeScript + Vite + TailwindCSS + Lucide Icons.
- **Charts**: Recharts / Chart.js for real-time 1 Hz telemetry streaming (error rates, concurrency, latency).
- **3D Visualization**: Lightweight **React Three Fiber (R3F) / Three.js** canvas rendering a "Live Event Core" globe surrounded by orbital service nodes (Transcoders, CDN edge, Packagers, Regions) with animated pulse rings.
  - Normal: Soft cyan/emerald ambient glow.
  - Incident: Australia & Singapore nodes pulse amber/red with particle flow indicating degraded pipelines.
  - Recovery: Verified transition back to emerald.
- **Real-Time Stream**: Server-Sent Events (`/api/v1/stream/events`) pushing typed event packets (`agent_started`, `evidence_found`, `decision_created`, `remediation_started`, `verification_completed`).

---

## 6. Persistence & Relational Schema

### Decision
Use **PostgreSQL 16 + SQLAlchemy 2.x (asyncpg) + Alembic migrations**.
- Normalized tables for relational integrity: `incidents`, `agent_runs`, `remediation_actions`, `verification_results`, `audit_logs`.
- JSONB columns for flexible agent outputs, evidence payloads, and incident fingerprints, avoiding premature schema rigidity while guaranteeing durable auditability.

---

## 7. Security & Enterprise Readiness

### Decision
- Zero secrets in frontend; all Grafana API tokens, Gemini API keys, and service identities are read strictly from environment variables or Google Secret Manager.
- Remediation actions are strictly allowlisted (`TRAFFIC_SHIFT`, `CONTAINER_RESTART`, `SCALE_REPLICAS`); arbitrary shell commands or unstructured script executions are forbidden by the deterministic Safety Director.
