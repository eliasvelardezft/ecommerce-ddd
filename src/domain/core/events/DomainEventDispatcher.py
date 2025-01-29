from typing import Dict, List, Type
from .DomainEvent import DomainEvent
from .handlers.DomainEventHandler import DomainEventHandler
import logging

logger = logging.getLogger(__name__)


class DomainEventDispatcher:
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[DomainEventHandler]] = {}
        logger.info("[Dispatcher] Initialized")

    def register_handler(self, event_type: Type[DomainEvent], handler: DomainEventHandler) -> None:
        """Register a handler for a specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info("[Dispatcher] Registered handler %s for event %s", 
                   handler.__class__.__name__, 
                   event_type.__name__)

    async def dispatch(self, event: DomainEvent) -> None:
        """Dispatch an event to all registered handlers"""
        event_type = type(event)
        logger.info("[Dispatcher] Dispatching event %s", event_type.__name__)
        
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                logger.info("[Dispatcher] Executing handler %s", handler.__class__.__name__)
                await handler.handle(event)
        else:
            logger.warning("[Dispatcher] No handlers registered for event %s", event_type.__name__)

    def clear(self) -> None:
        """Clear all registered handlers"""
        self._handlers.clear() 