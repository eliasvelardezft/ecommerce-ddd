import logging

from domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO, OrderItemDTO
from domain.orders.events.OrderPlacedEvent import OrderPlacedEvent
from domain.orders.models.OrderStatus import OrderStatus
from domain.orders.repositories.IOrderReadRepository import (
    IOrderReadRepository,
)

logger = logging.getLogger(__name__)

class UpdateOrderOnOrderPlaced:
    def __init__(self, read_repository: IOrderReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: OrderPlacedEvent) -> None:
        # Convert items_data to OrderItemDTO objects
        items = [
            OrderItemDTO(
                product_id=str(item_data["product_id"]),  # Convert EntityId to string
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                subtotal=float(item_data["unit_price"]["amount"]) * item_data["quantity"],
                final_price=float(item_data["unit_price"]["amount"]) * item_data["quantity"]
            )
            for item_data in event.items_data
        ]
        
        order_details = OrderDetailsDTO(
            id=str(event.aggregate_id),
            customer_id=str(event.customer_id),
            items=items,
            total_amount=event.total_amount,
            currency=event.currency,
            items_count=event.items_count,
            status=OrderStatus.DRAFT,
            created_at=event.occurred_on
        )
        await self._read_repository.update_read_model(order_details)
