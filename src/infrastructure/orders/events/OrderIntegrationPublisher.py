import logging
from typing import Callable

from pydantic import BaseModel as PydanticBaseModel

from domain.core.events.DomainEvent import DomainEvent

# Import specific internal event types from the Order domain that can become public
from domain.orders.events.OrderPlacedEvent import (
    OrderPlacedEvent as InternalOrderPlacedEvent,
)
from infrastructure.core.events.integration_event_dispatcher import (
    IntegrationEventDispatcher,
)

# from domain.orders.events.OrderCancelledEvent import OrderCancelledEvent as InternalOrderCancelledEvent # Example
# Import their corresponding mappers
from infrastructure.orders.events.mappers import (
    map_internal_order_placed_to_v1_contract,
)

logger = logging.getLogger(__name__)

class OrderIntegrationEventPublisher:
    """
    Responsible for converting internal Order domain events into public integration event contracts
    and dispatching them via the central IntegrationEventDispatcher.
    This publisher is specific to the Orders Bounded Context.
    """
    def __init__(self, integration_event_dispatcher: IntegrationEventDispatcher):
        self._integration_event_dispatcher = integration_event_dispatcher
        # Registry: InternalOrderEventType -> CallableMapperFunction (maps internal to public contract)
        self._mappers: dict[type[DomainEvent], Callable[[DomainEvent], PydanticBaseModel | None]] = {}
        self._register_default_mappers()
        logger.info("[OrderIntegrationEventPublisher] Initialized.")

    def _register_default_mappers(self):
        """Pre-registers known mappers for Order domain's public events."""
        self.register_mapper(
            InternalOrderPlacedEvent,
            map_internal_order_placed_to_v1_contract
        )
        logger.info("[OrderIntegrationEventPublisher] Default mappers registered.")

    def register_mapper(
        self,
        internal_event_type: type[DomainEvent],
        mapper_func: Callable[[DomainEvent], PydanticBaseModel | None]
    ) -> None:
        """Allows dynamic registration of mappers if needed (e.g., during bootstrap for plugin-like extensions)."""
        if not issubclass(internal_event_type, DomainEvent):
            logger.error(
                f"[OrderIntegrationEventPublisher] Attempted to register mapper for non-DomainEvent type: "
                f"{internal_event_type.__name__}"
            )
            return

        if internal_event_type in self._mappers:
            logger.warning(f"[OrderIntegrationEventPublisher] Re-registering mapper for internal event {internal_event_type.__name__}")
        self._mappers[internal_event_type] = mapper_func
        logger.info(f"[OrderIntegrationEventPublisher] Registered mapper for internal event {internal_event_type.__name__}")

    async def publish(self, internal_event: DomainEvent) -> None:
        """
        Maps a single internal domain event (passed by a command handler) to its public contract
        (if a mapper is registered) and dispatches the contract via the IntegrationEventDispatcher.
        """
        internal_event_type = type(internal_event)
        mapper = self._mappers.get(internal_event_type)

        if mapper:
            logger.info(
                f"[OrderIntegrationEventPublisher] Found mapper for internal event {internal_event_type.__name__}. "
                f"Creating public contract."
            )
            public_contract_event = mapper(internal_event)
            if public_contract_event:
                event_type_name = getattr(public_contract_event, 'event_type', public_contract_event.__class__.__name__)
                logger.info(
                    f"[OrderIntegrationEventPublisher] Publishing public contract: {event_type_name} "
                    f"(from internal {internal_event_type.__name__})"
                )
                await self._integration_event_dispatcher.dispatch(public_contract_event)
            else:
                logger.warning(
                    f"[OrderIntegrationEventPublisher] Mapper for {internal_event_type.__name__} returned None. "
                    f"No public contract dispatched."
                )
        else:
            # This indicates that the Command Handler called .publish() for an internal event
            # that does not have a registered mapper, meaning it's not intended to be a public event,
            # or the mapper registration is missing.
            logger.debug(
                f"[OrderIntegrationEventPublisher] No mapper registered for internal event type {internal_event_type.__name__}. "
                f"Public contract not published. This might be intended if the event is internal-only."
            )
