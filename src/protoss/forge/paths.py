"""Path management for protoss directories."""

from pathlib import Path


def get_protoss_dir(base_dir: str = None) -> Path:
    """Get protoss directory, configurable like cogency."""
    if base_dir:
        protoss_dir = Path(base_dir)
    else:
        protoss_dir = Path(".protoss")  # Local to current directory
    protoss_dir.mkdir(exist_ok=True)
    return protoss_dir


class Paths:
    """Clean path management for protoss directories."""

    @staticmethod
    def db(subpath: str = None, base_dir: str = None) -> Path:
        """Get database path with optional subpath."""
        base = get_protoss_dir(base_dir) / "store.db"
        return base / subpath if subpath else base

    @staticmethod
    def sandbox(subpath: str = None, base_dir: str = None) -> Path:
        """Get sandbox path with optional subpath."""
        base = get_protoss_dir(base_dir) / "sandbox"
        base.mkdir(exist_ok=True)
        return base / subpath if subpath else base

    @staticmethod
    def logs(subpath: str = None, base_dir: str = None) -> Path:
        """Get logs path with optional subpath."""
        base = get_protoss_dir(base_dir) / "logs"
        base.mkdir(exist_ok=True)
        return base / subpath if subpath else base