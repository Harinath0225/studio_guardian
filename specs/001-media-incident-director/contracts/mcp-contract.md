# Grafana Model Context Protocol (MCP) Contract: Studio Guardian

**Feature**: `001-media-incident-director`  
**Partner Integration**: Grafana Labs (MCP)  
**Protocol Version**: MCP 2024-11-05 (JSON-RPC 2.0)  
**Status**: Completed  

---

## 1. Protocol & Transport Overview

The Observability Investigator agent acts as an MCP client interacting with a Grafana MCP server:
- **Local Dev / Standalone**: Connects via `stdio` transport to the local Grafana MCP process or internal mock emitter.
- **Production / Cloud**: Connects via `sse` (Server-Sent Events) or `http` transport to Grafana Cloud with `GRAFANA_URL` and `GRAFANA_SERVICE_ACCOUNT_TOKEN`.

---

## 2. Tool Definitions

### Tool 1: `query_prometheus_metrics`

Executes PromQL instant and range queries against Grafana Prometheus datasource.

```json
{
  "name": "query_prometheus_metrics",
  "description": "Execute a PromQL query to retrieve streaming infrastructure metrics (playback error rates, transcoding latency, GPU allocation)",
  "inputSchema": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": {
        "type": "string",
        "description": "PromQL expression, e.g. sum(rate(playback_errors_total[1m])) / sum(rate(playback_attempts_total[1m]))"
      },
      "range_minutes": {
        "type": "integer",
        "default": 15,
        "description": "Minutes of history to fetch"
      },
      "step_seconds": {
        "type": "integer",
        "default": 15,
        "description": "Sampling interval in seconds"
      }
    }
  }
}
```

### Tool 2: `search_loki_logs`

Executes LogQL queries to search container and service logs in Grafana Loki.

```json
{
  "name": "search_loki_logs",
  "description": "Execute a LogQL query to search logs for deployment events, GPU driver errors, or transcoding process panics",
  "inputSchema": {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": {
        "type": "string",
        "description": "LogQL query expression, e.g. {app=\"live-transcoder\"} |= \"error\""
      },
      "limit": {
        "type": "integer",
        "default": 50,
        "description": "Maximum log entries to return"
      }
    }
  }
}
```

### Tool 3: `get_tempo_traces`

Fetches distributed trace spans from Grafana Tempo for stream chunk processing.

```json
{
  "name": "get_tempo_traces",
  "description": "Retrieve distributed trace spans to identify latency bottlenecks in media pipeline stages",
  "inputSchema": {
    "type": "object",
    "required": ["service_name"],
    "properties": {
      "service_name": {
        "type": "string",
        "description": "Target service name (e.g. video-packager, live-transcoder)"
      },
      "min_duration_ms": {
        "type": "integer",
        "default": 200,
        "description": "Filter spans exceeding duration in milliseconds"
      }
    }
  }
}
```

### Tool 4: `list_grafana_alerts`

Pulls currently firing or pending alert rules.

```json
{
  "name": "list_grafana_alerts",
  "description": "List firing alerts from the Grafana Alerting engine",
  "inputSchema": {
    "type": "object",
    "properties": {
      "state": {
        "type": "string",
        "enum": ["firing", "pending", "all"],
        "default": "firing"
      }
    }
  }
}
```
