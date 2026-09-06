from typing import Optional, Dict, Any
from pydantic import BaseModel
from src.config import settings

class GrafanaSettings(BaseModel):
    grafana_url: str = settings.GRAFANA_URL
    service_account_token: str = settings.GRAFANA_SERVICE_ACCOUNT_TOKEN
    mcp_server_url: str = settings.GRAFANA_MCP_SERVER_URL
    use_mock: bool = settings.USE_MOCK_GRAFANA_MCP

grafana_settings = GrafanaSettings()
