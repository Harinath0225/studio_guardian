from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- Phase 6: Observability Investigator Schemas ---

class TelemetryEvidence(BaseModel):
    source: str = Field(description="Source datasource e.g. Prometheus, Loki, Tempo, Alerts")
    signal_name: str = Field(description="Name of metric, log line, span, or alert")
    value: Any = Field(description="Observed value or snippet")
    status: str = Field(description="NORMAL, ELEVATED, CRITICAL, or FIRING")
    timestamp: float = Field(description="Unix epoch timestamp of observation")

class RootCauseHypothesis(BaseModel):
    title: str = Field(description="Concise description of the suspected failure mode")
    component: str = Field(description="Target subsystem e.g. transcoder-syd-01, cdn-edge, origin")
    confidence: float = Field(description="Calculated confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(description="Specific pieces of evidence pointing to this hypothesis")
    recommended_action: str = Field(description="Candidate remediation action e.g. TRAFFIC_SHIFT, RESTART")

class InvestigationInput(BaseModel):
    incident_id: str
    event_title: str
    triggered_at: float
    trigger_reason: str

class InvestigationReport(BaseModel):
    incident_id: str
    observations: List[TelemetryEvidence]
    hypotheses: List[RootCauseHypothesis]
    primary_root_cause: str
    confidence_score: float
    investigation_summary: str

# --- Phase 7: Business Impact Schemas ---

class BusinessImpactInput(BaseModel):
    incident_id: str
    total_viewers: int
    affected_regions: List[str]
    playback_error_rate_pct: float
    incident_duration_seconds: float

class BusinessImpactAssessment(BaseModel):
    incident_id: str
    affected_viewers: int
    affected_vip_viewers: int
    ad_revenue_at_risk_usd: float
    sla_breach_risk: str = Field(description="LOW, MEDIUM, HIGH, or CRITICAL")
    sla_penalty_exposure_usd: float
    executive_summary: str
    recommendation_urgency: str = Field(description="IMMEDIATE, HIGH, NORMAL")

# --- Phase 8: Remediation Schemas ---

class RemediationPlan(BaseModel):
    incident_id: str
    action_type: str = Field(description="TRAFFIC_SHIFT, CONTAINER_RESTART, SCALE_REPLICAS")
    target_component: str
    target_cluster: str
    parameters: Dict[str, Any]
    estimated_blast_radius_pct: float = Field(ge=0.0, le=100.0)
    risk_level: str = Field(description="LOW, MEDIUM, HIGH")
    rationale: str

class RemediationExecutionResult(BaseModel):
    incident_id: str
    action_type: str
    status: str = Field(description="EXECUTED, FAILED, REJECTED")
    details: Dict[str, Any]
    executed_at: float

# --- Phase 10: Verification Schemas ---

class VerificationInput(BaseModel):
    incident_id: str
    action_executed: str
    pre_remediation_error_rate: float
    pre_remediation_latency: float

class VerificationVerdict(BaseModel):
    incident_id: str
    recovered: bool
    current_playback_error_rate_pct: float
    current_transcoder_latency_ms: float
    error_rate_delta_pct: float
    latency_delta_pct: float
    status_summary: str
    recommendation: str = Field(description="RESOLVE_INCIDENT, REINVESTIGATE, or ESCALATE")
