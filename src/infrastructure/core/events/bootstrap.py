import logging

from domain.core.events.DomainEvent import DomainEvent
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.core.events.handlers.EventStoreHandler import EventStoreHandler
from infrastructure.core.events.integration_event_dispatcher import (
    IntegrationEventDispatcher,
)

logger = logging.getLogger(__name__)

def create_domain_event_dispatcher(container: dict) -> DomainEventDispatcher:
    """
    Creates the DomainEventDispatcher and registers core, non-domain-specific handlers
    like the EventStoreHandler.
    """
    logger.info("[Bootstrap] Creating DomainEventDispatcher...")
    domain_event_dispatcher = DomainEventDispatcher()
    logger.info("[Bootstrap] DomainEventDispatcher instantiated.")

    # Register a generic EventStoreHandler for all internal domain events if EventStore is configured.
    # This is typically for event sourcing persistence.
    event_store = container.get("event_store")
    if event_store:
        # Assuming DomainEventDispatcher.register_handler can take the base DomainEvent class
        # to catch all derived domain events for the store.
        domain_event_dispatcher.register_handler(
            DomainEvent, # Register for the base DomainEvent type
            EventStoreHandler(event_store)
        )
        logger.info("[Bootstrap] EventStoreHandler registered with DomainEventDispatcher.")
    else:
        logger.warning("[Bootstrap] EventStore not found in container. EventStoreHandler not registered for DomainEventDispatcher.")
    return domain_event_dispatcher

def create_integration_event_dispatcher() -> IntegrationEventDispatcher:
    """
    Creates the IntegrationEventDispatcher.
    """
    logger.info("[Bootstrap] Creating IntegrationEventDispatcher...")
    integration_event_dispatcher = IntegrationEventDispatcher()
    logger.info("[Bootstrap] IntegrationEventDispatcher instantiated.")
    return integration_event_dispatcher
