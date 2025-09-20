"""WebSocket server for agent communication."""

from typing import Dict, List, Callable, Awaitable
import websockets


class Server:
    """WebSocket server for agent communication."""

    def __init__(self, port: int = 8888):
        self.port = port
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_handlers: List[Callable[[str, str], Awaitable[None]]] = []
        self.connection_handlers: List[Callable[[str], Awaitable[None]]] = []
        self.disconnection_handlers: List[Callable[[str], Awaitable[None]]] = []

    def on_message(self, handler: Callable[[str, str], Awaitable[None]]):
        """Register message event handler.

        Handlers receive all messages from connected agents for processing
        by higher-level coordination systems (like Khala).

        Args:
            handler: Async function that receives (agent_id, raw_message)
        """
        self.message_handlers.append(handler)

    def on_connect(self, handler: Callable[[str], Awaitable[None]]):
        """Register connection event handler.

        Handlers are notified when agents establish WebSocket connections
        to enable coordination layer initialization and state synchronization.

        Args:
            handler: Async function that receives agent_id
        """
        self.connection_handlers.append(handler)

    def on_disconnect(self, handler: Callable[[str], Awaitable[None]]):
        """Register disconnection event handler.

        Handlers are notified when agents disconnect to enable coordination
        layer cleanup and graceful degradation of multi-agent systems.

        Args:
            handler: Async function that receives agent_id
        """
        self.disconnection_handlers.append(handler)

    async def send(self, agent_id: str, message: str):
        """Send direct message to specific agent.

        Core message delivery function for point-to-point communication.
        Automatically handles disconnected agents with graceful cleanup.

        Args:
            agent_id: Target agent identifier
            message: Raw message content to deliver
        """
        if agent_id in self.connections:
            try:
                await self.connections[agent_id].send(message)
            except websockets.exceptions.ConnectionClosed:
                await self._disconnect(agent_id)

    async def broadcast(self, message: str):
        """Broadcast message to all connected agents.

        Sends message to every active connection simultaneously.
        Automatically cleans up any agents that have disconnected.

        Args:
            message: Raw message content to broadcast
        """
        disconnected = []
        for agent_id, websocket in self.connections.items():
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(agent_id)

        # Clean up disconnected agents
        for agent_id in disconnected:
            await self._disconnect(agent_id)

    async def start(self):
        """Initialize and start the Pylon WebSocket server.

        Establishes the communication infrastructure that enables distributed
        AI agent coordination. Creates the power grid that constitutional
        coordination depends on.
        """
        self.server = await websockets.serve(self._connection, "localhost", self.port)
        print(f"🔹 Pylon powered up on ws://localhost:{self.port}")

    async def stop(self):
        """Stop WebSocket server."""
        if hasattr(self, "server"):
            self.server.close()
            await self.server.wait_closed()

    async def _connection(self, websocket):
        """Handle raw WebSocket connection."""
        agent_id = websocket.request.path.strip("/")
        self.connections[agent_id] = websocket
        print(f"🔹 {agent_id} connected to Pylon")

        # Notify connection handlers
        for handler in self.connection_handlers:
            await handler(agent_id)

        try:
            async for raw_message in websocket:
                # Forward raw message to all handlers
                for handler in self.message_handlers:
                    await handler(agent_id, raw_message)
        finally:
            await self._disconnect(agent_id)

    async def _disconnect(self, agent_id: str):
        """Handle agent disconnection."""
        self.connections.pop(agent_id, None)
        print(f"🔌 {agent_id} disconnected from Pylon")

        # Notify disconnection handlers
        for handler in self.disconnection_handlers:
            await handler(agent_id)

    @property
    def status(self) -> dict:
        """Basic Pylon transport status."""
        return {
            "active_connections": len(self.connections),
            "port": self.port,
            "connected_agents": list(self.connections.keys()),
        }
