# Studio Guardian — Enterprise Security & Safety Governance

---

## 1. Safety Director Policy Architecture

In mission-critical live broadcasting, autonomous agents must never be granted unrestricted mutation privileges. Studio Guardian implements a **Deterministic Policy Engine** (The Safety Director) that operates on formal mathematical rules, independent of LLM probabilistic outputs.

```text
[ Remediation Plan ]
         │
         ▼
[ Safety Director ]
  ├── 1. Action Allowlist Check:
  │      Is action in {TRAFFIC_SHIFT, CONTAINER_RESTART, SCALE_REPLICAS}?
  │      NO  ──► Immediate REJECT (ESCALATED_HUMAN_TAKEOVER)
  │      YES ──► Proceed to Step 2
  │
  ├── 2. Blast Radius Threshold Check:
  │      Is estimated blast radius > 25.0% of total stream audience?
  │      YES ──► Gate for HUMAN APPROVAL (WAITING_HUMAN_APPROVAL)
  │      NO  ──► Proceed to Step 3
  │
  └── 3. Diagnostic Confidence Check:
         Is diagnostic confidence < 0.85 (85%)?
         YES ──► Gate for HUMAN APPROVAL (WAITING_HUMAN_APPROVAL)
         NO  ──► Grant AUTO_EXECUTE
```

---

## 2. Security Principles

### Principle 1: Least Privilege
- Specialist agents have strictly scoped tool sets:
  - `Observability Investigator`: Read-only queries to Grafana MCP (`query_prometheus_metrics`, `search_loki_logs`, `get_tempo_traces`, `list_grafana_alerts`).
  - `Remediation Agent`: Only accesses the controlled video routing proxy (`/route`).
  - `Verification Agent`: Read-only query to Prometheus telemetry.

### Principle 2: Strict Mutation Allowlist
Only three operational actions are permitted:
1. `TRAFFIC_SHIFT`: Diverts regional client ingress to alternate transcode or origin clusters.
2. `CONTAINER_RESTART`: Restarts a failing container instance within an active pod.
3. `SCALE_REPLICAS`: Increases worker capacity in an overloaded cluster.

**Forbidden Actions**:
- `DATABASE_DROP`
- `FLUSH_ALL_KEYS`
- `TERMINATE_ORIGIN_CLUSTER`
- `GLOBAL_DNS_PURGE`

Any proposed action matching the forbidden list or not present in the allowlist is immediately **REJECTED** and logs an immutable audit event.

### Principle 3: No Secrets in Frontend
- Frontend code contains **zero** API keys, credentials, or service account tokens.
- All communications with Google Cloud Vertex AI and Grafana Cloud are mediated through the backend using Secret Manager or environment variables.

### Principle 4: Immutable Audit Logging
Every state transition, agent run, observation, policy evaluation, and operator decision is recorded in the PostgreSQL `audit_logs` and `incident_events` tables with microsecond timestamps and actor attribution.

### Principle 5: Chain-of-Thought Concealment
Raw internal model thinking and scratchpads are never exposed via public APIs or the frontend UI. The UI only displays validated Pydantic v2 structured schemas (hypotheses, impact assessments, and verification verdicts).
