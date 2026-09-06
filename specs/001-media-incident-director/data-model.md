# Data Model Specification: Studio Guardian

**Feature**: `001-media-incident-director`  
**Storage Engine**: PostgreSQL 16 (SQLAlchemy 2.x async ORM)  
**Status**: Completed  

---

## Entity Relationship Diagram (Conceptual)

```text
  ┌────────────────────────────────────────────────────────┐
  │                       incidents                        │
  │  (id, title, status, severity, started_at, resolved_at)│
  └───┬────────────┬─────────────┬────────────┬─────────┬──┘
      │            │             │            │         │
      ▼            ▼             ▼            ▼         ▼
┌───────────┐┌───────────┐┌─────────────┐┌─────────┐┌────────────────┐
│agent_runs ││incident_  ││observations ││business_││remediation_   │
│           ││events     ││             ││impacts  ││actions         │
└─────┬─────┘└───────────┘└──────┬──────┘└─────────┘└───────┬────────┘
      │                          │                          │
      │                          ▼                          ▼
      │               ┌───────────────────────┐   ┌───────────────────┐
      │               │ root_cause_hypotheses │   │verification_      │
      │               └───────────────────────┘   │results            │
      ▼                                           └───────────────────┘
┌───────────┐
│audit_logs │
└───────────┘
```

---

## 1. Table: `incidents`

Represents the core streaming incident lifecycle.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique incident identifier |
| `event_title` | `VARCHAR(255)` | NOT NULL | Name of live broadcast (e.g. "India vs Australia Final") |
| `status` | `VARCHAR(50)` | NOT NULL, INDEX | Current state: `HEALTHY`, `DETECTED`, `INVESTIGATING`, `CORRELATING`, `BUSINESS_IMPACT`, `DECISION`, `POLICY_CHECK`, `AWAITING_APPROVAL`, `REMEDIATING`, `VERIFYING`, `REINVESTIGATING`, `RESOLVED`, `ESCALATED` |
| `severity` | `VARCHAR(20)` | NOT NULL | `SEV1` (Critical), `SEV2` (Major), `SEV3` (Minor) |
| `primary_affected_service`| `VARCHAR(100)` | NULL | Primary degraded service (e.g. `transcoder-syd-01`) |
| `affected_regions` | `JSONB` | NOT NULL, default `'[]'` | List of affected ISO country/region codes |
| `retry_count` | `INTEGER` | NOT NULL, default `0` | Count of remediation attempts |
| `max_retries` | `INTEGER` | NOT NULL, default `2` | Configurable ceiling before human escalation |
| `started_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Timestamp when incident was detected |
| `resolved_at` | `TIMESTAMPTZ` | NULL | Timestamp when verified recovery occurred |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Database record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Database record update timestamp |

---

## 2. Table: `incident_events`

Append-only timeline events streamed via SSE/WebSocket to the Command Center UI.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique event ID |
| `incident_id` | `UUID` | FK → `incidents.id` ON DELETE CASCADE | Associated incident |
| `event_type` | `VARCHAR(50)` | NOT NULL, INDEX | Event identifier (`agent_started`, `tool_called`, `evidence_found`, `decision_created`, `remediation_started`, `verification_completed`, etc.) |
| `source_agent` | `VARCHAR(50)` | NULL | Agent originating the event |
| `summary` | `TEXT` | NOT NULL | Human-readable explanation for operational timeline |
| `payload` | `JSONB` | NOT NULL, default `'{}'` | Structured details (metrics, confidence, parameters) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Timestamp of occurrence |

---

## 3. Table: `agent_runs`

Audit of every discrete specialist agent execution.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique run ID |
| `incident_id` | `UUID` | FK → `incidents.id` ON DELETE CASCADE | Associated incident |
| `agent_name` | `VARCHAR(50)` | NOT NULL, INDEX | `incident_commander`, `observability_investigator`, `business_impact_agent`, `remediation_agent`, `verification_agent` |
| `status` | `VARCHAR(20)` | NOT NULL | `STARTED`, `COMPLETED`, `FAILED` |
| `input_context` | `JSONB` | NOT NULL, default `'{}'` | Input schema supplied to agent |
| `output_data` | `JSONB` | NULL | Structured Pydantic response returned by agent |
| `tool_invocations`| `JSONB` | NOT NULL, default `'[]'` | List of MCP/API tools called with args and durations |
| `duration_ms` | `INTEGER` | NULL | Execution duration in milliseconds |
| `started_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Agent start timestamp |
| `completed_at` | `TIMESTAMPTZ` | NULL | Agent completion timestamp |

---

## 4. Table: `observations`

Empirical evidence gathered by the Observability Investigator via Grafana MCP.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique observation ID |
| `incident_id` | `UUID` | FK → `incidents.id` ON DELETE CASCADE | Associated incident |
| `agent_run_id` | `UUID` | FK → `agent_runs.id` ON DELETE CASCADE | Generating agent run |
| `source` | `VARCHAR(50)` | NOT NULL | `grafana_prometheus`, `grafana_loki`, `grafana_tempo`, `grafana_alerts` |
| `metric_name` | `VARCHAR(100)` | NOT NULL | Name of metric/log queried |
| `baseline_value` | `FLOAT` | NULL | Expected normal value |
| `observed_value` | `FLOAT` | NULL | Anomalous observed value |
| `unit` | `VARCHAR(20)` | NULL | Metric unit (`%`, `ms`, `count`, etc.) |
| `is_anomaly` | `BOOLEAN` | NOT NULL, default `true` | Whether value represents statistically significant anomaly |
| `raw_telemetry` | `JSONB` | NOT NULL, default `'{}'` | Raw query result snippet |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Recorded timestamp |

