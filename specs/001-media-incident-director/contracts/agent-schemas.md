# Agent Structured Schemas Contract: Studio Guardian

**Feature**: `001-media-incident-director`  
**Framework**: Google GenAI SDK / Pydantic v2  
**Status**: Completed  

---

## 1. Observability Investigator

### Input Schema: `InvestigationInput`
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class InvestigationInput(BaseModel):
    incident_id: UUID
    event_title: str
    degraded_metric: str
    observed_value: float
    affected_regions: List[str]
    lookback_minutes: int = Field(default=15, description="Minutes of telemetry history to inspect")
```

### Output Schema: `InvestigationReport`
```python
class TelemetryAnomaly(BaseModel):
    source: str = Field(description="grafana_prometheus, grafana_loki, etc.")
    metric_or_log: str
    baseline: float
    observed: float
    unit: str
    summary: str

class InvestigationReport(BaseModel):
    incident_id: UUID
    anomalies: List[TelemetryAnomaly]
    correlated_deployment: Optional[str] = Field(None, description="Recent deployment identifier if found")
    primary_faulty_component: str
    preliminary_confidence: float = Field(ge=0.0, le=1.0)
    natural_language_evidence: str = Field(description="Concise evidence summary without private CoT")
```

---

## 2. Root Cause Correlator / Incident Commander

### Output Schema: `HypothesisResult`
```python
class HypothesisResult(BaseModel):
    root_cause_title: str
    primary_component: str
    confidence: float = Field(ge=0.0, le=1.0)
    causal_chain: str = Field(description="Step-by-step causal linkage grounded in evidence")
    recommended_action_type: str = Field(description="TRAFFIC_SHIFT, CONTAINER_RESTART, SCALE_REPLICAS")
    recommended_parameters: dict
```

---

## 3. Business Impact Agent

### Input Schema: `BusinessImpactInput`
```python
class BusinessImpactInput(BaseModel):
    incident_id: UUID
    event_title: str
    total_event_viewers: int
    affected_regions: List[str]
    error_rate_pct: float
```

### Output Schema: `BusinessImpactAssessment`
```python
class BusinessImpactAssessment(BaseModel):
    incident_id: UUID
    affected_viewers: int
    vip_viewers: int
    impact_score: int = Field(ge=1, le=100)
    estimated_ad_exposure_usd: float
    sla_breach_risk: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL")
    ad_window_active: bool
    executive_narrative: str
```

---

## 4. Remediation Agent & Safety Director

### Input Schema: `SafetyEvaluationInput`
```python
class SafetyEvaluationInput(BaseModel):
    incident_id: UUID
    action_type: str
    target_resource: str
    parameters: dict
    diagnostic_confidence: float
    affected_viewers_pct: float
```

### Output Schema: `SafetyPolicyDecision`
```python
class SafetyPolicyDecision(BaseModel):
    action_type: str
    target_resource: str
    blast_radius_pct: float
    risk_level: str = Field(description="LOW, MEDIUM, HIGH")
    decision: str = Field(description="AUTO_EXECUTE, HUMAN_APPROVAL_REQUIRED, BLOCKED")
    policy_rule_triggered: str
    justification: str
```

### Execution Output: `RemediationExecutionResult`
```python
class RemediationExecutionResult(BaseModel):
    action_id: UUID
    status: str = Field(description="COMPLETED, FAILED")
    dispatched_at: str
    duration_ms: int
    target_response: dict
    error_message: Optional[str] = None
```

---

## 5. Verification Agent

### Input Schema: `VerificationInput`
```python
class VerificationInput(BaseModel):
    incident_id: UUID
    remediation_action_id: UUID
    expected_healthy_metric: str
    healthy_threshold: float
    stability_duration_sec: int = Field(default=15)
```

### Output Schema: `VerificationVerdict`
```python
class VerificationVerdict(BaseModel):
    incident_id: UUID
    status: str = Field(description="VERIFIED_HEALTHY, RECOVERY_FAILED, INCONCLUSIVE")
    recovery_confidence: float = Field(ge=0.0, le=1.0)
    pre_remediation_value: float
    post_remediation_value: float
    summary: str
    recommended_workflow_action: str = Field(description="RESOLVE, REINVESTIGATE, ESCALATE")
```
