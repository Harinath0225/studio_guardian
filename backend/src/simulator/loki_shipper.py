import httpx
import time
import logging
from typing import Dict, Any, List
from src.config import settings

logger = logging.getLogger(__name__)

class GrafanaLokiShipper:
    """
    Direct HTTP log shipper pushing live broadcast & sentinel logs to Grafana Cloud Loki.
    Endpoint: POST /loki/api/v1/push
    Authentication: Basic Auth (Loki User ID, Cloud Access Policy Token with 'logs:write' scope)
    """
    def __init__(self):
        self.url = settings.GRAFANA_LOKI_URL
        self.user_id = settings.GRAFANA_LOKI_USER_ID
        self.token = settings.GRAFANA_LOKI_TOKEN or settings.GRAFANA_SERVICE_ACCOUNT_TOKEN

    async def push_logs(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Pushes structured log entries to Grafana Cloud Loki."""
        if not self.url or not self.token or not self.user_id:
            return {
                "status": "SKIPPED",
                "message": "Loki push not configured. Set GRAFANA_LOKI_TOKEN in .env (requires Cloud Access Policy token with logs:write)."
            }

        now_ns = str(time.time_ns())
        streams = []

        for entry in log_entries:
            service = entry.get("service", "media-pipeline")
            level = entry.get("level", "INFO").lower()
            msg = entry.get("message", "")

            streams.append({
                "stream": {
                    "app": "media-pipeline",
                    "service": service,
                    "level": level,
                    "cluster": "ap-south-1"
                },
                "values": [
                    [now_ns, msg]
                ]
            })

        payload = {"streams": streams}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    self.url,
                    auth=(self.user_id, self.token),
                    json=payload
                )

                if res.status_code in [200, 204]:
                    return {"status": "SUCCESS", "code": res.status_code, "count": len(log_entries)}
                elif res.status_code == 401:
                    return {
                        "status": "AUTH_FAILED",
                        "code": 401,
                        "error": "Grafana Cloud Loki rejected the token. Note: Grafana UI Service Account tokens (glsa_...) do not have logs:write permissions. A Cloud Access Policy token (glc_...) is required."
                    }
                else:
                    return {
                        "status": "ERROR",
                        "code": res.status_code,
                        "error": res.text
                    }
        except Exception as e:
            return {"status": "NETWORK_ERROR", "error": str(e)}

    async def test_connection(self) -> Dict[str, Any]:
        """Performs a self-test push of a single heartbeat log line to diagnose connection."""
        test_line = [{
            "service": "studio-guardian-diagnostics",
            "level": "INFO",
            "message": "Studio Guardian diagnostics heartbeat probe"
        }]
        return await self.push_logs(test_line)

loki_shipper = GrafanaLokiShipper()
