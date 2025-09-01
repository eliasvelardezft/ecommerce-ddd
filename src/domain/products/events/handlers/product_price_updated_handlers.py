import logging
from uuid import UUID

from domain.products.events.ProductPriceUpdatedEvent import (
    ProductPriceUpdatedEvent,
)
from domain.products.repositories.IProductReadRepository import (
    IProductReadRepository,
)

logger = logging.getLogger(__name__)

class UpdateProductOnProductPriceUpdated:
    def __init__(self, read_repository: IProductReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: ProductPriceUpdatedEvent) -> None:
        logger.info(f"Updating product price on event: {event.aggregate_id}, new price: {event.price.amount} {event.price.currency}")
        product_dto = await self._read_repository.get_product_details(id=UUID(event.aggregate_id))

        if product_dto:
            product_dto.price_amount = event.price.amount
            product_dto.price_currency = event.price.currency
            product_dto.updated_at = event.occurred_on # Update timestamp
            await self._read_repository.update_read_model(product_dto)
            logger.info(f"Successfully updated price for product {event.aggregate_id}")
        else:
            logger.warning(f"ProductDetailsDTO not found for product ID {event.aggregate_id} during price update.")