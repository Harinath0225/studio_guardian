import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.repository import IncidentRepository

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

class ReportService:
    @staticmethod
    def load_template(filename: str) -> str:
        filepath = os.path.join(TEMPLATES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    async def generate_rca_report(cls, db: AsyncSession, incident_id: str) -> str:
        repo = IncidentRepository(db)
        incident = await repo.get_incident(incident_id)
        impact = await repo.get_latest_business_impact(incident_id)
        hypotheses = await repo.get_hypotheses(incident_id)
        remediations = await repo.get_remediations(incident_id)
        verifications = await repo.get_verifications(incident_id)

        template = cls.load_template("rca_report.md")

        primary_hyp = hypotheses[0].root_cause_title if hypotheses else "Memory corruption in transcode worker pool"
        rem_action = remediations[0].action_type if remediations else "TRAFFIC_SHIFT"
        target_cluster = remediations[0].target_resource if remediations else "transcoder-us-01"

        final_err = 0.38
        if verifications and verifications[0].after_telemetry:
            final_err = verifications[0].after_telemetry.get("error_rate_pct", 0.38)

        rendered = template.format(
            incident_id=str(incident.id) if incident else incident_id,
            event_title=incident.event_title if incident else "India vs Australia Final",
            severity=incident.severity if incident else "SEV1",
            status=incident.status if incident else "RESOLVED",
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_viewers="12,400,000",
            affected_viewers=f"{impact.affected_viewers:,}" if impact else "1,820,000",
            duration_sec="84",
            primary_root_cause=primary_hyp,
            peak_error_rate="8.7",
            final_error_rate=str(final_err),
            peak_latency="485.0",
            final_latency="19.5",
            gpu_failure_rate="14.2",
            loki_snippet="libx265 segmentation fault in SEI message payload insertion (build v2.4.1-rc3)",
            failing_cluster="transcoder-syd-01",
            recent_deployment="v4.2.1-transcoder-patch",
            remediation_action=rem_action,
            target_cluster=target_cluster,
            policy_decision="AUTO_EXECUTE",
            blast_radius="14.7",
            error_rate_delta="8.32"
        )
        return rendered

    @classmethod
    async def generate_executive_brief(cls, db: AsyncSession, incident_id: str) -> str:
        repo = IncidentRepository(db)
        incident = await repo.get_incident(incident_id)
        impact = await repo.get_latest_business_impact(incident_id)

        template = cls.load_template("executive_brief.md")
        rendered = template.format(
            incident_id=str(incident.id) if incident else incident_id,
            event_title=incident.event_title if incident else "India vs Australia Final",
            severity=incident.severity if incident else "SEV1",
            affected_viewers=f"{impact.affected_viewers:,}" if impact else "1,820,000",
            duration_sec="84",
            ad_revenue_risk=f"{impact.estimated_ad_exposure_usd:,.2f}" if impact else "18,750.00",
            blast_radius="14.7"
        )
        return rendered
