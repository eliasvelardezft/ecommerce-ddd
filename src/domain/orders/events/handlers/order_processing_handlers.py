from domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO
from domain.orders.events.OrderProcessingEvent import OrderProcessingEvent
from domain.orders.repositories.IOrderReadRepository import IOrderReadRepository
from uuid import UUID

import logging

logger = logging.getLogger(__name__)

class UpdateOrderOnOrderProcessing:
    """Handler for updating read model when an order moves to PROCESSING status"""
    def __init__(self, read_repository: IOrderReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: OrderProcessingEvent) -> None:
        logger.info(f"[UpdateOrderOnOrderProcessingHandler] Updating read model for order {event.order_number} to status {event.status}")
        
        order_dto = await self._read_repository.get_order_details(id=UUID(event.aggregate_id))
        
        if order_dto:
            order_dto.status = event.status
            # Potentially update other fields if they are part of the OrderProcessingEvent and DTO
            # For now, only status is directly from the event.
            await self._read_repository.update_read_model(order_dto)
            logger.info(f"[UpdateOrderOnOrderProcessingHandler] Successfully updated read model for order {event.order_number}.")
        else:
            logger.warning(f"[UpdateOrderOnOrderProcessingHandler] OrderDetailsDTO not found for order ID {event.aggregate_id}. Cannot update read model.") 