import pytest
from src.agents.impact import BusinessImpactAgent
from src.agents.schemas import BusinessImpactInput, BusinessImpactAssessment

@pytest.mark.asyncio
async def test_business_impact_critical_degradation():
    agent = BusinessImpactAgent()
    input_data = BusinessImpactInput(
        incident_id="inc-impact-991",
        total_viewers=12_400_000,
        affected_regions=["AU", "SG"],
        playback_error_rate_pct=8.7,
        incident_duration_seconds=900.0 # 15 minutes
    )

    assessment = await agent.assess_impact(input_data)
    assert isinstance(assessment, BusinessImpactAssessment)
    assert assessment.incident_id == "inc-impact-991"
    assert assessment.affected_viewers > 500_000
    assert assessment.affected_vip_viewers > 20_000
    assert assessment.ad_revenue_at_risk_usd > 10_000.0
    assert assessment.sla_breach_risk == "CRITICAL"
    assert assessment.sla_penalty_exposure_usd >= 18_750.0
    assert assessment.recommendation_urgency == "IMMEDIATE"
    assert "Incident inc-impact-991" in assessment.executive_summary

@pytest.mark.asyncio
async def test_business_impact_healthy_threshold():
    agent = BusinessImpactAgent()
    input_data = BusinessImpactInput(
        incident_id="inc-impact-healthy",
        total_viewers=12_400_000,
        affected_regions=[],
        playback_error_rate_pct=0.4,
        incident_duration_seconds=120.0
    )

    assessment = await agent.assess_impact(input_data)
    assert assessment.sla_breach_risk == "LOW"
    assert assessment.sla_penalty_exposure_usd == 0.0
    assert assessment.recommendation_urgency == "NORMAL"
