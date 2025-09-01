import logging
from uuid import UUID

from domain.products.events.ProductActivatedEvent import ProductActivatedEvent
from domain.products.repositories.IProductReadRepository import (
    IProductReadRepository,
)

logger = logging.getLogger(__name__)

class UpdateProductOnProductActivated:
    def __init__(self, read_repository: IProductReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: ProductActivatedEvent) -> None:
        logger.info(f"Activating product on event: {event.aggregate_id}")
        product_dto = await self._read_repository.get_product_details_by_id(product_id=UUID(event.aggregate_id))

        if product_dto:
            product_dto.active = True
            product_dto.updated_at = event.occurred_on # Update timestamp
            await self._read_repository.update_read_model(product_dto)
            logger.info(f"Successfully activated product {event.aggregate_id}")
        else:
            logger.warning(f"ProductDetailsDTO not found for product ID {event.aggregate_id} during activation.")
