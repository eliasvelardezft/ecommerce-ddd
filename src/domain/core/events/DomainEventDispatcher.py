import logging
from typing import Any

from .DomainEvent import DomainEvent

logger = logging.getLogger(__name__)


class DomainEventDispatcher:
    """Handles dispatching of INTERNAL DomainEvents to their respective handlers within the same Bounded Context."""
    def __init__(self):
        # Registry: InternalEventType -> List[HandlerInstance]
        # Using Type[Any] for key if events don't all share a very specific common base other than object
        # Using Any for handler type if no common base handler class
        self._handlers: dict[type[DomainEvent], list[Any]] = {}
        logger.info("[DomainEventDispatcher] Initialized for internal domain events.")

    def register_handler(self, event_type: type[DomainEvent], handler: Any) -> None:
        """Register a handler for a specific internal domain event type."""
        if not issubclass(event_type, DomainEvent):
            logger.error(f"Attempted to register handler for non-DomainEvent type: {event_type.__name__}")
            return

        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        handler_name = handler.__class__.__name__ if hasattr(handler, '__class__') else str(handler)
        logger.info(f"[DomainEventDispatcher] Registered internal handler '{handler_name}' for event '{event_type.__name__}'")

    async def dispatch(self, event: DomainEvent) -> None:
        """Dispatch an internal domain event to all registered internal handlers."""
        event_type = type(event)
        logger.info(f"[DomainEventDispatcher] Dispatching internal event: {event_type.__name__} (ID: {event.id if hasattr(event, 'id') else 'N/A'})")

        # Handlers for the specific event type
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler_name = handler.__class__.__name__ if hasattr(handler, '__class__') else str(handler)
                logger.debug(f"[DomainEventDispatcher] Executing internal handler '{handler_name}' for '{event_type.__name__}'")
                try:
                    await handler.handle(event) # Assuming handlers have an async 'handle' method
                except Exception as e:
                    logger.error(f"[DomainEventDispatcher] Error in internal handler '{handler_name}' for event '{event_type.__name__}': {e}", exc_info=True)

        # Handlers for the base DomainEvent type (e.g., EventStoreHandler for internal events)
        # This ensures base handlers run for all specific event types, unless event_type is DomainEvent itself.
        if DomainEvent in self._handlers and event_type is not DomainEvent:
            for handler in self._handlers[DomainEvent]:
                handler_name = handler.__class__.__name__ if hasattr(handler, '__class__') else str(handler)
                logger.debug(f"[DomainEventDispatcher] Executing base DomainEvent handler '{handler_name}' for specific event '{event_type.__name__}'")
                try:
                    await handler.handle(event)
                except Exception as e:
                    logger.error(f"[DomainEventDispatcher] Error in base DomainEvent handler '{handler_name}' for event '{event_type.__name__}': {e}", exc_info=True)

        # If the event itself is of type DomainEvent (e.g. a generic event was dispatched)
        elif event_type is DomainEvent and DomainEvent in self._handlers:
            for handler in self._handlers[DomainEvent]:
                handler_name = handler.__class__.__name__ if hasattr(handler, '__class__') else str(handler)
                logger.debug(f"[DomainEventDispatcher] Executing handler '{handler_name}' for generic DomainEvent")
                try:
                    await handler.handle(event)
                except Exception as e:
                    logger.error(f"[DomainEventDispatcher] Error in handler '{handler_name}' for generic DomainEvent: {e}", exc_info=True)

        if event_type not in self._handlers and (event_type is not DomainEvent or DomainEvent not in self._handlers):
            logger.debug(f"[DomainEventDispatcher] No specific or base handlers registered for internal event '{event_type.__name__}'")

    async def dispatch_events(self, events: list[DomainEvent]) -> None:
        """Dispatch a list of domain events to all registered handlers."""
        logger.info(f"[DomainEventDispatcher] Dispatching {len(events)} domain events")
        for event in events:
            await self.dispatch(event)

    def clear(self) -> None:
        """Clear all registered internal handlers."""
        self._handlers.clear()
        logger.info("[DomainEventDispatcher] All internal handlers cleared.")