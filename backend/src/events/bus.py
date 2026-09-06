import asyncio
import json
import logging
from typing import Set, Dict, Any, AsyncGenerator

logger = logging.getLogger(__name__)

class EventBus:
    """
    In-process asynchronous event bus for broadcasting live telemetry,
    agent timeline updates, and incident state transitions via Server-Sent Events (SSE).
    """
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    async def subscribe(self) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(queue)
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            self._subscribers.discard(queue)

    async def publish(self, event_type: str, payload: Dict[str, Any]):
        message = {
            "type": event_type,
            "data": payload
        }
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.warning("Subscriber queue full, discarding message")

event_bus = EventBus()
