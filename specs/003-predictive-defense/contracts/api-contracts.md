# API Contracts: Predictive Media Protection & Black Swan Defense

**Feature**: Predictive Media Protection & Black Swan Defense  
**Branch**: `003-predictive-defense`  
**Date**: 2026-09-08  
**Format**: OpenAPI 3.1 Specification / Markdown Contracts  

---

## 1. Predictive Engine Endpoints

### 1.1 `GET /api/v1/predictive/status`
Retrieves the latest evaluated operational risk status, contributing signals, failure horizon window, and Vertex AI runtime metadata.

**Response `200 OK`**:
```json
{
  "snapshot_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "sampled_at": "2026-09-08T07:15:30Z",
  "risk_score": 0.87,
  "risk_tier": "HIGH_RISK",
  "predicted_failure_mode": "transcoder_capacity_exhaustion",
  "prediction_window": {
    "min_minutes": 3,
    "max_minutes": 7
  },
  "confidence": 0.89,
  "contributors": [
    {
      "name": "gpu_pressure",
      "label": "GPU Utilization Saturation",
      "raw_value": 93.4,
      "normalized": 0.9644,
      "points": 24.11
    },
    {
      "name": "queue_growth",
      "label": "Transcoder Queue Buildup",
      "raw_value": 48.0,
      "normalized": 0.9556,
      "points": 19.11
    },
    {
      "name": "latency_pressure",
      "label": "Segment Fetch Latency",
      "raw_value": 470.0,
      "normalized": 0.9143,
      "points": 18.29
    }
  ],
  "runtime_metadata": {
    "agent_runtime": "Vertex AI Agent Engine",
    "agent_name": "PredictiveRiskAgent",
    "session_id": "session-pred-7f2a1b9c",
    "agent_state": "EVALUATED",
    "execution_frames": [
      {
        "timestamp": 1788851730.12,
        "stage": "TELEMETRY_INGESTION",
        "provider": "GRAFANA_MCP"
      }
    ]
  }
}
```

---

### 1.2 `POST /api/v1/predictive/evaluate`
Triggers an on-demand live evaluation by querying fresh Grafana MCP telemetry.

**Request**:
```json
{
  "channel_id": "star-sports-live",
  "force_refresh": true
}
```

**Response `200 OK`**: Same schema as `GET /api/v1/predictive/status`.

---

### 1.3 `POST /api/v1/predictive/prevent`
Executes an approved preventive remediation action governed by the Safety Director.

**Request**:
```json
{
  "action_type": "scale_transcoder_pool",
  "target_service": "transcoder-worker-pool",
  "parameters": {
    "scale_factor": 2.0
  },
  "override_reason": null
}
```

**Response `200 OK`**:
```json
{
  "action_id": "3a8c6f11-9e11-4fa2-bc89-8b9a12c45def",
  "action_type": "scale_transcoder_pool",
  "status": "COMPLETED",
  "policy_verdict": "AUTO_EXECUTE",
  "details": {
    "previous_pool_size": 8,
    "new_pool_size": 16,
    "message": "Successfully scaled transcoder worker pool to 16 active nodes."
  },
  "economics": {
    "expected_loss_without_action": 48500.0,
    "cost_of_prevention": 680.0,
    "expected_avoided_exposure": 47820.0,
    "provenance_label": "ESTIMATED"
  },
  "executed_at": 1788851745.5
}
```

---

### 1.4 `GET /api/v1/predictive/provenance/{snapshot_id}/{metric_name}`
Returns complete mathematical lineage and calculation steps for a specific signal or composite score.

**Response `200 OK`**:
```json
{
  "snapshot_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "metric_name": "gpu_pressure",
  "source_datasource": "prometheus",
  "raw_mcp_query": "sum(rate(container_gpu_utilization[1m])) by (cluster)",
  "raw_value": 93.4,
  "unit": "%",
  "sampled_timestamp": "2026-09-08T07:15:30Z",
  "slo_bounds": {
    "floor": 50.0,
    "ceil": 95.0
  },
  "normalization_formula": "clamp_min_max(raw, 50.0, 95.0) -> (93.4 - 50.0) / (95.0 - 50.0)",
  "normalized_value": 0.9644,
  "assigned_weight": 0.25,
  "contribution_points": 24.11,
  "formula_provenance": "points = normalized_value * weight * 100"
}
```

