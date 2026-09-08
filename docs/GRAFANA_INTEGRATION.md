# Grafana MCP Integration & Telemetry Architecture

## Partner Architecture Overview
Grafana serves as the operational source of truth in Studio Guardian. The evidence path is:
`Simulated Media Environment -> Prometheus / Loki / Tempo -> Grafana -> Grafana MCP Server -> Studio Guardian Agents`

## MCP Transport & Connection Details
- **Protocol**: Model Context Protocol (MCP)
- **Transport**: `streamable-http`
- **Default Endpoint**: `http://localhost:8001/mcp`
- **Session Management**: Each agent run establishes an authenticated session maintaining continuity via `Mcp-Session-Id` headers.
- **Authentication**: Local unauthenticated connection or managed Bearer Token via `GRAFANA_SERVICE_ACCOUNT_TOKEN`.

## Supported MCP Tools
1. `query_prometheus`: Instant and range queries across operational metrics (`container_gpu_utilization_pct`, `transcoder_processing_latency_seconds`, `transcoder_queue_depth_total`, `stream_playback_error_rate_pct`).
2. `query_loki_logs`: Log analysis across transcoder pods for stacktraces and SCTE-35 parse anomalies.
3. `alerting_manage_rules`: Reading and reconciling alert rule state.
4. `tempo_get-trace`: Distributed span inspection across media pipeline segment packaging.

## Relational Telemetry & Audit Persistence
All raw Grafana MCP tool responses are recorded in the relational database (`prediction_evidence` and `runtime_evidence` tables) with:
- Target datasource identifier
- Precise query expression
- Execution latency (ms)
- Exact ISO UTC timestamp
- Raw payload preserved verbatim for mathematical provenance