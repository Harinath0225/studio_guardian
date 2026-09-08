from typing import Set
from enum import Enum

class RemediationActionType(str, Enum):
    TRAFFIC_SHIFT = "TRAFFIC_SHIFT"
    CONTAINER_RESTART = "CONTAINER_RESTART"
    SCALE_REPLICAS = "SCALE_REPLICAS"

# Strict allowlist of permissible autonomous / controlled actions
ALLOWLISTED_ACTIONS: Set[str] = {
    RemediationActionType.TRAFFIC_SHIFT.value,
    RemediationActionType.CONTAINER_RESTART.value,
    RemediationActionType.SCALE_REPLICAS.value
}

# Allowlisted actions for predictive proactive prevention
PREDICTIVE_ALLOWLISTED_ACTIONS: Set[str] = {
    "scale_transcoder_pool",
    "SCALE_TRANSCODER_POOL",
    "prewarm_failover_nodes",
    "PREWARM_FAILOVER_NODES",
    "traffic_shed_noncritical",
    "TRAFFIC_SHED_NONCRITICAL",
    RemediationActionType.SCALE_REPLICAS.value,
    RemediationActionType.TRAFFIC_SHIFT.value,
}

# Explicitly disallowed mutating operations
FORBIDDEN_ACTIONS: Set[str] = {
    "DATABASE_DROP",
    "FLUSH_ALL_KEYS",
    "TERMINATE_ORIGIN_CLUSTER",
    "GLOBAL_DNS_PURGE"
}

