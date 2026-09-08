import httpx
import logging
from typing import Dict, Any, Optional
from src.config import settings
from src.integrations.mock_grafana import mock_grafana_server

logger = logging.getLogger(__name__)

# MCP streamable-http transport headers
_MCP_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

# Mapping: our internal tool names → official Grafana MCP tool names
_TOOL_NAME_MAP = {
    "query_prometheus": "query_prometheus",
    "query_loki_logs": "query_loki_logs",
    "alerting_manage_rules": "alerting_manage_rules",
    "tempo_get-trace": "tempo_get-trace",
    # Legacy aliases for backward compatibility
    "query_prometheus_metrics": "query_prometheus",
    "search_loki_logs": "query_loki_logs",
    "list_grafana_alerts": "alerting_manage_rules",
    "get_tempo_traces": "tempo_get-trace",
}

# Mapping: tool names → mock handler functions
_MOCK_TOOL_MAP = {
    "query_prometheus": "prometheus",
    "query_prometheus_metrics": "prometheus",
    "query_loki_logs": "loki",
    "search_loki_logs": "loki",
    "alerting_manage_rules": "alerts",
    "list_grafana_alerts": "alerts",
    "tempo_get-trace": "tempo",
    "get_tempo_traces": "tempo",
}


class GrafanaMCPClient:
    """
    Model Context Protocol (MCP) client communicating with Grafana MCP server
    over streamable-http transport with transparent mock fallback.

    The streamable-http transport requires:
    1. An `initialize` handshake to get a session ID.
    2. An `initialized` notification to confirm the session.
    3. Tool calls using the session ID in the `Mcp-Session-Id` header.
    """
    def __init__(self):
        self.server_url = settings.GRAFANA_MCP_SERVER_URL
        self.use_mock = settings.USE_MOCK_GRAFANA_MCP
        self._mcp_endpoint = f"{self.server_url}/mcp"
        self._request_id = 0
        self._session_id: Optional[str] = None
        self._initialized = False

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _ensure_initialized(self, client: httpx.AsyncClient) -> bool:
        """Perform the MCP initialize handshake if not already done."""
        if self._initialized and self._session_id:
            return True

        # Step 1: Send initialize request
        init_payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "studio-guardian",
                    "version": "1.0.0"
                }
            }
        }
        res = await client.post(self._mcp_endpoint, json=init_payload, headers=_MCP_HEADERS)
        res.raise_for_status()

        # Extract session ID from response header
        self._session_id = res.headers.get("mcp-session-id")
        if not self._session_id:
            logger.warning("Grafana MCP server did not return a session ID; proceeding without one.")

        # Step 2: Send initialized notification (no id = notification per JSON-RPC)
        session_headers = {**_MCP_HEADERS}
        if self._session_id:
            session_headers["Mcp-Session-Id"] = self._session_id

        notif_payload = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        notif_res = await client.post(self._mcp_endpoint, json=notif_payload, headers=session_headers)
        if notif_res.status_code not in (200, 202, 204):
            logger.warning(f"MCP initialized notification returned unexpected status: {notif_res.status_code}")

        self._initialized = True
        logger.info(f"MCP session established (session_id={self._session_id})")
        return True

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke an MCP tool via JSON-RPC `tools/call`.
        If running in offline or mock mode, routes directly to high-fidelity mock server.
        """
        if self.use_mock:
            return self._call_mock_tool(tool_name, arguments)

        # Resolve to canonical Grafana MCP tool name
        resolved_name = _TOOL_NAME_MAP.get(tool_name, tool_name)

        # Live JSON-RPC invocation over MCP streamable-http transport
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": resolved_name,
                "arguments": arguments
            }
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await self._ensure_initialized(client)

                headers = {**_MCP_HEADERS}
                if self._session_id:
                    headers["Mcp-Session-Id"] = self._session_id

                res = await client.post(self._mcp_endpoint, json=payload, headers=headers)

                # If session was reaped/expired, re-initialize once and retry
                if res.status_code == 404 and "session" in res.text.lower():
                    logger.info("MCP session expired; re-initializing session...")
                    self._session_id = None
                    self._initialized = False
                    await self._ensure_initialized(client)
                    headers["Mcp-Session-Id"] = self._session_id or ""
                    res = await client.post(self._mcp_endpoint, json=payload, headers=headers)

                res.raise_for_status()

                # streamable-http may return SSE-wrapped response; parse accordingly
                raw = res.text
                data = self._parse_mcp_response(raw)

                if "error" in data:
                    logger.error(f"Grafana MCP tool call error: {data['error']}")
                    raise RuntimeError(f"Grafana MCP Error: {data['error']}")

                result = data.get("result", {})
                if result.get("isError"):
                    error_text = ""
                    for item in result.get("content", []):
                        if isinstance(item, dict) and item.get("type") == "text":
                            error_text += item.get("text", "")
                    logger.warning(f"Grafana MCP tool {resolved_name} returned isError: {error_text}")
                    raise RuntimeError(f"Grafana MCP Error: {error_text}")

                return self._unwrap_mcp_result(result)
        except Exception as e:
            logger.warning(f"Failed to reach live Grafana MCP at {self.server_url}: {e}. Falling back to mock MCP server.")
            self._session_id = None
            self._initialized = False
            return self._call_mock_tool(tool_name, arguments)

    def _parse_mcp_response(self, raw: str) -> Dict[str, Any]:
        """Parse MCP response, handling both plain JSON and SSE-wrapped formats."""
        import json
        if raw.strip().startswith("event:") or raw.strip().startswith("data:"):
            for line in raw.strip().split("\n"):
                line = line.strip()
                if line.startswith("data: "):
                    payload = line[6:]
                    try:
                        parsed = json.loads(payload)
                        if "id" in parsed:
                            return parsed
                    except json.JSONDecodeError:
                        continue
            return {}
        else:
            return json.loads(raw)

    def _unwrap_mcp_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unwrap MCP tool result format into the structure our code expects.
        MCP returns: {"content": [{"type": "text", "text": "{...json...}"}]}
        We need the parsed JSON from the text field.
        """
        import json
        content = result.get("content", [])
        if not content:
            return result

        if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
            first = content[0]
            if first.get("type") == "text":
                text = first.get("text", "")
                try:
                    return json.loads(text)
                except (json.JSONDecodeError, TypeError):
                    return {"text": text, "isError": result.get("isError", False)}

        return result

    def _call_mock_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        handler = _MOCK_TOOL_MAP.get(tool_name, tool_name)
        if handler in ("prometheus", "query_prometheus", "query_prometheus_metrics"):
            return mock_grafana_server.query_prometheus(arguments.get("query", arguments.get("expr", "")))
        elif handler in ("loki", "query_loki_logs", "search_loki_logs"):
            return mock_grafana_server.search_loki(
                arguments.get("query", arguments.get("logql", "")),
                arguments.get("limit", 10)
            )
        elif handler in ("tempo", "tempo_get-trace", "get_tempo_traces"):
            return mock_grafana_server.get_tempo_traces(arguments.get("trace_id", arguments.get("traceId", "")))
        elif handler in ("alerts", "alerting_manage_rules", "list_grafana_alerts"):
            return {"alerts": mock_grafana_server.list_alerts(), "rules": mock_grafana_server.list_alerts()}
        else:
            raise ValueError(f"Unknown Grafana MCP tool: {tool_name}")


mcp_client = GrafanaMCPClient()
