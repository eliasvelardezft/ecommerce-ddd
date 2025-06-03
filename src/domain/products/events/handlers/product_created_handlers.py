import logging
from uuid import UUID

from domain.products.dtos.ProductDetailsDTO import ProductDetailsDTO
from domain.products.events.ProductCreatedEvent import ProductCreatedEvent
from domain.products.repositories.IProductReadRepository import IProductReadRepository
from domain.products.value_objects.ImageUrl import ImageUrl
from domain.products.value_objects.Attribute import Attribute

logger = logging.getLogger(__name__)


class UpdateProductOnProductCreated:
    def __init__(self, read_repository: IProductReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: ProductCreatedEvent) -> None:
        logger.info(f"Creating product read model on ProductCreatedEvent: {event.aggregate_id}")

        image_url = ImageUrl(
            url=event.image_url,
            alt_text=event.image_alt_text
        ) if event.image_url else None

        attributes = [Attribute(**attr) for attr in event.attributes]

        product_details = ProductDetailsDTO(
            id=UUID(event.aggregate_id),
            name=event.name,
            description=event.description,
            sku=event.sku,
            active=event.active,
            stock_quantity=event.stock_quantity,
            price_amount=event.price_amount,
            price_currency=event.price_currency,
            category_id=event.category_id,
            attributes=attributes,
            image_url=image_url,
            created_at=event.occurred_on,
            updated_at=event.occurred_on # Initially, updated_at is same as created_at
        )
        await self._read_repository.update_read_model(product_details)
        logger.info(f"Successfully created/updated read model for product {event.aggregate_id}")
