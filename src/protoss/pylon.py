"""Pylon: Communication grid for Protoss coordination.

Single responsibility: Route §PSI messages between agents.
Zero ceremony. Pure message flow.
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional
import websockets


@dataclass
class Psi:
    """Atomic communication unit."""

    target: str
    source: str
    type: str
    content: str

    @classmethod
    def parse(cls, raw: str) -> Optional["Psi"]:
        """Parse §PSI:target:source:type:content"""
        if not raw.startswith("§PSI:"):
            return None

        try:
            _, target, source, msg_type, content = raw.split(":", 4)
            return cls(target=target, source=source, type=msg_type, content=content)
        except ValueError:
            return None

    def serialize(self) -> str:
        """Serialize to §PSI format."""
        return f"§PSI:{self.target}:{self.source}:{self.type}:{self.content}"


class Pylon:
    """Message router. Powers the coordination grid."""

    def __init__(self, port: int = 8228):
        self.port = port
        self.agents: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.inbox: Dict[str, List[Psi]] = {}
        self.message_queue = asyncio.Queue()

    async def start(self):
        """Start Pylon grid."""
        self.server = await websockets.serve(
            self._handle_connection, "localhost", self.port
        )
        self.router_task = asyncio.create_task(self._route())

    async def stop(self):
        """Stop Pylon grid."""
        if hasattr(self, "router_task"):
            self.router_task.cancel()
        if hasattr(self, "server"):
            self.server.close()
            await self.server.wait_closed()

    async def _flush(self, agent_id: str, websocket):
        """Deliver queued messages to agent."""
        if agent_id in self.inbox:
            for message in self.inbox[agent_id]:
                try:
                    await websocket.send(message.serialize())
                except websockets.exceptions.ConnectionClosed:
                    return
            # Clear delivered messages
            del self.inbox[agent_id]

    async def _handle_connection(self, websocket):
        """Handle agent connection to grid."""
        agent_id = websocket.request.path.strip("/")
        self.agents[agent_id] = websocket
        
        # Flush queued messages when agent connects
        await self._flush(agent_id, websocket)

        try:
            async for raw_message in websocket:
                message = Psi.parse(raw_message)
                if message:
                    await self.message_queue.put(message)
        finally:
            self.agents.pop(agent_id, None)

    async def _route(self):
        """Route messages to target agents or inbox."""
        while True:
            message = await self.message_queue.get()
            target_socket = self.agents.get(message.target)

            if target_socket:
                # Agent online - deliver immediately
                try:
                    await target_socket.send(message.serialize())
                except websockets.exceptions.ConnectionClosed:
                    self.agents.pop(message.target, None)
            else:
                # Agent offline - queue in inbox
                if message.target not in self.inbox:
                    self.inbox[message.target] = []
                self.inbox[message.target].append(message)
