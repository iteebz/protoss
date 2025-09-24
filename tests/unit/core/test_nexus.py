"""Nexus publish/subscribe behaviour."""

import asyncio

import pytest

from protoss.core.nexus import Nexus


@pytest.mark.asyncio
async def test_publish_reaches_general_subscribers(event_factory):
    nexus = Nexus()

    async def consume():
        async for event in nexus.subscribe():
            return event

    consumer = asyncio.create_task(consume())
    await asyncio.sleep(0)

    await nexus.publish(event_factory(type="test"))
    result = await consumer

    assert result.type == "test"


@pytest.mark.asyncio
async def test_publish_filters_by_type_and_channel(event_factory):
    nexus = Nexus()

    async def consume():
        async for event in nexus.subscribe(event_type="agent_message", channel="alpha"):
            return event

    consumer = asyncio.create_task(consume())
    await asyncio.sleep(0)

    await nexus.publish(event_factory(type="agent_message", channel="beta"))
    await nexus.publish(event_factory(type="agent_message", channel="alpha"))

    result = await consumer
    assert result.channel == "alpha"
