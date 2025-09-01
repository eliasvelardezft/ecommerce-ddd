from domain.core.events.DomainEvent import DomainEvent
from domain.core.events.EventStore import EventStore
from domain.core.events.handlers.DomainEventHandler import DomainEventHandler


class EventStoreHandler(DomainEventHandler[DomainEvent]):
    """Handler that stores all domain events in the event store"""
    
    def __init__(self, event_store: EventStore):
        self._event_store = event_store

    async def handle(self, event: DomainEvent) -> None:
        """Store the event in the event store"""
        await self._event_store.append(event)
