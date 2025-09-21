"""Protoss coordination configuration."""

from dataclasses import dataclass, field
import os
from typing import Dict, Any
import dataclasses # Added for dataclasses.fields

@dataclass(frozen=True)
class Config:
    agents: int = 2
    max_agents: int = 10
    timeout: int = 300
    debug: bool = False
    bus_url: str = "ws://localhost:8888"

    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        return cls(
            agents=int(os.getenv("PROTOSS_AGENTS", cls.agents)),
            max_agents=int(os.getenv("PROTOSS_MAX_AGENTS", cls.max_agents)),
            timeout=int(os.getenv("PROTOSS_TIMEOUT", cls.timeout)),
            debug=os.getenv("PROTOSS_DEBUG", str(cls.debug)).lower() == "true",
            bus_url=os.getenv("PROTOSS_BUS_URL", cls.bus_url),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return dataclasses.asdict(self) # Use asdict for frozen dataclasses

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary."""
        # Filter out keys not in the dataclass constructor
        valid_keys = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def override(self, **kwargs) -> 'Config':
        """Create a new Config instance with overridden values."""
        current_data = self.to_dict()
        current_data.update(kwargs)
        return self.from_dict(current_data)


# No ceremony - use Config() directly
