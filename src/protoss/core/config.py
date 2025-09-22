"""Protoss coordination configuration."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    """Pure constitutional configuration - minimal ceremony."""

    timeout: int = 3600  # Constitutional patience
    debug: bool = False
    port: int = 8888  # Bus port - simple name
    max_agents: int = 100  # Constitutional safeguard
    bus_url: str = field(default="ws://localhost:8888")
