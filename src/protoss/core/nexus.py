import asyncio
import logging
from collections import defaultdict
from typing import AsyncIterator, Dict, List, Optional, Tuple

from .message import Event  # Assuming Event dataclass will be defined here or imported

logger = logging.getLogger(__name__)


class Nexus:
    """
    The internal event bus for the Protoss swarm.
    Provides publish/subscribe functionality for inter-component communication.
    """

    def __init__(self):
        # Mapping event_type -> list of (queue, filter_channel)
        self._subscribers: Dict[
            Optional[str], List[Tuple[asyncio.Queue, Optional[str]]]
        ] = defaultdict(list)
        # A general queue for subscribers interested in all events
        self._general_subscribers: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    async def publish(self, event: Event):
        """
        Publishes an event to all relevant subscribers.
        """
        if not isinstance(event, Event):
            logger.error(f"Attempted to publish non-Event object: {type(event)}")
            return

        # Publish to general subscribers
        for queue in self._general_subscribers:
            await queue.put(event)

        # Publish to type-specific subscribers
        if event.type in self._subscribers:
            for queue, filter_channel in self._subscribers[event.type]:
                if filter_channel is None or filter_channel == event.channel:
                    await queue.put(event)

        logger.debug(f"Published event: {event.type} to channel {event.channel}")

    async def subscribe(
        self, event_type: Optional[str] = None, channel: Optional[str] = None
    ) -> AsyncIterator[Event]:
        """
        Subscribes to events.
        If event_type is None, subscribes to all events.
        If channel is not None, filters events by channel for type-specific subscriptions.
        """
        queue = asyncio.Queue()
        async with self._lock:
            if event_type is None:
                self._general_subscribers.append(queue)
            else:
                self._subscribers[event_type].append((queue, channel))

        logger.debug(f"New subscriber for event_type={event_type}, channel={channel}")

        try:
            while True:
                yield await queue.get()
        except asyncio.CancelledError:
            logger.debug(
                f"Subscriber cancelled for event_type={event_type}, channel={channel}"
            )
        finally:
            async with self._lock:
                if event_type is None:
                    if queue in self._general_subscribers:
                        self._general_subscribers.remove(queue)
                else:
                    if (queue, channel) in self._subscribers[event_type]:
                        self._subscribers[event_type].remove((queue, channel))
