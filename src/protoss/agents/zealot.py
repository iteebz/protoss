"""Zealot: Constitutional AI Agent with Righteous Conviction"""

import logging
from .unit import Unit
from ..core.config import Config
from ..constitution import ZEALOT_IDENTITY

logger = logging.getLogger(__name__)


class Zealot(Unit):
    """Constitutional AI Agent with Zealot Principles"""

    @property
    def identity(self) -> str:
        return ZEALOT_IDENTITY

    @property
    def tools(self):
        return self._cogency_tools(
            ["file_read", "file_write", "file_edit", "file_list", "shell"]
        )

