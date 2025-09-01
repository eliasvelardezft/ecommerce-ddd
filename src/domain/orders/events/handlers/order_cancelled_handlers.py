import logging
from uuid import UUID

from domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO
from domain.orders.events.OrderCancelledEvent import OrderCancelledEvent
from domain.orders.repositories.IOrderReadRepository import (
    IOrderReadRepository,
)

logger = logging.getLogger(__name__)

class UpdateOrderOnOrderCancelled:
    """Handler for updating read model when an order is cancelled"""
    def __init__(self, read_repository: IOrderReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: OrderCancelledEvent) -> None:
        logger.info(f"[UpdateOrderOnOrderCancelledHandler] Updating read model for order {event.order_number} to status {event.status}")
        if event.cancellation_reason:
            logger.info(f"[UpdateOrderOnOrderCancelledHandler] Cancellation reason: {event.cancellation_reason}")

        order_dto = await self._read_repository.get_order_details(id=UUID(event.aggregate_id))

        if order_dto:
            order_dto.status = event.status
            order_dto.cancellation_reason = event.cancellation_reason

            await self._read_repository.update_read_model(order_dto)
            logger.info(f"[UpdateOrderOnOrderCancelledHandler] Successfully updated read model for order {event.order_number}.")
        else:
            logger.warning(f"[UpdateOrderOnOrderCancelledHandler] OrderDetailsDTO not found for order ID {event.aggregate_id}. Cannot update read model.")