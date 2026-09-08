import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from src.events.bus import event_bus
from src.simulator.media_env import media_env

router = APIRouter(prefix="/api/v1/stream", tags=["stream"])

@router.get("/events")
async def stream_events(request: Request):
    """
    SSE stream delivering real-time telemetry (1 Hz) and live agent events to frontend.
    """
    async def event_generator():
        queue = asyncio.Queue()
        event_bus._subscribers.add(queue)
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait up to 1 second for an agent event or emit 1Hz telemetry heartbeat
                    data = await asyncio.wait_for(queue.get(), timeout=1.0)
                    import json
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Emit regular telemetry heartbeat
                    telemetry = media_env.get_telemetry_snapshot()
                    import json
                    msg = {"type": "TELEMETRY_HEARTBEAT", "data": telemetry}
                    yield f"data: {json.dumps(msg)}\n\n"

                    # Emit live Loki logs matching active state
                    try:
                        from src.api.observability import generate_live_log_lines
                        live_logs = generate_live_log_lines()
                        if live_logs:
                            log_msg = {"type": "LOKI_LOG_BATCH", "data": live_logs}
                            yield f"data: {json.dumps(log_msg)}\n\n"
                    except Exception:
                        pass
        except asyncio.CancelledError:
            pass
        finally:
            event_bus._subscribers.discard(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
