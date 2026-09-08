import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from src.persistence.database import Base

# Universal UUID type helper
UUID_TYPE = PG_UUID(as_uuid=True)
JSON_TYPE = JSONB().with_variant(JSON(), "sqlite")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    event_title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, index=True, default="HEALTHY")
    severity = Column(String(20), nullable=False, default="SEV1")
    primary_affected_service = Column(String(100), nullable=True)
    affected_regions = Column(JSON_TYPE, nullable=False, default=list)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=2)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentEvent.created_at")
    agent_runs = relationship("AgentRun", back_populates="incident", cascade="all, delete-orphan", order_by="AgentRun.started_at")
    observations = relationship("Observation", back_populates="incident", cascade="all, delete-orphan")
    hypotheses = relationship("RootCauseHypothesis", back_populates="incident", cascade="all, delete-orphan")
    business_impacts = relationship("BusinessImpact", back_populates="incident", cascade="all, delete-orphan")
    remediations = relationship("RemediationAction", back_populates="incident", cascade="all, delete-orphan")
    verifications = relationship("VerificationResult", back_populates="incident", cascade="all, delete-orphan")
    fingerprints = relationship("IncidentFingerprint", back_populates="incident", cascade="all, delete-orphan")


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID_TYPE, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    source_agent = Column(String(50), nullable=True)
    summary = Column(Text, nullable=False)
    payload = Column(JSON_TYPE, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="events")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID_TYPE, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="STARTED")
    input_context = Column(JSON_TYPE, nullable=False, default=dict)
    output_data = Column(JSON_TYPE, nullable=True)
    tool_invocations = Column(JSON_TYPE, nullable=False, default=list)
    duration_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    incident = relationship("Incident", back_populates="agent_runs")
    observations = relationship("Observation", back_populates="agent_run", cascade="all, delete-orphan")


class Observation(Base):
    __tablename__ = "observations"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID_TYPE, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_run_id = Column(UUID_TYPE, ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=True)
    source = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    baseline_value = Column(Float, nullable=True)
    observed_value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    is_anomaly = Column(Boolean, nullable=False, default=True)
    raw_telemetry = Column(JSON_TYPE, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="observations")
    agent_run = relationship("AgentRun", back_populates="observations")


class RootCauseHypothesis(Base):
    __tablename__ = "root_cause_hypotheses"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID_TYPE, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    root_cause_title = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    causal_chain = Column(Text, nullable=False)
    supporting_evidence_ids = Column(JSON_TYPE, nullable=False, default=list)
    is_primary = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="hypotheses")


class BusinessImpact(Base):
    __tablename__ = "business_impacts"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID_TYPE, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    affected_viewers = Column(Integer, nullable=False, default=0)
    vip_viewers = Column(Integer, nullable=False, default=0)
    impact_score = Column(Integer, nullable=False, default=1)
    estimated_ad_exposure_usd = Column(Float, nullable=False, default=0.0)
    sla_breach_risk = Column(String(20), nullable=False, default="LOW")
    narrative_summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="business_impacts")


class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID_TYPE, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    target_resource = Column(String(100), nullable=False)
    parameters = Column(JSON_TYPE, nullable=False, default=dict)
    risk_level = Column(String(20), nullable=False, default="LOW")
    blast_radius_pct = Column(Float, nullable=False, default=0.0)
    policy_decision = Column(String(30), nullable=False, default="AUTO_EXECUTE")
    approval_status = Column(String(20), nullable=False, default="NOT_REQUIRED")
    approved_by = Column(String(100), nullable=True)
    execution_status = Column(String(20), nullable=False, default="PENDING")
    executed_at = Column(DateTime(timezone=True), nullable=True)
    execution_output = Column(JSON_TYPE, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="remediations")
    verifications = relationship("VerificationResult", back_populates="remediation_action")


class VerificationResult(Base):
    __tablename__ = "verification_results"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID_TYPE, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    remediation_action_id = Column(UUID_TYPE, ForeignKey("remediation_actions.id"), nullable=True)
    status = Column(String(20), nullable=False)
    recovery_confidence = Column(Float, nullable=False)
    before_telemetry = Column(JSON_TYPE, nullable=False, default=dict)
    after_telemetry = Column(JSON_TYPE, nullable=False, default=dict)
    stability_duration_sec = Column(Integer, nullable=False, default=15)
    verification_summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="verifications")
    remediation_action = relationship("RemediationAction", back_populates="verifications")


