"""Protoss coordination configuration."""

from dataclasses import dataclass, field
from typing import Dict, Any
import dataclasses


@dataclass(frozen=True)
class Config:
    """Pure constitutional configuration - minimal ceremony."""

    timeout: int = 3600  # Constitutional patience
    debug: bool = False
    port: int = 8888  # Bus port - simple name
    max_agents: int = 100  # Constitutional safeguard
    bus_url: str = field(init=False)  # Derived from port

    def __post_init__(self):
        # Derive bus_url from port
        object.__setattr__(self, "bus_url", f"ws://localhost:{self.port}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        valid_keys = {f.name for f in dataclasses.fields(cls) if f.init}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def with_overrides(self, **kwargs) -> "Config":
        """Pure constitutional configuration with overrides."""
        current_data = self.to_dict()
        current_data.update(kwargs)
        return self.from_dict(current_data)
