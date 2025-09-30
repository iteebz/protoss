"""Path management for protoss directories."""

from pathlib import Path


def get_protoss_dir(base_dir: str = None) -> Path:
    """Get protoss directory, using base_dir if provided."""
    if base_dir:
        protoss_dir = Path(base_dir)
    else:
        protoss_dir = Path(".protoss")  # Local to current directory
    protoss_dir.mkdir(exist_ok=True)
    return protoss_dir


class Paths:
    """Clean path management for protoss directories."""

    @staticmethod
    def db(base_dir: str = None) -> Path:
        """Get database path."""
        return get_protoss_dir(base_dir) / "ledger.db"

    @staticmethod
    def sandbox(base_dir: str = None) -> Path:
        """Get sandbox path."""
        base = get_protoss_dir(base_dir) / "sandbox"
        base.mkdir(exist_ok=True)
        return base
