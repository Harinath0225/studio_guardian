# Interface Contract: Predictive Prevention REST API

**Feature**: [`specs/002-predictive-prevention/spec.md`](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/002-predictive-prevention/spec.md)
**Base Path**: `/api/v1/prediction`

---

## 1. Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/status` | Current predictive state, composite risk score, contributing factors, and horizon. |
| `POST` | `/evaluate` | Trigger an on-demand evaluation cycle querying live Grafana MCP telemetry. |
| `POST` | `/proposals/{id}/authorize` | Operator authorization for gated preventive action (`WAITING_HUMAN_APPROVAL`). |
| `POST` | `/proposals/{id}/reject` | Operator rejection of a recommended preventive action. |
| `GET` | `/history` | Historical audit list of predictions, prevention actions, and verification deltas. |
| `POST` | `/demo/scenario` | Trigger the deterministic multi-step predictive demo scenario. |

---

## 2. Endpoint Specifications

### 2.1 GET `/status`
Returns the active predictive operating condition.

#### Response `200 OK`
```json
{
  "state": "IMMINENT_RISK",
  "risk_score": 0.87,
  "risk_level": "HIGH",
  "confidence_score": 0.91,
  "predicted_failure_mode": "transcoder_capacity_exhaustion",
  "estimated_window_minutes": {
    "min": 7,
    "max": 12
  },
  "contributors": [
    {"name": "gpu_pressure", "label": "GPU Utilization Saturation", "raw_value": 93.4, "normalized": 0.95, "points": 23.8},
    {"name": "queue_growth", "label": "Transcoder Queue Acceleration", "raw_value": 48.0, "normalized": 0.92, "points": 18.4},
    {"name": "latency_pressure", "label": "Origin Segment Fetch Latency", "raw_value": 470.0, "normalized": 0.88, "points": 17.6},
    {"name": "error_growth", "label": "Playback Error Growth Rate", "raw_value": 0.05, "normalized": 0.60, "points": 9.0},
    {"name": "viewer_growth", "label": "Audience Concurrency Surge", "raw_value": 11800000, "normalized": 0.85, "points": 8.5},
    {"name": "deployment_risk", "label": "Recent Config Update Recency", "raw_value": 0.0, "normalized": 0.0, "points": 0.0}
  ],
  "failure_hypothesis": "Rapid queue buildup coupled with GPU core allocation throttling indicates primary transcoder pool saturation within 7 to 12 minutes.",
  "active_proposal": {
    "id": "prop-8e2b-45a1",
    "action_type": "scale_transcoder_pool",
    "target_service": "transcoder-worker-pool",
    "blast_radius_pct": 15.0,
    "expected_loss_without_action": 46000.0,
    "cost_of_prevention": 340.0,
    "expected_avoided_exposure": 45660.0,
    "policy_verdict": "AUTO_EXECUTE",
    "status": "DISPATCHED"
  },
  "runtime_metadata": {
    "agent_engine": "Vertex AI (gemini-2.5-flash)",
    "active_agent": "Predictive Risk Agent",
    "session_id": "sg-pred-20260907-8831a",
    "telemetry_source": "LIVE_GRAFANA_MCP"
  },
  "updated_at": "2026-09-07T19:15:00Z"
}
```

---

### 2.2 POST `/evaluate`
Forces immediate telemetry sampling from Grafana MCP, running feature normalization and risk calculation.

#### Request Body (Optional)
```json
{
  "force_telemetry_refresh": true
}
```

#### Response `200 OK`
Returns the generated `PredictionDecision` entity.

---

### 2.3 POST `/proposals/{id}/authorize`
Human operator authorization when an action is gated by the Safety Director.

#### Request Body
```json
{
  "operator_id": "sre-director-alpha",
  "notes": "Pre-authorized regional transcoder scale for final quarter."
}
```

#### Response `200 OK`
```json
{
  "action_id": "act-9102-fa41",
  "status": "DISPATCHED",
  "dispatched_at": "2026-09-07T19:15:12Z",
  "message": "Preventive remediation authorized and dispatched."
}
```

---

### 2.4 POST `/demo/scenario`
Drives the progressive multi-step scenario for demonstration.

#### Request Body
```json
{
  "scenario": "transcoder_saturation_surge",
  "step": 3
}
```

- `step 1`: Healthy baseline (GPU 65%, Latency 220ms, Risk 15)
- `step 2`: Elevated risk (GPU 81%, Latency 340ms, Risk 62)
- `step 3`: Imminent risk (GPU 93%, Latency 470ms, Risk 87) → Triggers prevention
- `step 4`: Post-prevention recovery (GPU 61%, Latency 260ms, Risk 18) → Verified