---

## 5. Table: `root_cause_hypotheses`

Ranked causal hypotheses formulated from correlated evidence.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique hypothesis ID |
| `incident_id` | `UUID` | FK → `incidents.id` ON DELETE CASCADE | Associated incident |
| `root_cause_title`| `VARCHAR(255)` | NOT NULL | Concise description of suspected cause |
| `confidence` | `FLOAT` | NOT NULL | Confidence score `0.00` – `1.00` |
| `causal_chain` | `TEXT` | NOT NULL | Natural-language explanation of sequence |
| `supporting_evidence_ids` | `JSONB` | NOT NULL, default `'[]'` | List of `observations.id` supporting this hypothesis |
| `is_primary` | `BOOLEAN` | NOT NULL, default `false` | Selected by supervisor as primary working diagnosis |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Creation timestamp |

---

## 6. Table: `business_impacts`

Operational and financial risk evaluation for the incident.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique impact record ID |
| `incident_id` | `UUID` | FK → `incidents.id` ON DELETE CASCADE | Associated incident |
| `affected_viewers`| `INTEGER` | NOT NULL | Estimated concurrent viewers degraded |
| `vip_viewers` | `INTEGER` | NOT NULL | Estimated premium/VIP subscribers impacted |
| `impact_score` | `INTEGER` | NOT NULL | Normalized score `1` – `100` |
| `estimated_ad_exposure_usd` | `FLOAT` | NOT NULL | Projected ad window revenue at risk |
| `sla_breach_risk`| `VARCHAR(20)` | NOT NULL | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `narrative_summary` | `TEXT` | NOT NULL | Executive-level impact summary |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Calculation timestamp |

---

## 7. Table: `remediation_actions`

Controlled operational tasks evaluated by the Safety Director and dispatched.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique action ID |
| `incident_id` | `UUID` | FK → `incidents.id` ON DELETE CASCADE | Associated incident |
| `action_type` | `VARCHAR(50)` | NOT NULL | `TRAFFIC_SHIFT`, `CONTAINER_RESTART`, `SCALE_REPLICAS` |
| `target_resource`| `VARCHAR(100)` | NOT NULL | Target infrastructure resource |
| `parameters` | `JSONB` | NOT NULL, default `'{}'` | Action-specific parameters (e.g. `{"shift_pct": 100, "to": "transcoder-us-01"}`) |
| `risk_level` | `VARCHAR(20)` | NOT NULL | `LOW`, `MEDIUM`, `HIGH` |
| `blast_radius_pct`| `FLOAT` | NOT NULL | Percentage of audience/system affected |
| `policy_decision`| `VARCHAR(30)` | NOT NULL | `AUTO_EXECUTE`, `HUMAN_APPROVAL_REQUIRED`, `BLOCKED` |
| `approval_status`| `VARCHAR(20)` | NOT NULL | `NOT_REQUIRED`, `PENDING`, `APPROVED`, `REJECTED` |
| `approved_by` | `VARCHAR(100)` | NULL | User ID or `SYSTEM_POLICY_ENGINE` |
| `execution_status`| `VARCHAR(20)` | NOT NULL | `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED` |
| `executed_at` | `TIMESTAMPTZ` | NULL | Execution dispatch timestamp |
| `execution_output`| `JSONB` | NULL | Output payload from target system |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Creation timestamp |

---

## 8. Table: `verification_results`

Independent post-remediation validation records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique verification ID |
| `incident_id` | `UUID` | FK → `incidents.id` ON DELETE CASCADE | Associated incident |
| `remediation_action_id` | `UUID` | FK → `remediation_actions.id` | Tested remediation action |
| `status` | `VARCHAR(20)` | NOT NULL | `VERIFIED_HEALTHY`, `RECOVERY_FAILED`, `INCONCLUSIVE` |
| `recovery_confidence` | `FLOAT` | NOT NULL | Confidence `0.00` – `1.00` |
| `before_telemetry` | `JSONB` | NOT NULL | Metric snapshot prior to action |
| `after_telemetry` | `JSONB` | NOT NULL | Metric snapshot after action |
| `stability_duration_sec` | `INTEGER` | NOT NULL | Telemetry window checked (e.g. 15s) |
| `verification_summary` | `TEXT` | NOT NULL | Explanation of verification conclusion |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Verification timestamp |

---

## 9. Table: `incident_fingerprints`

Historical pattern vectors for post-incident institutional memory.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique fingerprint ID |
| `incident_id` | `UUID` | FK → `incidents.id` ON DELETE CASCADE | Source incident |
| `symptom_signature` | `JSONB` | NOT NULL | Normalized anomaly vector (error rate, GPU, latency deltas) |
| `root_cause_summary`| `VARCHAR(255)` | NOT NULL | Resolved root cause statement |
| `successful_action_type`| `VARCHAR(50)` | NOT NULL | Action type that verified recovery |
| `tags` | `JSONB` | NOT NULL, default `'[]'` | Descriptive tags for keyword matching |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Creation timestamp |

---

## 10. Table: `audit_logs`

Immutable security and governance audit trail.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique audit entry ID |
| `actor` | `VARCHAR(100)` | NOT NULL | Agent name or operator user ID |
| `action` | `VARCHAR(100)` | NOT NULL | Action name (e.g. `POLICY_EVALUATION`, `MANUAL_OVERRIDE`, `REMEDIATION_DISPATCH`) |
| `resource_id` | `VARCHAR(100)` | NOT NULL | Impacted incident or resource ID |
| `details` | `JSONB` | NOT NULL, default `'{}'` | Security context and payload |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Recorded timestamp |
