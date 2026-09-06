import pytest
import asyncio
import json
from src.events.bus import event_bus
from src.orchestration.states import IncidentWorkflowState

@pytest.mark.asyncio
async def test_event_bus_pub_sub():
    received = []

    async def listener():
        async for msg in event_bus.subscribe():
            # msg format: "data: {...}\n\n"
            data_str = msg.strip().replace("data: ", "")
            received.append(json.loads(data_str))
            if len(received) >= 1:
                break

    task = asyncio.create_task(listener())
    await asyncio.sleep(0.05) # Allow subscription queue registration

    await event_bus.publish(
        event_type="STATE_TRANSITION",
        payload={"incident_id": "test-inc-1", "to_state": IncidentWorkflowState.INVESTIGATING.value}
    )

    await asyncio.wait_for(task, timeout=2.0)
    assert len(received) == 1
    assert received[0]["type"] == "STATE_TRANSITION"
    assert received[0]["data"]["incident_id"] == "test-inc-1"
    assert received[0]["data"]["to_state"] == "INVESTIGATING"
