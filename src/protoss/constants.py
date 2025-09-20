"""Protoss network constants - Clean, memorable port assignments."""

# Pylon grid ports
PYLON_DEFAULT_PORT = 8888  # Clean, memorable
PYLON_TEST_PORT = 8889  # +1 for test isolation

# Default hosts
DEFAULT_HOST = "localhost"

# Cogency configuration
MODE = "resume"
LLM = "gemini"


# WebSocket URIs
def pylon_uri(host: str = DEFAULT_HOST, port: int = PYLON_DEFAULT_PORT) -> str:
    """Generate WebSocket URI for Pylon connection."""
    return f"ws://{host}:{port}"
