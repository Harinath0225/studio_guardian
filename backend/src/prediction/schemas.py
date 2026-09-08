from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SignalContributor(BaseModel):
    name: str = Field(..., description="Signal key name")
    label: str = Field(..., description="Human-readable signal label")
    raw_value: float = Field(..., description="Original sensor/metric value")
    normalized: float = Field(..., ge=0.0, le=1.0, description="Normalized score [0.0, 1.0]")
    points: float = Field(..., ge=0.0, le=100.0, description="Contribution to total risk points")


class FailureWindow(BaseModel):
    min: int = Field(..., description="Earliest estimated failure horizon in minutes")
    max: int = Field(..., description="Latest estimated failure horizon in minutes")


class PreventionProposalResponse(BaseModel):
    id: str
    action_type: str
    target_service: str
    blast_radius_pct: float
    expected_loss_without_action: float
    cost_of_prevention: float
    expected_avoided_exposure: float
    policy_verdict: str
    status: str
    requires_approval: bool = False


class RuntimeMetadata(BaseModel):
    agent_engine: str = "Vertex AI (gemini-2.5-flash)"
    agent_runtime: str = "Vertex AI Agent Engine"
    active_agent: str = "Predictive Risk Agent"
    current_specialist: str = "Predictive Risk Agent"
    session_id: str
    agent_state: str = "EVALUATED"
    telemetry_source: str = "LIVE_GRAFANA_MCP"
    execution_frames: List[Dict[str, Any]] = []


class PredictiveStatusResponse(BaseModel):
    state: str = Field(..., description="Operating state: HEALTHY, WATCH, ELEVATED_RISK, HIGH_RISK, IMMINENT_RISK, PREVENTED")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Composite risk score [0.0, 1.0]")
    risk_level: str = Field(..., description="Categorical tier: LOW, MEDIUM, HIGH, CRITICAL")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Statistical/data confidence [0.0, 1.0]")
    predicted_failure_mode: Optional[str] = None
    estimated_window_minutes: Optional[FailureWindow] = None
    contributors: List[SignalContributor] = []
    failure_hypothesis: Optional[str] = None
    reasoning_summary: Optional[str] = None
    active_proposal: Optional[PreventionProposalResponse] = None
    runtime_metadata: RuntimeMetadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EvaluateRequest(BaseModel):
    force_telemetry_refresh: bool = False


class AuthorizeProposalRequest(BaseModel):
    operator_id: str = "sre-director"
    notes: Optional[str] = None


class AuthorizeProposalResponse(BaseModel):
    action_id: str
    status: str
    dispatched_at: datetime
    message: str


class DemoScenarioRequest(BaseModel):
    scenario: str = "transcoder_saturation_surge"
    step: int = Field(..., ge=1, le=4, description="Step 1 to 4 in rising-risk scenario")


class TelemetryComparison(BaseModel):
    risk_score: Dict[str, float]
    gpu_utilization_pct: Dict[str, float]
    transcoder_latency_ms: Dict[str, float]
    playback_error_rate_pct: Dict[str, float]


class CounterfactualEstimate(BaseModel):
    projected_risk_reduction: str
    estimated_exposure_avoided: float
    estimated_viewers_protected: int


class VerificationResponse(BaseModel):
    action_id: str
    verdict: str
    comparison: TelemetryComparison
    counterfactual: CounterfactualEstimate
    verified_at: datetime = Field(default_factory=datetime.utcnow)
