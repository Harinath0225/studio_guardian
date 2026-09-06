"""Initial schema with all 10 entities

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-06

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. incidents
    op.create_table(
        'incidents',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('event_title', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('primary_affected_service', sa.String(100), nullable=True),
        sa.Column('affected_regions', sa.JSON(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=False, default=2),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 2. incident_events
    op.create_table(
        'incident_events',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('incident_id', sa.UUID(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('event_type', sa.String(50), nullable=False, index=True),
        sa.Column('source_agent', sa.String(50), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 3. agent_runs
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('incident_id', sa.UUID(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('agent_name', sa.String(50), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('input_context', sa.JSON(), nullable=False),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('tool_invocations', sa.JSON(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 4. observations
    op.create_table(
        'observations',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('incident_id', sa.UUID(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('agent_run_id', sa.UUID(), sa.ForeignKey('agent_runs.id', ondelete='CASCADE'), nullable=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('baseline_value', sa.Float(), nullable=True),
        sa.Column('observed_value', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(20), nullable=True),
        sa.Column('is_anomaly', sa.Boolean(), nullable=False, default=True),
        sa.Column('raw_telemetry', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 5. root_cause_hypotheses
    op.create_table(
        'root_cause_hypotheses',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('incident_id', sa.UUID(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('root_cause_title', sa.String(255), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('causal_chain', sa.Text(), nullable=False),
        sa.Column('supporting_evidence_ids', sa.JSON(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 6. business_impacts
    op.create_table(
        'business_impacts',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('incident_id', sa.UUID(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('affected_viewers', sa.Integer(), nullable=False, default=0),
        sa.Column('vip_viewers', sa.Integer(), nullable=False, default=0),
        sa.Column('impact_score', sa.Integer(), nullable=False, default=1),
        sa.Column('estimated_ad_exposure_usd', sa.Float(), nullable=False, default=0.0),
        sa.Column('sla_breach_risk', sa.String(20), nullable=False, default='LOW'),
        sa.Column('narrative_summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 7. remediation_actions
    op.create_table(
        'remediation_actions',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('incident_id', sa.UUID(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('target_resource', sa.String(100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('risk_level', sa.String(20), nullable=False, default='LOW'),
        sa.Column('blast_radius_pct', sa.Float(), nullable=False, default=0.0),
        sa.Column('policy_decision', sa.String(30), nullable=False, default='AUTO_EXECUTE'),
        sa.Column('approval_status', sa.String(20), nullable=False, default='NOT_REQUIRED'),
        sa.Column('approved_by', sa.String(100), nullable=True),
        sa.Column('execution_status', sa.String(20), nullable=False, default='PENDING'),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_output', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 8. verification_results
    op.create_table(
        'verification_results',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('incident_id', sa.UUID(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('remediation_action_id', sa.UUID(), sa.ForeignKey('remediation_actions.id'), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('recovery_confidence', sa.Float(), nullable=False),
        sa.Column('before_telemetry', sa.JSON(), nullable=False),
        sa.Column('after_telemetry', sa.JSON(), nullable=False),
        sa.Column('stability_duration_sec', sa.Integer(), nullable=False, default=15),
        sa.Column('verification_summary', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 9. incident_fingerprints
    op.create_table(
        'incident_fingerprints',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('incident_id', sa.UUID(), sa.ForeignKey('incidents.id', ondelete='CASCADE'), nullable=True),
        sa.Column('symptom_signature', sa.JSON(), nullable=False),
        sa.Column('root_cause_summary', sa.String(255), nullable=False),
        sa.Column('successful_action_type', sa.String(50), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 10. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('actor', sa.String(100), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(100), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('incident_fingerprints')
    op.drop_table('verification_results')
    op.drop_table('remediation_actions')
    op.drop_table('business_impacts')
    op.drop_table('root_cause_hypotheses')
    op.drop_table('observations')
    op.drop_table('agent_runs')
    op.drop_table('incident_events')
    op.drop_table('incidents')
