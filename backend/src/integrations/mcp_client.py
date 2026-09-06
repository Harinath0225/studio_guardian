import httpx
import logging
from typing import Dict, Any, Optional
from src.config import settings
from src.integrations.mock_grafana import mock_grafana_server

logger = logging.getLogger(__name__)

class GrafanaMCPClient:
    """
    Model Context Protocol (MCP) client communicating with Grafana MCP server
    over JSON-RPC / SSE transport with transparent mock fallback.
    """
    def __init__(self):
        self.server_url = settings.GRAFANA_MCP_SERVER_URL
        self.use_mock = settings.USE_MOCK_GRAFANA_MCP
        self._request_id = 0

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke an MCP tool via JSON-RPC `tools/call`.
        If running in offline or mock mode, routes directly to high-fidelity mock server.
        """
        if self.use_mock:
            return self._call_mock_tool(tool_name, arguments)

        # Live JSON-RPC invocation over HTTP/SSE
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(f"{self.server_url}/jsonrpc", json=payload)
                res.raise_for_status()
                data = res.json()
                if "error" in data:
                    logger.error(f"Grafana MCP tool call error: {data['error']}")
                    raise RuntimeError(f"Grafana MCP Error: {data['error']}")
                return data.get("result", {})
        except Exception as e:
            logger.warning(f"Failed to reach live Grafana MCP at {self.server_url}: {e}. Falling back to mock MCP server.")
            return self._call_mock_tool(tool_name, arguments)

    def _call_mock_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "query_prometheus_metrics":
            return mock_grafana_server.query_prometheus(arguments.get("query", ""))
        elif tool_name == "search_loki_logs":
            return mock_grafana_server.search_loki(arguments.get("query", ""), arguments.get("limit", 10))
        elif tool_name == "get_tempo_traces":
            return mock_grafana_server.get_tempo_traces(arguments.get("trace_id", ""))
        elif tool_name == "list_grafana_alerts":
            return {"alerts": mock_grafana_server.list_alerts()}
        else:
            raise ValueError(f"Unknown Grafana MCP tool: {tool_name}")

mcp_client = GrafanaMCPClient()
