"""Unit tests for agent constitutional identity and tools."""

from unittest.mock import patch


def test_zealot_identity():
    """Zealot has constitutional identity."""
    from protoss.agents.zealot import Zealot
    from protoss.core.config import Config

    zealot = Zealot("test", "zealot", "channel", Config())

    assert "ZEALOT" in zealot.identity
    assert "Beautiful code" in zealot.identity
    assert "simplicity is salvation" in zealot.identity


def test_zealot_tools():
    """Zealot has constitutional tools."""
    from protoss.agents.zealot import Zealot
    from protoss.core.config import Config

    zealot = Zealot("test", "zealot", "channel", Config())
    tools = zealot.tools

    assert isinstance(tools, list)


def test_archon_identity():
    """Archon has constitutional identity."""
    from protoss.agents.archon import Archon
    from protoss.core.config import Config

    archon = Archon("test", "archon", "channel", Config())

    assert "ARCHON" in archon.identity
    assert "Channel seeding and knowledge compression specialist." in archon.identity
    assert "institutional memory" in archon.identity


def test_archon_tools():
    """Archon has constitutional tools."""
    from protoss.agents.archon import Archon
    from protoss.core.config import Config

    # Mock the cogency tools singleton
    with patch(
        "cogency.tools.tools.category", return_value=["mock_tool_1", "mock_tool_2"]
    ) as mock_category:
        archon = Archon("test", "archon", "channel", Config())
        tools = archon.tools

        # Assert that the category method was called correctly
        mock_category.assert_called_once_with(["file", "system"])

        # Assert that the tools property returns the mocked tools
        assert isinstance(tools, list)
        assert tools == ["mock_tool_1", "mock_tool_2"]


def test_conclave_identity():
    """Conclave has constitutional identity."""
    from protoss.agents.conclave import Conclave
    from protoss.core.config import Config

    conclave = Conclave("tassadar", "test", "conclave", "channel", Config())

    assert "TASSADAR" in conclave.identity
    assert "Tassadar" in conclave.identity


def test_conclave_tools():
    """Conclave has constitutional tools."""
    from protoss.agents.conclave import Conclave
    from protoss.core.config import Config

    conclave = Conclave("tassadar", "test", "conclave", "channel", Config())
    tools = conclave.tools

    assert isinstance(tools, list)
    # Conclave might not have specific tools, or they might be internal


def test_arbiter_identity():
    """Arbiter has constitutional identity."""
    from protoss.agents.arbiter import Arbiter
    from protoss.core.config import Config

    arbiter = Arbiter("test", "arbiter", "channel", Config())

    assert "ARBITER" in arbiter.identity
    assert "HUMAN COMMAND INTERFACE" in arbiter.identity
    assert "YOU BRIDGE HUMAN INTENT WITH SWARM COORDINATION." in arbiter.identity


def test_arbiter_tools():
    """Arbiter has constitutional tools."""
    from protoss.agents.arbiter import Arbiter
    from protoss.core.config import Config

    arbiter = Arbiter("test", "arbiter", "channel", Config())
    tools = arbiter.tools

    assert isinstance(tools, list)
    # Arbiter might not have specific tools, or they might be internal
