from typing import Dict, Any
from src.agents.base import BaseAgent
from src.agents.schemas import BusinessImpactInput, BusinessImpactAssessment

class BusinessImpactAgent(BaseAgent):
    """
    Business Impact Specialist Agent.
    Responsibilities:
    1. Calculate deterministic broadcast and business blast metrics (affected viewers, VIPs, ad revenue exposure, SLA risk).
    2. Synthesize an executive-ready natural language brief using Gemini 2.5 structured generation.
    """
    def __init__(self):
        super().__init__(
            name="BusinessImpactAgent",
            role_description="Calculates broadcast audience disruption, ad revenue burn rate, and SLA liability"
        )

        # Baseline business parameters for live cricket final
        self.cpm_usd = 28.50 # $28.50 CPM for premium live sports
        self.ad_impressions_per_hour_per_user = 12.0
        self.vip_tier_percentage = 0.04 # 4% VIP subscribers (4K/Dolby Atmos tier)
        self.sla_tier_threshold_error_pct = 2.0 # 2.0% playback error SLA threshold
        self.hourly_sla_penalty_usd = 75_000.0

    def get_system_instruction(self) -> str:
        return (
            "You are the Studio Guardian Business Impact Agent. "
            "Your objective is to translate live streaming operational degradation into commercial terms: "
            "quantify audience disruption, high-value subscriber churn risk, immediate ad revenue at risk, "
            "and contractual broadcast SLA penalties. "
            "Deliver crisp, high-stakes operational summaries suitable for executive incident directors."
        )

    def calculate_deterministic_metrics(self, input_data: BusinessImpactInput) -> Dict[str, Any]:
        """
        Calculates exact mathematical figures without relying on LLM arithmetic.
        """
        # Affected viewers based on error rate and regional weighting
        error_ratio = min(1.0, max(0.0, input_data.playback_error_rate_pct / 100.0))
        # Affected viewers calculation
        affected_viewers = int(input_data.total_viewers * error_ratio * (len(input_data.affected_regions) / 4.0 if input_data.affected_regions else 0.25))
        affected_viewers = min(input_data.total_viewers, max(0, affected_viewers))

        affected_vips = int(affected_viewers * self.vip_tier_percentage)

        # Ad revenue at risk: (viewers * ad_frequency * duration_hours * CPM / 1000)
        duration_hours = max(0.0, input_data.incident_duration_seconds / 3600.0)
        ad_impressions_missed = affected_viewers * (self.ad_impressions_per_hour_per_user * duration_hours)
        ad_revenue_at_risk = round((ad_impressions_missed / 1000.0) * self.cpm_usd, 2)

        # SLA exposure
        if input_data.playback_error_rate_pct >= 5.0:
            sla_risk = "CRITICAL"
            sla_penalty = round(self.hourly_sla_penalty_usd * max(0.5, duration_hours), 2)
            urgency = "IMMEDIATE"
        elif input_data.playback_error_rate_pct >= self.sla_tier_threshold_error_pct:
            sla_risk = "HIGH"
            sla_penalty = round((self.hourly_sla_penalty_usd * 0.5) * max(0.25, duration_hours), 2)
            urgency = "HIGH"
        else:
            sla_risk = "LOW"
            sla_penalty = 0.0
            urgency = "NORMAL"

        return {
            "affected_viewers": affected_viewers,
            "affected_vip_viewers": affected_vips,
            "ad_revenue_at_risk_usd": ad_revenue_at_risk,
            "sla_breach_risk": sla_risk,
            "sla_penalty_exposure_usd": sla_penalty,
            "recommendation_urgency": urgency
        }

    async def assess_impact(self, input_data: BusinessImpactInput) -> BusinessImpactAssessment:
        metrics = self.calculate_deterministic_metrics(input_data)

        prompt = (
            f"Assess commercial and broadcast impact for Incident {input_data.incident_id}.\n"
            f"Key Telemetry & Math Metrics:\n"
            f"- Total Concurrent Viewers: {input_data.total_viewers:,}\n"
            f"- Playback Error Rate: {input_data.playback_error_rate_pct:.2f}%\n"
            f"- Affected Regions: {', '.join(input_data.affected_regions)}\n"
            f"- Calculated Disrupted Viewers: {metrics['affected_viewers']:,}\n"
            f"- Affected VIP Viewers (4K/Atmos Tier): {metrics['affected_vip_viewers']:,}\n"
            f"- Ad Revenue at Immediate Risk: ${metrics['ad_revenue_at_risk_usd']:,.2f}\n"
            f"- Contractual SLA Liability Exposure: ${metrics['sla_penalty_exposure_usd']:,.2f}\n"
            f"- SLA Breach Risk: {metrics['sla_breach_risk']}\n\n"
            f"Generate an executive briefing summary and action urgency."
        )

        fallback_summary = (
            f"Incident {input_data.incident_id} is causing active playback degradation across {metrics['affected_viewers']:,} "
            f"concurrent viewers in {', '.join(input_data.affected_regions)}. "
            f"Ad burn risk stands at ${metrics['ad_revenue_at_risk_usd']:,.2f} with ${metrics['sla_penalty_exposure_usd']:,.2f} "
            f"in contractual SLA liabilities. Urgent remediation is required."
        ) if input_data.playback_error_rate_pct >= 2.0 else "Stream telemetry is nominal. Commercial impact is negligible."

        fallback_payload = {
            "incident_id": input_data.incident_id,
            "affected_viewers": metrics["affected_viewers"],
            "affected_vip_viewers": metrics["affected_vip_viewers"],
            "ad_revenue_at_risk_usd": metrics["ad_revenue_at_risk_usd"],
            "sla_breach_risk": metrics["sla_breach_risk"],
            "sla_penalty_exposure_usd": metrics["sla_penalty_exposure_usd"],
            "executive_summary": fallback_summary,
            "recommendation_urgency": metrics["recommendation_urgency"]
        }

        assessment = await self.execute_structured(
            prompt=prompt,
            response_schema=BusinessImpactAssessment,
            fallback_data=fallback_payload
        )
        # Enforce deterministic mathematical figures
        assessment.affected_viewers = metrics["affected_viewers"]
        assessment.affected_vip_viewers = metrics["affected_vip_viewers"]
        assessment.ad_revenue_at_risk_usd = metrics["ad_revenue_at_risk_usd"]
        assessment.sla_breach_risk = metrics["sla_breach_risk"]
        assessment.sla_penalty_exposure_usd = metrics["sla_penalty_exposure_usd"]
        assessment.recommendation_urgency = metrics["recommendation_urgency"]

        return assessment

    def calculate_prevention_economics(
        self,
        total_viewers: int = 12_400_000,
        risk_score: float = 0.85,
        blast_radius_pct: float = 15.0,
        action_type: str = "scale_transcoder_pool",
    ) -> Dict[str, float]:
        """
        Calculates expected loss without action, cost of prevention, and net avoided exposure.
        """
        projected_disrupted_viewers = int(total_viewers * (blast_radius_pct / 100.0) * risk_score)
        ad_loss = (projected_disrupted_viewers * (12.0 * (10.0 / 60.0)) / 1000.0) * self.cpm_usd
        sla_risk = 25000.0 if risk_score >= 0.80 else 10000.0
        expected_loss = round(ad_loss + sla_risk, 2)

        hourly_node_cost = 42.50
        nodes = 8 if "scale" in action_type else 2
        prevention_cost = round(nodes * hourly_node_cost * 1.0, 2)
        expected_avoided_exposure = round(max(0.0, expected_loss - prevention_cost), 2)

        return {
            "expected_loss_without_action": expected_loss,
            "cost_of_prevention": prevention_cost,
            "expected_avoided_exposure": expected_avoided_exposure,
            "projected_disrupted_viewers": projected_disrupted_viewers,
        }

