import logging
from typing import Dict, Any, List
from src.persistence.fingerprints import FingerprintStore
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class VertexMemoryAdapter:
    """
    Adapter connecting to Vertex AI Search / Vector Search with transparent
    PostgreSQL / local in-memory fallback.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.store = FingerprintStore(session)

    async def search_similar_past_incidents(self, signature: Dict[str, Any]) -> List[Dict[str, Any]]:
        # In offline/hackathon environment, gracefully query indexed historical fingerprints
        logger.info(f"Querying historical incident memory for signature: {signature}")
        return await self.store.find_similar_incidents(signature)
