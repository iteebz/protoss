"""Evaluation configuration."""

import random

from protoss.lib.paths import Paths  # Import Paths from protoss.lib.paths


# Removed ProtossPaths class as it's now in protoss.lib.paths


class Config:
    """Zero ceremony eval config."""

    sample_size: int = 2
    seed: int = 42
    max_iterations: int = 3
    timeout: int = 60
    max_concurrent_tests: int = 2
    mode: str = "replay"  # replay, resume, auto
    llm: str = "gemini"  # Default LLM
    sandbox: bool = True  # Always sandbox for safety
    security_simulation: bool = True  # Simulate dangerous ops, don't execute

    def __init__(self):
        self._judge = "gemini"
        random.seed(self.seed)

    # Removed agent() method as agent deployment is now handled by protoss_eval_runner

    @property
    def output_dir(self):
        return Paths.evals()  # Use Paths from protoss.lib.paths

    @property
    def judge(self):
        """Cross-model judge to prevent self-evaluation bias."""
        return self._judge

    @judge.setter
    def judge(self, value):
        self._judge = value


config = Config()
