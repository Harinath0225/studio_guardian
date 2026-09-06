from typing import Dict, Any, List
from pydantic import BaseModel

class IncidentFingerprintSchema(BaseModel):
    symptom_signature: Dict[str, Any]
    root_cause_summary: str
    successful_action_type: str
    tags: List[str]

class IncidentMemoryEngine:
    @staticmethod
    def extract_signature(
        error_rate_pct: float,
        latency_ms: float,
        failing_component: str,
        recent_deployment: str
    ) -> Dict[str, Any]:
        return {
            "error_rate_category": "CRITICAL" if error_rate_pct > 5.0 else "ELEVATED",
            "latency_category": "STALLED" if latency_ms > 1000 else "ELEVATED",
            "failing_component": failing_component,
            "has_recent_deployment": bool(recent_deployment)
        }

incident_memory_engine = IncidentMemoryEngine()