class IncidentFingerprint(Base):
    __tablename__ = "incident_fingerprints"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID_TYPE, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True)
    symptom_signature = Column(JSON_TYPE, nullable=False, default=dict)
    root_cause_summary = Column(String(255), nullable=False)
    successful_action_type = Column(String(50), nullable=False)
    tags = Column(JSON_TYPE, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    incident = relationship("Incident", back_populates="fingerprints")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    actor = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=False)
    details = Column(JSON_TYPE, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


# ─── PREDICTIVE PREVENTION ENTITIES ───────────────────────────────────────────

class PredictiveSnapshot(Base):
    __tablename__ = "predictive_snapshots"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    sampled_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    channel_id = Column(String(100), nullable=False, default="star-sports-hindi")
    region = Column(String(50), nullable=False, default="ap-south-1")

    # Raw metrics
    gpu_utilization_raw = Column(Float, nullable=False, default=0.0)
    transcoder_latency_raw = Column(Float, nullable=False, default=0.0)
    queue_depth_raw = Column(Integer, nullable=False, default=0)
    playback_error_rate_raw = Column(Float, nullable=False, default=0.0)
    active_viewers_raw = Column(Integer, nullable=False, default=0)

    # Normalized metrics [0.0 - 1.0]
    gpu_utilization_norm = Column(Float, nullable=False, default=0.0)
    transcoder_latency_norm = Column(Float, nullable=False, default=0.0)
    queue_growth_slope = Column(Float, nullable=False, default=0.0)
    error_growth_slope = Column(Float, nullable=False, default=0.0)
    viewer_growth_slope = Column(Float, nullable=False, default=0.0)
    regional_saturation_norm = Column(Float, nullable=False, default=0.0)
    deployment_risk_norm = Column(Float, nullable=False, default=0.0)

    # Relationships
    evidence = relationship("PredictionEvidence", back_populates="snapshot", cascade="all, delete-orphan")
    decision = relationship("PredictionDecision", back_populates="snapshot", uselist=False, cascade="all, delete-orphan")


class PredictionEvidence(Base):
    __tablename__ = "prediction_evidence"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(UUID_TYPE, ForeignKey("predictive_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    queried_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    tool_name = Column(String(100), nullable=False)
    query_expression = Column(Text, nullable=False)
    raw_response = Column(JSON_TYPE, nullable=False, default=dict)
    query_duration_ms = Column(Float, nullable=False, default=0.0)
    provider_source = Column(String(50), nullable=False, default="MOCK_GRAFANA_MCP")

    snapshot = relationship("PredictiveSnapshot", back_populates="evidence")


class PredictionDecision(Base):
    __tablename__ = "prediction_decisions"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(UUID_TYPE, ForeignKey("predictive_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    decided_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    risk_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String(50), nullable=False, default="HEALTHY")
    confidence_score = Column(Float, nullable=False, default=0.0)
    risk_contributors = Column(JSON_TYPE, nullable=False, default=list)
    predicted_failure_mode = Column(String(100), nullable=True)
    window_minutes_min = Column(Integer, nullable=True)
    window_minutes_max = Column(Integer, nullable=True)
    failure_hypothesis = Column(Text, nullable=True)
    reasoning_summary = Column(Text, nullable=True)
    agent_session_id = Column(String(100), nullable=True)
    runtime_metadata = Column(JSON_TYPE, nullable=False, default=dict)

    snapshot = relationship("PredictiveSnapshot", back_populates="decision")
    action = relationship("PreventionAction", back_populates="decision", uselist=False, cascade="all, delete-orphan")


class PreventionAction(Base):
    __tablename__ = "prevention_actions"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    decision_id = Column(UUID_TYPE, ForeignKey("prediction_decisions.id", ondelete="CASCADE"), nullable=False, index=True)
    dispatched_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    action_type = Column(String(100), nullable=False)
    target_service = Column(String(100), nullable=False)
    action_parameters = Column(JSON_TYPE, nullable=False, default=dict)
    blast_radius_pct = Column(Float, nullable=False, default=0.0)
    expected_loss_without_action = Column(Float, nullable=False, default=0.0)
    cost_of_prevention = Column(Float, nullable=False, default=0.0)
    expected_avoided_exposure = Column(Float, nullable=False, default=0.0)
    policy_verdict = Column(String(50), nullable=False, default="AUTO_EXECUTE")
    authorization_tier = Column(String(50), nullable=False, default="AUTONOMOUS")
    operator_id = Column(String(100), nullable=True)
    execution_status = Column(String(50), nullable=False, default="PENDING")
    completed_at = Column(DateTime(timezone=True), nullable=True)

    decision = relationship("PredictionDecision", back_populates="action")
    verification = relationship("PreventionVerification", back_populates="action", uselist=False, cascade="all, delete-orphan")


class PreventionVerification(Base):
    __tablename__ = "prevention_verifications"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    action_id = Column(UUID_TYPE, ForeignKey("prevention_actions.id", ondelete="CASCADE"), nullable=False, index=True)
    verified_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    risk_score_before = Column(Float, nullable=False)
    risk_score_after = Column(Float, nullable=False)
    gpu_before = Column(Float, nullable=False)
    gpu_after = Column(Float, nullable=False)
    latency_before = Column(Float, nullable=False)
    latency_after = Column(Float, nullable=False)
    error_rate_before = Column(Float, nullable=False)
    error_rate_after = Column(Float, nullable=False)
    verification_verdict = Column(String(50), nullable=False, default="PREVENTION_VERIFIED")
    net_avoided_loss = Column(Float, nullable=False, default=0.0)
    estimated_viewers_protected = Column(Integer, nullable=False, default=0)

    @property
    def delta_gpu_utilization(self) -> float:
        return self.gpu_after - self.gpu_before

    @property
    def verified_successful(self) -> bool:
        return self.verification_verdict in ("PREVENTION_VERIFIED", "VERIFIED_SUCCESSFUL")

    action = relationship("PreventionAction", back_populates="verification")
    fingerprint = relationship("PredictionFingerprint", back_populates="verification", uselist=False, cascade="all, delete-orphan")


class PredictionFingerprint(Base):
    __tablename__ = "prediction_fingerprints"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID_TYPE, ForeignKey("prevention_verifications.id", ondelete="CASCADE"), nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    service_name = Column(String(100), nullable=False)
    failure_pattern = Column(String(100), nullable=False)
    signature_signals = Column(JSON_TYPE, nullable=False, default=dict)
    proven_action = Column(String(100), nullable=False)
    times_applied = Column(Integer, nullable=False, default=1)
    success_rate = Column(Float, nullable=False, default=1.0)

    verification = relationship("PreventionVerification", back_populates="fingerprint")


class MediaQualityEvent(Base):
    __tablename__ = "media_quality_events"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    stream_id = Column(String(100), nullable=False, default="star-sports-live")
    av_sync_drift_ms = Column(Float, nullable=False, default=0.0)
    loudness_lufs = Column(Float, nullable=False, default=-24.0)
    loudness_deviation_lufs = Column(Float, nullable=False, default=0.0)
    frame_drop_ratio_pct = Column(Float, nullable=False, default=0.0)
    black_frame_ratio_pct = Column(Float, nullable=False, default=0.0)
    is_anomaly = Column(Boolean, nullable=False, default=False)
    severity = Column(String(20), nullable=False, default="INFO")
    details = Column(JSON_TYPE, nullable=False, default=dict)


class AdIntegrityEvent(Base):
    __tablename__ = "ad_integrity_events"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    stream_id = Column(String(100), nullable=False, default="star-sports-live")
    scte_timing_drift_ms = Column(Float, nullable=False, default=0.0)
    splice_alignment_error_ms = Column(Float, nullable=False, default=0.0)
    ad_pod_drop_pct = Column(Float, nullable=False, default=0.0)
    tracking_error_ratio = Column(Float, nullable=False, default=0.0)
    operational_tolerance_ms = Column(Float, nullable=False, default=200.0)
    is_anomaly = Column(Boolean, nullable=False, default=False)
    severity = Column(String(20), nullable=False, default="INFO")
    estimated_ad_exposure_usd = Column(Float, nullable=False, default=0.0)
    details = Column(JSON_TYPE, nullable=False, default=dict)


class BlackSwanRun(Base):
    __tablename__ = "black_swan_runs"

    id = Column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    scenario_name = Column(String(100), nullable=False, index=True)
    injected_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    triggered_by = Column(String(100), nullable=False, default="operator")
    status = Column(String(50), nullable=False, default="INJECTED")
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    initial_telemetry = Column(JSON_TYPE, nullable=False, default=dict)
    final_telemetry = Column(JSON_TYPE, nullable=True)

