"""Simple message bus for conversational coordination."""

import asyncio
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class Message:
    """A single message in conversation."""
    sender: str
    content: str
    timestamp: float
    channel: str = "human"
    
    def to_dict(self) -> Dict:
        return asdict(self)


class Bus:
    """Minimal message bus - stores and routes conversation."""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        
    async def send(self, sender: str, content: str, channel: str = "human"):
        """Send a message to channel."""
        message = Message(
            sender=sender,
            content=content,
            timestamp=time.time(),
            channel=channel
        )
        
        self.messages.append(message)
        
        # Notify subscribers
        for queue in self.subscribers.get(channel, []):
            await queue.put(message)
            
    def get_history(self, channel: str = "human", since: Optional[float] = None) -> List[Dict]:
        """Get conversation history for context assembly."""
        messages = [
            msg for msg in self.messages 
            if msg.channel == channel and (since is None or msg.timestamp > since)
        ]
        return [msg.to_dict() for msg in messages]
        
    async def subscribe(self, channel: str = "human"):
        """Subscribe to new messages in channel."""
        queue = asyncio.Queue()
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(queue)
        
        try:
            while True:
                message = await queue.get()
                yield message
        finally:
            self.subscribers[channel].remove(queue)