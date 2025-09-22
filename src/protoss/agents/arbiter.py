from protoss.core.bus import Bus
from protoss.agents.unit import Unit
from protoss.constitution.identities import ARBITER_IDENTITY
from protoss.core.message import Message # Added Message import


class Arbiter(Unit):
    """Arbiter agent: mediates disputes and ensures constitutional adherence."""

    def __init__(self, bus: Bus):
        super().__init__(bus)
        self.name = "Arbiter"
        self.bus.register(self, ["general"])

    @property
    def identity(self) -> str:
        return ARBITER_IDENTITY

    @property
    def purpose(self) -> str:
        return (
            "To mediate disputes and ensure adherence to the Protoss Constitution. "
            "The Arbiter maintains order and resolves conflicts between other agents."
        )

    async def decide(self, message: Message):
        print(f"Arbiter received message: {message.event.get('content')}")
