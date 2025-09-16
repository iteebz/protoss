"""Storage protocols for Protoss forge persistence."""

from typing import Protocol, List


class Storage(Protocol):
    """Storage interface for Protoss coordination persistence."""
    
    async def save_psi(self, pathway: str, sender: str, content: str, timestamp: float = None) -> None:
        """Save psi transmission to pathway."""
        ...
    
    async def load_pathways(self) -> List[dict]:
        """Load all pathways with activity stats."""
        ...
        
    async def load_pathway_psi(self, pathway: str, since: float = 0, limit: int = None) -> List[dict]:
        """Load psi transmissions from pathway since timestamp."""
        ...
    
    async def get_recent_messages(self, pathway: str, limit: int = 10) -> List[str]:
        """Get recent message content from pathway."""
        ...