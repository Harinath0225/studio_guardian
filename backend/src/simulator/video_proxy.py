from typing import Dict, Any
from src.simulator.media_env import media_env

class VideoRoutingProxy:
    @staticmethod
    def shift_traffic(target_cluster: str, shift_pct: float = 100.0) -> Dict[str, Any]:
        """Dispatches an authentic routing change against the simulated video routing proxy."""
        return media_env.apply_traffic_shift(target_cluster=target_cluster, shift_pct=shift_pct)

    @staticmethod
    def get_routing_table() -> Dict[str, Any]:
        return {
            "active_weights": media_env.routing_weights,
            "status": media_env.state.value
        }
