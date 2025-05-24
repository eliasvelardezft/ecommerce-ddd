from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from src.domain.core.events.EventStore import EventStore
from src.domain.core.events.handlers.EventStoreHandler import EventStoreHandler
from .registry import register_customer_event_handlers, register_order_event_handlers


def configure_dispatcher(container):
    """Create and configure the domain event dispatcher with all handlers"""
    # Create dispatcher
    dispatcher = DomainEventDispatcher()
    
    # Register event store handler for all events
    event_store = container.get("event_store", EventStore())
    dispatcher.register_handler(
        "DomainEvent",  # Base event type
        EventStoreHandler(event_store)
    )
    
    # Register domain-specific handlers
    register_customer_event_handlers(dispatcher, container)
    register_order_event_handlers(dispatcher, container)
    
    return dispatcher
