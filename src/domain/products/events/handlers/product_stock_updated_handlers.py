import logging
from uuid import UUID

from domain.products.dtos.ProductDetailsDTO import ProductDetailsDTO
from domain.products.events.ProductStockUpdatedEvent import ProductStockUpdatedEvent
from domain.products.repositories.IProductReadRepository import IProductReadRepository

logger = logging.getLogger(__name__)

class UpdateProductOnProductStockUpdated:
    def __init__(self, read_repository: IProductReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: ProductStockUpdatedEvent) -> None:
        logger.info(f"Updating product stock on event: {event.aggregate_id}, new stock: {event.stock_quantity}")
        product_dto = await self._read_repository.get_product_details(id=UUID(event.aggregate_id))
        
        if product_dto:
            product_dto.stock_quantity = event.stock_quantity
            product_dto.updated_at = event.occurred_on # Update timestamp
            await self._read_repository.update_read_model(product_dto)
            logger.info(f"Successfully updated stock for product {event.aggregate_id}")
        else:
            logger.warning(f"ProductDetailsDTO not found for product ID {event.aggregate_id} during stock update.") 