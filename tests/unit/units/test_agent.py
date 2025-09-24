"""LLM Agent tests."""

from unittest.mock import AsyncMock

import pytest

from protoss.units.agent import Agent


@pytest.fixture
def agent(monkeypatch):
    monkeypatch.setattr(
        "protoss.units.unit.get_unit_data",
        lambda unit_type: {
            "identity": ["ZEALOT"],
            "guidelines": "Be bold",
            "tools": [],
        },
    )
    monkeypatch.setattr("protoss.units.agent.cogency", None)

    ag = Agent(
        unit_type="zealot",
        channel="alpha",
        bus_url="ws://bus",
        coordination_id="coord-1",
    )
    ag.send_message = AsyncMock()
    return ag


@pytest.mark.asyncio
async def test_broadcast_routes_through_send(agent):
    event = {"type": "respond", "content": "hi"}
    await agent.broadcast(event)

    agent.send_message.assert_awaited_once_with(
        content="hi",
        event_type="agent_message",
        event_payload=event,
        coordination_id="coord-1",
    )


def test_identity_selection(agent):
    agent.registry_data = {"identity": ["A", "B"]}
    agent.identity_index = 1
    assert agent._get_identity() == "B"


@pytest.mark.asyncio
async def test_process_message_invokes_llm(agent, monkeypatch):
    calls = []

    async def fake_call(self, content):
        calls.append(content)
        return "done !despawn"

    monkeypatch.setattr(Agent, "__call__", fake_call)

    await agent._process_message(
        type("Event", (), {"type": "agent_message", "content": "do"})()
    )

    assert calls == ["do"]
    assert agent._running is False
