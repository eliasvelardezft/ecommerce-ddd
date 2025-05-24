from src.domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO
from src.domain.orders.events.OrderPlacedEvent import OrderPlacedEvent
from src.domain.orders.models.OrderStatus import OrderStatus
from src.domain.orders.repositories.IOrderReadRepository import IOrderReadRepository

import logging

logger = logging.getLogger(__name__)

class UpdateReadModelHandler:
    def __init__(self, read_repository: IOrderReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: OrderPlacedEvent) -> None:
        order_details = OrderDetailsDTO(
            id=str(event.aggregate_id),
            customer_id=str(event.customer_id),
            total_amount=event.total_amount,
            items_count=event.items_count,
            status=OrderStatus.DRAFT,
            created_at=event.occurred_on
        )
        await self._read_repository.update_read_model(order_details)
