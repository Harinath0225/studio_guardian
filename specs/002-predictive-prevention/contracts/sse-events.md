# Interface Contract: Predictive Prevention SSE Events

**Feature**: [`specs/002-predictive-prevention/spec.md`](file:///c:/Coding_learning/studio_guardian/studio_guardian/specs/002-predictive-prevention/spec.md)
**Stream Path**: `/api/v1/stream/events`

All predictive events stream over the existing Server-Sent Events (SSE) bus with standard JSON envelopes: `{"event": "<EVENT_NAME>", "data": {...}}`.

---

## 1. Event Types

### 1.1 `PREDICTIVE_SNAPSHOT`
Emitted periodically (every 5–10s) with live normalized telemetry vectors.
```json
{
  "event": "PREDICTIVE_SNAPSHOT",
  "data": {
    "timestamp": 1788772500.0,
    "metrics": {
      "gpu_utilization_pct": 93.4,
      "transcoder_latency_ms": 470.0,
      "queue_depth": 48,
      "playback_error_rate_pct": 0.45,
      "active_viewers": 11800000
    },
    "normalized": {
      "gpu_pressure": 0.95,
      "queue_growth": 0.92,
      "latency_pressure": 0.88,
      "error_growth": 0.60,
      "viewer_growth": 0.85
    }
  }
}
```

---

### 1.2 `PREDICTION_DECISION`
Emitted when risk thresholds change or on model recalculation.
```json
{
  "event": "PREDICTION_DECISION",
  "data": {
    "decision_id": "dec-9912-bb34",
    "risk_score": 0.87,
    "risk_level": "HIGH",
    "confidence": 0.91,
    "failure_mode": "transcoder_capacity_exhaustion",
    "window_minutes": {"min": 7, "max": 12},
    "contributors": [
      {"name": "gpu_pressure", "points": 23.8},
      {"name": "queue_growth", "points": 18.4},
      {"name": "latency_pressure", "points": 17.6},
      {"name": "error_growth", "points": 9.0},
      {"name": "viewer_growth", "points": 8.5}
    ],
    "hypothesis": "High probability of service degradation within 7–12 minutes due to transcoder worker queue saturation.",
    "agent": "Predictive Risk Agent",
    "runtime": "Vertex AI Agent Engine (gemini-2.5-flash)"
  }
}
```

---

### 1.3 `PREVENTION_PROPOSAL`
Emitted when an action is formulated and evaluated by the Safety Director.
```json
{
  "event": "PREVENTION_PROPOSAL",
  "data": {
    "proposal_id": "prop-8e2b-45a1",
    "action_type": "scale_transcoder_pool",
    "target_service": "transcoder-worker-pool",
    "blast_radius_pct": 15.0,
    "expected_loss_without_action": 46000.0,
    "cost_of_prevention": 340.0,
    "expected_avoided_exposure": 45660.0,
    "policy_verdict": "AUTO_EXECUTE",
    "requires_approval": false
  }
}
```

---

### 1.4 `PREVENTION_VERIFIED`
Emitted after post-remediation telemetry confirms recovery.
```json
{
  "event": "PREVENTION_VERIFIED",
  "data": {
    "action_id": "act-9102-fa41",
    "verdict": "PREVENTION_VERIFIED",
    "comparison": {
      "risk_score": {"before": 0.87, "after": 0.18, "delta": -0.69},
      "gpu_utilization_pct": {"before": 93.4, "after": 61.2, "delta": -32.2},
      "transcoder_latency_ms": {"before": 470.0, "after": 260.0, "delta": -210.0},
      "playback_error_rate_pct": {"before": 0.45, "after": 0.38, "delta": -0.07}
    },
    "counterfactual": {
      "projected_risk_reduction": "87 → 18",
      "estimated_exposure_avoided": 45660.0,
      "estimated_viewers_protected": 1250000
    }
  }
}
```

---

### 1.5 `AGENT_RUNTIME_TRACE`
Powers the Unified Agent Runtime & Tool Trace Ledger in the Command Center.
```json
{
  "event": "AGENT_RUNTIME_TRACE",
  "data": {
    "trace_id": "tr-4011-aa92",
    "timestamp": 1788772505.2,
    "runtime_origin": "Grafana MCP",
    "tool_name": "query_prometheus_metrics",
    "query": "avg(media_transcode_rendition_error_rate{profile=\"1080p60_hdr\"})",
    "duration_ms": 42.6,
    "status": "SUCCESS",
    "sanitized_payload": {
      "metric": "media_transcode_rendition_error_rate",
      "value": 0.934
    }
  }
}
```
