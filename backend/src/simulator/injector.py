from typing import Dict, Any
from src.simulator.media_env import media_env

class IncidentInjector:
    @staticmethod
    def inject_incident(scenario: str = "india_vs_australia_final") -> Dict[str, Any]:
        """Injects deterministic live streaming degradation into the media environment."""
        media_env.trigger_incident()
        return {
            "scenario": scenario,
            "status": "INCIDENT_TRIGGERED",
            "telemetry": media_env.get_telemetry_snapshot(),
            "message": "Incident injected: Playback error rate spiked to 8.7%, transcoder latency increased to 485ms in Australia and Singapore."
        }

    @staticmethod
    def reset_incident() -> Dict[str, Any]:
        """Resets the media environment back to healthy baseline."""
        media_env.reset()
        return {
            "status": "RESET_COMPLETE",
            "telemetry": media_env.get_telemetry_snapshot(),
            "message": "Media simulation reset to healthy state."
        }

    @staticmethod
    def force_failure(enable: bool = True) -> Dict[str, Any]:
        """Forces subsequent remediation to fail verification for testing reinvestigation/escalation."""
        media_env.force_recovery_failure = enable
        return {
            "force_recovery_failure": enable,
            "message": f"Force recovery failure set to {enable}."
        }
