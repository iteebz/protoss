"""Resource tracking for the Protoss swarm."""

import time
from dataclasses import dataclass, field


@dataclass
class TokenUsage:
    """Represents token usage for a single AI model call."""

    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class ResourceTracker:
    """Tracks resource usage (e.g., tokens, time) for the swarm."""

    total_usage: TokenUsage = field(default_factory=TokenUsage)
    start_time: float = field(default_factory=time.time)

    def add_usage(self, usage: TokenUsage):
        """Add token usage from a model call."""
        self.total_usage.input_tokens += usage.input_tokens
        self.total_usage.output_tokens += usage.output_tokens

    def get_summary(self) -> dict:
        """Return a summary of resource usage."""
        elapsed_time = time.time() - self.start_time
        return {
            "total_input_tokens": self.total_usage.input_tokens,
            "total_output_tokens": self.total_usage.output_tokens,
            "total_tokens": self.total_usage.total_tokens,
            "elapsed_time_seconds": elapsed_time,
        }
