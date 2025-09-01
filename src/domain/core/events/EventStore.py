from typing import List

from .DomainEvent import DomainEvent
from .StoredEvent import StoredEvent


class EventStore:
    """Stores and retrieves domain events"""
    def __init__(self):
        self._events: List[StoredEvent] = []

    async def append(self, event: DomainEvent) -> None:
        """Store a new event"""
        stored_event = StoredEvent.from_domain_event(event)
        self._events.append(stored_event)

    async def get_events(self, aggregate_id: str) -> List[StoredEvent]:
        """Get all events for an aggregate"""
        return [e for e in self._events if e.aggregate_id == aggregate_id]
