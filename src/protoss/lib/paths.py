"""Path utilities for the Protoss system."""

from pathlib import Path


def get_protoss_dir() -> Path:
    """Returns the canonical path to the .protoss directory in the user's home."""
    return Path.home() / ".protoss"
