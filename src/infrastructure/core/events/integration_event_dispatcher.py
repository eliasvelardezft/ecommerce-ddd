# src/infrastructure/core/events/integration_event_dispatcher.py
import logging
from typing import Any

from pydantic import (
    BaseModel as PydanticBaseModel,  # Integration events are Pydantic models
)

# If you have a base IntegrationEventHandler class, you can import and use it

logger = logging.getLogger(__name__)

class IntegrationEventDispatcher:
    """
    Handles dispatching of PUBLIC IntegrationEventContracts (Pydantic models) 
    to their respective handlers across Bounded Contexts (within the monolith).
    In a microservices architecture, this would be replaced by a message bus (e.g., Kafka, RabbitMQ).
    """
    def __init__(self):
        # Registry: PublicContractDTOType -> List[HandlerInstance]
        self._handlers: dict[type[PydanticBaseModel], list[Any]] = {}
        logger.info("[IntegrationEventDispatcher] Initialized for public integration event contracts.")

    def register_handler(self, contract_event_type: type[PydanticBaseModel], handler: Any) -> None:
        """Register a handler for a specific public integration event contract type."""
        if not issubclass(contract_event_type, PydanticBaseModel):
            logger.error(
                f"[IntegrationEventDispatcher] Attempted to register handler for non-Pydantic type: "
                f"{contract_event_type.__name__}. Integration event handlers should subscribe to Pydantic model contracts."
            )
            return

        if contract_event_type not in self._handlers:
            self._handlers[contract_event_type] = []
        self._handlers[contract_event_type].append(handler)
        handler_name = handler.__class__.__name__ if hasattr(handler, '__class__') else str(handler)
        logger.info(
            f"[IntegrationEventDispatcher] Registered integration handler '{handler_name}' "
            f"for contract '{contract_event_type.__name__}'")

    async def dispatch(self, contract_event: PydanticBaseModel) -> None:
        """Dispatch a public integration event contract to all registered integration handlers."""
        contract_event_type = type(contract_event)
        # Using a field like 'event_type' from the contract itself for more descriptive logging
        event_type_name_attr = getattr(contract_event, 'event_type', contract_event_type.__name__)
        event_id_attr = getattr(contract_event, 'event_id', 'N/A')
        logger.info(f"[IntegrationEventDispatcher] Dispatching public contract: {event_type_name_attr} (ID: {event_id_attr})")

        if contract_event_type in self._handlers:
            for handler in self._handlers[contract_event_type]:
                handler_name = handler.__class__.__name__ if hasattr(handler, '__class__') else str(handler)
                logger.debug(
                    f"[IntegrationEventDispatcher] Executing integration handler '{handler_name}' "
                    f"for contract '{contract_event_type.__name__}'")
                try:
                    await handler.handle(contract_event) # Assuming handlers have an async 'handle' method
                except Exception as e:
                    logger.error(
                        f"[IntegrationEventDispatcher] Error in integration handler '{handler_name}' "
                        f"for contract '{contract_event_type.__name__}': {e}", exc_info=True)
        else:
            logger.debug(f"[IntegrationEventDispatcher] No handlers registered for public contract '{contract_event_type.__name__}'")

    def clear(self) -> None:
        """Clear all registered integration handlers."""
        self._handlers.clear()
        logger.info("[IntegrationEventDispatcher] All integration handlers cleared.")
