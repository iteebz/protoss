"""Workspace utilities."""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)


async def get_workspace_state(base_dir: str) -> str:
    """Get current workspace file listing for coordination."""
    if not base_dir:
        return ""

    try:
        # Show only sandbox contents, not internal DBs
        workspace = Path(base_dir) / "sandbox"
        if not workspace.exists():
            return ""

        files = []
        for item in sorted(workspace.rglob("*")):
            if item.is_file() and not item.name.startswith("."):
                rel_path = item.relative_to(workspace)
                files.append(str(rel_path))

        if files:
            files_list = "\n".join(f"  - {f}" for f in files[:20])
            return f"[Workspace]\n{files_list}\n\n"
    except Exception as e:
        logger.debug(f"Failed to list workspace: {e}")

    return ""
