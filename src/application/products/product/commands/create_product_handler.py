import logging
from uuid import UUID

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher # Assuming we'll inject this for event publishing
from domain.core.value_objects.Money import Money # Import Money VO
from domain.products.models.Product import Product
from domain.products.repositories.IProductWriteRepository import IProductWriteRepository
from domain.products.repositories.ICategoryWriteRepository import ICategoryWriteRepository # To validate category
from .CreateProductCommand import CreateProductCommand


logger = logging.getLogger(__name__)

class CreateProductHandler:
    def __init__(
        self,
        product_write_repository: IProductWriteRepository,
        category_write_repository: ICategoryWriteRepository,
        domain_event_dispatcher: DomainEventDispatcher # For explicit dispatch, or handled by UoW
    ):
        self._product_write_repository = product_write_repository
        self._category_write_repository = category_write_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: CreateProductCommand) -> UUID:
        logger.info(f"Handling CreateProductCommand for SKU: {command.sku}")

        # 1. Validate category_id (optional, but good practice in handler)
        category = await self._category_write_repository.get_by_id(command.category_id)
        if not category:
            logger.error(f"Category with ID {command.category_id} not found.")
            raise ValueError(f"Category with ID {command.category_id} not found.")

        # 2. Create Product aggregate
        # The Product.create method handles initial event creation (ProductCreatedEvent)
        price = Money(amount=command.price_amount, currency=command.price_currency)
        product = Product.create(
            name=command.name,
            description=command.description,
            sku=command.sku,
            price=price,
            category_id=command.category_id,
            stock_quantity=command.stock_quantity,
            image_url=command.image_url,
            attributes=command.attributes,
            active=command.active
        )

        # 3. Persist the aggregate
        await self._product_write_repository.save(product)
        logger.info(f"Product {product.id} created successfully with SKU {product.sku}.")

        # 4. Dispatch domain events
        # This might be handled by a Unit of Work pattern or a decorator in a full setup.
        # For explicitness here, we can dispatch them directly if the dispatcher is provided.
        await self._domain_event_dispatcher.dispatch_events(product.domain_events)
        logger.info(f"Dispatched {len(product.domain_events)} domain events for product {product.id}.")
        product.clear_domain_events()

        return product
