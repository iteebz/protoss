"""Protoss coordination configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Immutable Protoss coordination configuration.

    Separates system setup (config) from runtime parameters (per-task).
    Configuration cannot be modified after creation.
    """

    # Core coordination
    agents: int = 5
    """Default number of agents for coordination"""

    max_agents: int = 50
    """Maximum agents allowed (safety limit)"""

    timeout: int = 3600
    """Default coordination timeout in seconds (1 hour)"""

    # LLM configuration
    llm: str = "claude-sonnet"
    """LLM provider for agent execution"""

    # Storage and memory
    archives: str = "./archives"
    """Directory for institutional memory storage"""

    rich_context: bool = True
    """Whether to use archon context seeding by default"""

    # Execution control
    debug: bool = False
    """Enable debug logging and enhanced monitoring"""

    # Coordination limits
    max_context: int = 20
    """Maximum recent messages to include in channel context"""

    max_cycles: int = 10
    """Maximum coordination cycles before giving up"""

    cooldown: int = 300
    """Cooldown in seconds between repeated escalations for the same task"""

    # Completion signals
    complete: str = "[COMPLETE]"
    """Signal that task is fully completed"""

    escalate: str = "[ESCALATE]"
    """Signal to escalate to Sacred Four"""

    # Error handling
    retry: bool = True
    """Whether to retry on execution failures"""

    # Quality control
    constitutional_strictness: str = "standard"
    """Constitutional adherence level: relaxed, standard, strict"""

    escalation_enabled: bool = True
    """Whether to enable strategic consultation escalation"""

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.agents < 1:
            raise ValueError("agents must be at least 1")

        if self.max_agents < self.agents:
            raise ValueError("max_agents must be >= agents")

        if self.timeout < 1:
            raise ValueError("timeout must be at least 1 second")

        valid_strictness = ["relaxed", "standard", "strict"]
        if self.constitutional_strictness not in valid_strictness:
            raise ValueError(
                f"constitutional_strictness must be one of {valid_strictness}"
            )

        if not self.archives.strip():
            raise ValueError("archives path cannot be empty")

        if self.cooldown < 0:
            raise ValueError("cooldown must be non-negative")

    def override(self, **kwargs) -> "Config":
        """Create new Config with overridden values."""
        from dataclasses import replace

        return replace(self, **kwargs)


# No ceremony - use Config() directly
