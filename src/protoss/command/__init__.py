"""Protoss Command Interface - CLI for commanding the swarm."""

from .cli import main
from .observatory import observe, show_pathways, show_minds, show_pathway

__all__ = ["main", "observe", "show_pathways", "show_minds", "show_pathway"]