---

## 2. Media Specialist Endpoints

### 2.1 `GET /api/v1/media/ad-integrity`
Returns current SCTE-35 ad splice integrity metrics and drift status.

**Response `200 OK`**:
```json
{
  "timestamp": "2026-09-08T07:15:30Z",
  "stream_id": "star-sports-live",
  "scte_timing_drift_ms": 14.5,
  "operational_tolerance_ms": 200.0,
  "splice_alignment_error_ms": 8.0,
  "ad_pod_drop_pct": 0.0,
  "tracking_error_ratio": 0.002,
  "status": "NOMINAL",
  "is_anomaly": false,
  "active_remediation_path": "PRIMARY_SPLICE_INSERTER"
}
```

---

### 2.2 `GET /api/v1/media/perceptual-quality`
Returns lightweight perceptual stream quality signals.

**Response `200 OK`**:
```json
{
  "timestamp": "2026-09-08T07:15:30Z",
  "stream_id": "star-sports-live",
  "av_sync_drift_ms": -18.2,
  "av_sync_tolerance_ms": 100.0,
  "loudness_lufs": -23.8,
  "loudness_target_lufs": -24.0,
  "loudness_deviation_lufs": 0.2,
  "frame_drop_ratio_pct": 0.12,
  "black_frame_ratio_pct": 0.0,
  "status": "HEALTHY",
  "is_anomaly": false
}
```

---

## 3. Black Swan Gameday Endpoints

### 3.1 `POST /api/v1/demo/black-swan/inject`
Injects a deterministic chaos scenario.

**Request**:
```json
{
  "scenario_name": "TRANSCODER_SURGE"
}
```

**Response `200 OK`**:
```json
{
  "run_id": "1d8b9e11-4a11-4cb3-91ab-6b9a89c41aaa",
  "scenario_name": "TRANSCODER_SURGE",
  "status": "INJECTED",
  "message": "Black Swan injected: 4K/HDR audience surge escalating GPU to 93.4% and queue depth to 48 chunks.",
  "telemetry_delta": {
    "gpu_utilization_pct": 93.4,
    "queue_depth": 48,
    "playback_error_rate_pct": 0.48
  }
}
```

---

### 3.2 `POST /api/v1/demo/black-swan/reset`
Resets simulation and routing back to baseline healthy state.

**Response `200 OK`**:
```json
{
  "status": "RESET_COMPLETE",
  "message": "Media simulation reset to nominal healthy parameters.",
  "telemetry": {
    "gpu_utilization_pct": 65.0,
    "queue_depth": 6,
    "playback_error_rate_pct": 0.41
  }
}
```

---

## 4. Evidentiary Audit Endpoints

### 4.1 `GET /api/v1/evidence/runtime`
Returns an audit log of recent Grafana MCP tool executions across all specialist agents.

**Query Parameters**:
- `limit`: Integer (default 20)
- `agent`: Optional string filter (e.g., `PredictiveRiskAgent`)

**Response `200 OK`**:
```json
[
  {
    "id": "7c1deb4d-1b2d-3cad-8bee-4b0d7b3dcb7f",
    "timestamp": "2026-09-08T07:15:28Z",
    "agent_name": "PredictiveRiskAgent",
    "tool_name": "query_prometheus",
    "datasource": "prometheus",
    "query_metadata": {
      "expr": "transcoder_gpu_utilization_percent"
    },
    "raw_result": {
      "status": "success",
      "data": {
        "resultType": "vector",
        "result": [
          {
            "metric": { "instance": "transcoder-syd-01" },
            "value": [1788851728, "93.4"]
          }
        ]
      }
    }
  }
]
```
