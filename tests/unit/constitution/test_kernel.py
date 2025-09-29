from protoss.core.event import Event
from protoss.constitution import kernel


def test_validate_spawn_allows_constitutional_agents():
    assert kernel.validate_spawn("arbiter")
    assert kernel.validate_spawn("zealot")
    assert kernel.validate_spawn("archon")


def test_validate_spawn_rejects_unknown_agents():
    assert not kernel.validate_spawn("rogue")
    assert not kernel.validate_spawn("terran")


def test_validate_sovereignty_allows_self_deregistration():
    assert kernel.validate_sovereignty("zealot", "zealot")


def test_validate_sovereignty_blocks_cross_deregistration():
    assert not kernel.validate_sovereignty("zealot", "arbiter")


def test_validate_coordination_requires_id_for_critical_events():
    event = Event(
        type="agent_message", channel="alpha", sender="zealot", coordination_id=None
    )
    assert not kernel.validate_coordination(event)

    event.coordination_id = "coord-123"
    assert kernel.validate_coordination(event)


def test_validate_coordination_allows_non_critical_events_without_id():
    event = Event(
        type="system_message", channel="alpha", sender="system", coordination_id=None
    )
    assert kernel.validate_coordination(event)
