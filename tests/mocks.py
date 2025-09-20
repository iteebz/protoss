"""Mock implementations for PROTOSS testing.

Provides deterministic mock responses for Cogency Agent calls,
enabling fast, reliable contract validation without LLM dependencies.
"""

import asyncio
from typing import AsyncGenerator, Dict, Any


class MockCogencyAgent:
    """Mock Cogency Agent with deterministic responses for testing."""

    def __init__(self, response_map: Dict[str, str] = None):
        """Initialize with optional response mapping."""
        self.response_map = response_map or {}
        self.default_responses = {
            "constitutional": {
                "tassadar": "TASSADAR POSITION: Focus on shipping viable solution quickly. Technical debt acceptable for MVP validation.",
                "zeratul": "ZERATUL POSITION: Hidden risks include security vulnerabilities and scalability bottlenecks. Need deeper investigation.",
                "artanis": "ARTANIS POSITION: Balance shipping speed with quality. Suggest iterative approach with clear milestones.",
                "fenix": "FENIX POSITION: Simplest path: start with monolith, extract services only when needed.",
            },
            "coordination": "I'll coordinate with the team via PSI messages to divide this work effectively.",
            "synthesis": "SYNTHESIS COMPLETE: Key insights preserved. Implementation patterns documented for institutional memory.",
            "completion": "Task completed successfully. All requirements fulfilled.",
            "uncertainty": "true",  # Zealot uncertainty assessment
        }

    def __call__(
        self, prompt: str, conversation_id: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Mock agent call - returns async generator like real Cogency."""
        return self._mock_response_stream(prompt, conversation_id)

    async def _mock_response_stream(
        self, prompt: str, conversation_id: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate mock response stream."""
        # Determine response based on prompt content
        response = self._get_response_for_prompt(prompt, conversation_id)

        # Simulate streaming response chunks
        chunks = self._chunk_response(response)

        for chunk in chunks:
            yield {"type": "respond", "content": chunk}
            # Brief delay to simulate real streaming
            await asyncio.sleep(0.01)

    def _get_response_for_prompt(self, prompt: str, conversation_id: str = None) -> str:
        """Determine appropriate mock response based on prompt content."""
        prompt_lower = prompt.lower()

        # Check custom response map first
        for key, response in self.response_map.items():
            if key.lower() in prompt_lower:
                return response

        # Constitutional positions for Sacred Four
        if "constitutional position" in prompt_lower:
            if "tassadar" in (conversation_id or "").lower():
                return self.default_responses["constitutional"]["tassadar"]
            elif "zeratul" in (conversation_id or "").lower():
                return self.default_responses["constitutional"]["zeratul"]
            elif "artanis" in (conversation_id or "").lower():
                return self.default_responses["constitutional"]["artanis"]
            elif "fenix" in (conversation_id or "").lower():
                return self.default_responses["constitutional"]["fenix"]

        # Coordination tasks
        if "coordination task" in prompt_lower:
            return self.default_responses["coordination"]

        # Archon synthesis
        if "synthesis" in prompt_lower or "preserve" in prompt_lower:
            return self.default_responses["synthesis"]

        # Zealot uncertainty assessment
        if "true if i need help" in prompt_lower:
            return self.default_responses["uncertainty"]

        # Default completion response
        return self.default_responses["completion"]

    def _chunk_response(self, response: str) -> list[str]:
        """Split response into realistic streaming chunks."""
        if len(response) <= 20:
            return [response]

        # Split into word-based chunks
        words = response.split()
        chunks = []
        current_chunk = ""

        for word in words:
            if len(current_chunk + " " + word) > 20 and current_chunk:
                chunks.append(current_chunk)
                current_chunk = word
            else:
                current_chunk = current_chunk + " " + word if current_chunk else word

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


def mock_agent_factory(
    unit_type: str = "zealot", custom_responses: Dict[str, str] = None
) -> MockCogencyAgent:
    """Create mock agent for specific unit type."""
    responses = custom_responses or {}

    # Add unit-specific responses
    if unit_type == "tassadar":
        responses["constitutional"] = (
            "Focus on pragmatic shipping constraints and timeline realities."
        )
    elif unit_type == "zeratul":
        responses["constitutional"] = (
            "Investigate hidden risks and challenge assumptions systematically."
        )
    elif unit_type == "artanis":
        responses["constitutional"] = (
            "Synthesize perspectives and find collaborative consensus."
        )
    elif unit_type == "fenix":
        responses["constitutional"] = (
            "Cut complexity and focus on simplest effective solution."
        )
    elif unit_type == "archon":
        responses["synthesis"] = (
            "Knowledge synthesis complete - patterns preserved in institutional memory."
        )

    return MockCogencyAgent(responses)


class MockKhalaConnection:
    """Mock Khala connection for isolated unit testing."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.sent_messages = []
        self.received_messages = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def send(self, pathway: str, content: str):
        """Mock PSI message sending."""
        self.sent_messages.append(
            {"pathway": pathway, "content": content, "sender": self.agent_id}
        )

    async def receive(self):
        """Mock PSI message receiving."""
        if self.received_messages:
            return self.received_messages.pop(0)
        return None

    def inject_message(self, pathway: str, sender: str, content: str):
        """Inject mock message for testing."""
        self.received_messages.append(MockPsi(pathway, sender, content))


class MockPsi:
    """Mock PSI message for testing."""

    def __init__(self, pathway: str, sender: str, content: str):
        self.pathway = pathway
        self.sender = sender
        self.content = content
        self.timestamp = 1000.0  # Fixed timestamp for deterministic tests

    def serialize(self) -> str:
        return f"§PSI|{self.pathway}|{self.sender}: {self.content}"
