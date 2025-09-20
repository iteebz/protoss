"""Unit tests for Khala persistence and coordination contracts.

Fast, isolated tests validating Khala behavior without infrastructure dependencies.
Tests SQLite persistence, PSI message handling, and pathway management.
"""

import pytest
from unittest.mock import Mock, patch
import tempfile

from protoss.khala import Khala, Psi
from protoss.forge.storage import SQLite


class TestPsiMessage:
    """Test PSI message parsing and serialization."""

    def test_psi_parse_valid_message(self):
        """Test parsing valid PSI message format."""
        raw = "§PSI|test-pathway|agent-123: Hello world"

        psi = Psi.parse(raw)

        assert psi is not None
        assert psi.pathway == "test-pathway"
        assert psi.sender == "agent-123"
        assert psi.content == "Hello world"
        assert psi.timestamp > 0

    def test_psi_parse_invalid_format(self):
        """Test parsing invalid message formats returns None."""
        invalid_messages = [
            "Not a PSI message",
            "§PSI|incomplete",
            "§PSI|no|colon",
            "",
            "§PSI||empty-sender: content",
        ]

        for invalid in invalid_messages:
            psi = Psi.parse(invalid)
            assert psi is None

    def test_psi_serialize(self):
        """Test PSI message serialization."""
        psi = Psi(
            pathway="test-pathway",
            sender="agent-123",
            content="Test message",
            timestamp=1000.0,
        )

        serialized = psi.serialize()
        assert serialized == "§PSI|test-pathway|agent-123: Test message"

    def test_psi_mentions_detection(self):
        """Test @mention detection in PSI content."""
        test_cases = [
            ("Hello @archon please help", ["archon"]),
            ("Need @tassadar and @zeratul input", ["tassadar", "zeratul"]),
            ("No mentions here", []),
            ("@archon @archon duplicate", ["archon"]),  # Should deduplicate
        ]

        for content, expected_mentions in test_cases:
            psi = Psi("test", "sender", content)
            assert set(psi.mentions) == set(expected_mentions)

    def test_psi_direct_message_detection(self):
        """Test direct message detection."""
        # Direct messages use agent-type pattern
        direct_psi = Psi("zealot-123", "sender", "Direct message")
        broadcast_psi = Psi("squad-456", "sender", "Broadcast message")

        assert direct_psi.is_direct_message is True
        assert broadcast_psi.is_direct_message is False


class TestKhalaCore:
    """Test core Khala functionality."""

    def test_khala_initialization(self):
        """Test Khala initializes with correct state."""
        khala = Khala()

        assert khala.subscribers == {}
        assert khala.memories == {}
        assert khala.agents == {}
        assert khala.max_memory == 50
        assert khala.storage is not None

    def test_grid_port_management(self):
        """Test grid port setting and retrieval."""
        khala = Khala()

        # Default port
        default_port = khala.get_grid_port()
        assert default_port == 8888  # PYLON_DEFAULT_PORT

        # Custom port
        khala.set_grid_port(9999)
        assert khala.get_grid_port() == 9999

        # Grid URI construction
        uri = khala.get_grid_uri()
        assert "localhost:9999" in uri

    def test_agent_registration(self):
        """Test agent registration and severing."""
        khala = Khala()
        mock_websocket = Mock()

        # Register agent
        khala.register_agent("agent-123", mock_websocket)
        assert "agent-123" in khala.agents
        assert khala.agents["agent-123"] == mock_websocket

        # Sever agent
        khala.sever("agent-123")
        assert "agent-123" not in khala.agents


class TestKhalaTransmission:
    """Test Khala PSI transmission functionality."""

    @pytest.mark.asyncio
    async def test_transmit_pathway_creation(self):
        """Test pathway auto-creation on first transmission."""
        khala = Khala()

        with patch.object(khala.storage, "save_psi") as mock_save:
            await khala.transmit("new-pathway", "sender", "First message")

            # Should auto-create pathway
            assert "new-pathway" in khala.subscribers
            assert "new-pathway" in khala.memories
            assert len(khala.memories["new-pathway"]) == 1

            # Should persist to storage
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_transmit_memory_trimming(self):
        """Test memory trimming when exceeding max_memory."""
        khala = Khala()
        khala.max_memory = 3  # Small limit for testing

        with patch.object(khala.storage, "save_psi"):
            # Send more messages than max_memory
            for i in range(5):
                await khala.transmit("test-pathway", "sender", f"Message {i}")

            # Should trim to max_memory
            memories = khala.memories["test-pathway"]
            assert len(memories) == 3

            # Should keep most recent messages
            contents = [msg.content for msg in memories]
            assert "Message 2" in contents
            assert "Message 3" in contents
            assert "Message 4" in contents
            assert "Message 0" not in contents

    @pytest.mark.asyncio
    async def test_transmit_pathway_broadcasting(self):
        """Test pathway message broadcasting to subscribers."""
        khala = Khala()

        with patch.object(khala.storage, "save_psi"):
            # Send message to pathway
            await khala.transmit("test-pathway", "sender", "Broadcast message")

            # Should create pathway and store in memory
            assert "test-pathway" in khala.subscribers
            assert "test-pathway" in khala.memories
            assert len(khala.memories["test-pathway"]) == 1

    @pytest.mark.asyncio
    async def test_transmit_archon_mention_detection(self):
        """Test @archon mention triggers archon spawning."""
        khala = Khala()

        with patch.object(khala, "_spawn_archon_for_pathway") as mock_spawn:
            with patch.object(khala.storage, "save_psi"):
                await khala.transmit(
                    "test-pathway", "requester", "Please @archon synthesize this work"
                )

                # Should trigger archon spawning
                mock_spawn.assert_called_once_with("test-pathway")

    @pytest.mark.asyncio
    async def test_transmit_completion_detection(self):
        """Test pathway completion triggers auto-synthesis."""
        khala = Khala()

        with patch.object(khala, "_detect_pathway_completion", return_value=True):
            with patch.object(khala, "_spawn_synthesis_archon") as mock_synthesis:
                with patch.object(khala.storage, "save_psi"):
                    await khala.transmit(
                        "test-pathway", "worker", "Task completed successfully"
                    )

                    # Should trigger auto-synthesis
                    mock_synthesis.assert_called_once_with("test-pathway")


class TestKhalaStorage:
    """Test Khala SQLite storage integration."""

    @pytest.mark.asyncio
    async def test_pathways_method_lists_all(self):
        """Test pathways() method lists all pathways from storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = SQLite(temp_dir)
            khala = Khala()
            khala.storage = storage

            # Create multiple pathways
            pathways = ["pathway-1", "pathway-2", "pathway-3"]
            for pathway in pathways:
                await khala.transmit(pathway, "agent", f"Message for {pathway}")

            # List all pathways
            all_pathways = await khala.pathways()

            pathway_names = [p["name"] for p in all_pathways]
            for pathway in pathways:
                assert pathway in pathway_names
