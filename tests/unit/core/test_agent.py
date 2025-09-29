from unittest.mock import AsyncMock

import pytest

from protoss.core.agent import Agent
from protoss.constitution import registry


@pytest.fixture
def agent(monkeypatch):
    monkeypatch.setattr(
        registry,
        "get_agent_data",
        lambda unit_type: {
            "identity": ["ZEALOT"],
            "guidelines": "Be bold",
            "tools": [],
        },
    )

    mock_cogency_agent = AsyncMock(return_value="mocked response !despawn")
    monkeypatch.setattr(
        "protoss.core.agent.cogency.Agent",
        lambda llm, instructions, tools: mock_cogency_agent,
    )

    ag = Agent(
        agent_type="zealot",
        channel="alpha",
        bus_url="ws://bus",
        coordination_id="coord-1",
    )
    ag.send_message = AsyncMock()
    ag.cogency_agent = mock_cogency_agent  # Ensure the agent instance uses the mock
    return ag


@pytest.mark.asyncio
async def test_broadcast_routes_through_send(agent):
    event = {"type": "respond", "content": "hi"}
    await agent.broadcast(event)

    agent.send_message.assert_awaited_once_with(
        content="hi",
        event_type="respond",
        event_payload=event,
        coordination_id="coord-1",
    )


@pytest.mark.asyncio
async def test_process_message_invokes_llm(agent, monkeypatch):
    calls = []

    async def mock_cogency_agent_call(content_arg):
        calls.append(content_arg)
        yield {"type": "respond", "content": "done !despawn"}

    # Mock the cogency agent to return the async generator
    agent.cogency_agent = mock_cogency_agent_call

    await agent._process_message(
        type("Event", (), {"type": "agent_message", "content": "do"})()
    )

    assert calls == ["do"]
    assert agent._running is False


@pytest.mark.asyncio
async def test_agent_history_processing(monkeypatch):
    """Regression test: Agent must process channel history through cogency on startup."""
    # Mock registry
    monkeypatch.setattr(
        registry,
        "get_agent_data",
        lambda unit_type: {
            "identity": ["ARBITER"],
            "guidelines": "Bridge human intent",
            "tools": [],
        },
    )

    # Mock cogency with history processing
    history_calls = []

    async def mock_cogency_agent_call(content_arg):
        history_calls.append(content_arg)
        yield {"type": "respond", "content": "Status report acknowledged"}

    mock_cogency_agent = mock_cogency_agent_call
    monkeypatch.setattr(
        "protoss.core.agent.cogency.Agent",
        lambda llm, instructions, tools: mock_cogency_agent,
    )

    # Mock khala
    mock_khala = AsyncMock()
    mock_khala.request_history.return_value = [
        {"sender": "human", "content": "Give me status @arbiter"},
        {"sender": "system", "content": "Agent spawned"},
    ]
    monkeypatch.setattr("protoss.core.agent.Khala", lambda bus_url: mock_khala)

    agent = Agent(
        agent_type="arbiter",
        channel="nexus",
        bus_url="ws://test",
        coordination_id="test-coord",
    )
    agent.send_message = AsyncMock()

    # Simulate agent startup (partial run method)
    await agent.khala.connect(agent_id=agent.agent_id)
    history = await agent.khala.request_history(agent.channel)

    # Process history through cogency (regression fix)
    if agent.cogency_agent and history:
        history_text = "\n".join(
            [
                f"{msg.get('sender', 'unknown')}: {msg.get('content', '')}"
                for msg in history
            ]
        )
        async for cogency_event in agent.cogency_agent(
            f"Channel history:\n{history_text}"
        ):
            if cogency_event["type"] == "respond":
                await agent.send_message(content=cogency_event["content"])
                break

    # Verify cogency processed channel history
    assert len(history_calls) == 1
    assert "human: Give me status @arbiter" in history_calls[0]

    # Verify response was sent
    agent.send_message.assert_awaited_once_with(content="Status report acknowledged")
