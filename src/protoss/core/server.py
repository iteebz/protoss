"""WebSocket server for the Protoss Bus."""

import asyncio
import json
import logging
import websockets
from typing import Callable, Dict, Set

logger = logging.getLogger(__name__)

class Server:
    """Manages WebSocket connections for the Bus."""

    def __init__(self, port: int):
        self.port = port
        self.server = None
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.agent_to_ws: Dict[str, websockets.WebSocketServerProtocol] = {}

        # Callbacks
        self._on_message: Callable[[str, str], None] = None
        self._on_connect: Callable[[str], None] = None
        self._on_disconnect: Callable[[str], None] = None

    def on_message(self, callback: Callable[[str, str], None]):
        """Register a callback for incoming messages."""
        self._on_message = callback

    def on_connect(self, callback: Callable[[str], None]):
        """Register a callback for new connections."""
        self._on_connect = callback

    def on_disconnect(self, callback: Callable[[str], None]):
        """Register a callback for disconnections."""
        self._on_disconnect = callback

    async def start(self):
        """Start the WebSocket server."""
        if self.server:
            return
        import functools
        self.server = await websockets.serve(
            functools.partial(self._handler), "localhost", self.port
        )
        logger.info(f"Protoss Server started on port {self.port}")

    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            logger.info("Protoss Server stopped")

    async def send(self, agent_id: str, message: str):
        """Send a message to a specific agent."""
        websocket = self.agent_to_ws.get(agent_id)
        if websocket and websocket.open:
            try:
                await websocket.send(message)
            except websockets.ConnectionClosed:
                # The connection might have closed between the check and the send
                pass

    def is_running(self) -> bool:
        """Check if the server is running."""
        return self.server is not None

    async def _handler(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle incoming WebSocket connections."""
        agent_id = path.lstrip("/")
        self.connections[agent_id] = websocket
        self.agent_to_ws[agent_id] = websocket

        if self._on_connect:
            await self._on_connect(agent_id)

        try:
            async for message in websocket:
                if self._on_message:
                    await self._on_message(agent_id, message)
        except websockets.ConnectionClosed:
            pass
        finally:
            del self.connections[agent_id]
            del self.agent_to_ws[agent_id]
            if self._on_disconnect:
                await self._on_disconnect(agent_id)