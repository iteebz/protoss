"""Constitutional Claims - Pure accountability."""

import uuid
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class WorkClaim:
    claim_id: str
    agent_id: str
    coordination_id: str
    content: str
    status: str = "active"


class Claims:
    """Constitutional accountability - no ceremony."""

    def __init__(self):
        self.claims: Dict[str, WorkClaim] = {}

    def claim(self, agent_id: str, coordination_id: str, content: str) -> str:
        """Agent claims work."""
        claim_id = str(uuid.uuid4())[:8]
        self.claims[claim_id] = WorkClaim(claim_id, agent_id, coordination_id, content)
        return claim_id

    def complete(self, claim_id: str, agent_id: str) -> bool:
        """Agent completes their claim."""
        claim = self.claims.get(claim_id)
        if not claim or claim.agent_id != agent_id:
            return False

        claim.status = "complete"
        return True

    def get(self, claim_id: str) -> Optional[WorkClaim]:
        """Get claim by ID."""
        return self.claims.get(claim_id)
