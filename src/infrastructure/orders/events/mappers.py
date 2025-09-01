from domain.orders.events.OrderPlacedEvent import (
    OrderPlacedEvent as InternalOrderPlacedEvent,
)
from integration_contracts.events.order.order_placed import (
    OrderPlacedEventContractV1,
)


def map_internal_order_placed_to_v1_contract(
    internal_event: InternalOrderPlacedEvent
) -> OrderPlacedEventContractV1:
    """Maps the internal OrderPlacedEvent to its V1 public contract."""
    # The contract DTO (OrderPlacedEventContractV1) uses default_factory for event_id and occurred_on
    return OrderPlacedEventContractV1(
        order_id=internal_event.aggregate_id, # aggregate_id from DomainEvent is the order_id
        customer_id=str(internal_event.customer_id),
        total_amount=internal_event.total_amount,
        currency=internal_event.currency,
        item_count=internal_event.items_count, # Using the property from internal event
        occurred_on=internal_event.occurred_on,
    )
