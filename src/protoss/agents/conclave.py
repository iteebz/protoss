from typing import Dict
from protoss.core.message import Message
from protoss.agents.unit import Unit
from protoss.constitution.identities import (
    TASSADAR_IDENTITY,
    ZERATUL_IDENTITY,
    ARTANIS_IDENTITY,
    FENIX_IDENTITY,
)


class Conclave(Unit):
    """Conclave agent: represents the collective wisdom and decision-making of the Protoss hierarchy."""

    PERSPECTIVES: Dict[str, Dict] = {
        "tassadar": {"identity": TASSADAR_IDENTITY},
        "zeratul": {"identity": ZERATUL_IDENTITY},
        "artanis": {"identity": ARTANIS_IDENTITY},
        "fenix": {"identity": FENIX_IDENTITY},
    }

    @property
    def identity(self) -> str:
        return "Conclave"

    @property
    def purpose(self) -> str:
        return (
            "To synthesize diverse perspectives and make collective decisions for the Protoss. "
            "The Conclave ensures that all major actions align with the greater good of the Khala."
        )

    async def decide(self, message: Message):
        print(f"Conclave received message: {message.event.get('content')}")
