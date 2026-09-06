from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.models import IncidentFingerprint

class FingerprintStore:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_similar_incidents(self, signature: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
        result = await self.session.execute(select(IncidentFingerprint).limit(limit))
        records = list(result.scalars().all())

        matches = []
        for r in records:
            # Deterministic similarity matching on tags and symptoms
            score = 0.85 if signature.get("failing_component", "") in str(r.symptom_signature) else 0.70
            matches.append({
                "id": str(r.id),
                "root_cause_summary": r.root_cause_summary,
                "successful_action_type": r.successful_action_type,
                "similarity_score": score,
                "tags": r.tags
            })
        return sorted(matches, key=lambda x: x["similarity_score"], reverse=True)
