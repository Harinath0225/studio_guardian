from typing import Dict, Any, List, Optional
from src.integrations.mcp_client import mcp_client

async def query_prometheus_metrics(query: str) -> Dict[str, Any]:
    """
    Executes a PromQL metric query via Grafana MCP datasource adapter.
    """
    return await mcp_client.call_tool(
        tool_name="query_prometheus_metrics",
        arguments={"query": query}
    )

async def search_loki_logs(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Searches Loki log streams via Grafana MCP datasource adapter.
    """
    return await mcp_client.call_tool(
        tool_name="search_loki_logs",
        arguments={"query": query, "limit": limit}
    )

async def get_tempo_traces(trace_id: str = "") -> Dict[str, Any]:
    """
    Retrieves distributed trace spans via Grafana MCP datasource adapter.
    """
    return await mcp_client.call_tool(
        tool_name="get_tempo_traces",
        arguments={"trace_id": trace_id}
    )

async def list_grafana_alerts() -> List[Dict[str, Any]]:
    """
    Lists active alerts and evaluations from Grafana Alerting via MCP.
    """
    result = await mcp_client.call_tool(
        tool_name="list_grafana_alerts",
        arguments={}
    )
    return result.get("alerts", [])
