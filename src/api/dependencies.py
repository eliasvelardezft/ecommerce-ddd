"""Core/infrastructure dependencies"""
from fastapi import Depends

from src.domain.core.events.DomainEvent import DomainEvent
from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from src.domain.core.events.EventStore import EventStore
from src.domain.core.events.handlers.EventStoreHandler import EventStoreHandler


def get_event_store():
    return EventStore()


def get_base_event_dispatcher(
    event_store: EventStore = Depends(get_event_store)
):
    """Creates a base event dispatcher with common handlers like event store"""
    dispatcher = DomainEventDispatcher()
    
    # Register event store handler for all events
    dispatcher.register_handler(
        DomainEvent,  # Base event type to handle all events
        EventStoreHandler(event_store)
    )
    
    return dispatcher
