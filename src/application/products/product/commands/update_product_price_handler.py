import logging
from uuid import UUID

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.core.value_objects.Money import Money
from domain.products.repositories.IProductWriteRepository import (
    IProductWriteRepository,
)

from .UpdateProductPriceCommand import UpdateProductPriceCommand

logger = logging.getLogger(__name__)

class UpdateProductPriceHandler:
    def __init__(
        self,
        product_write_repository: IProductWriteRepository,
        domain_event_dispatcher: DomainEventDispatcher
    ):
        self._product_write_repository = product_write_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: UpdateProductPriceCommand) -> None:
        logger.info(f"Handling UpdateProductPriceCommand for Product ID: {command.product_id}")

        product = await self._product_write_repository.get_by_id(command.product_id)
        if not product:
            logger.error(f"Product with ID {command.product_id} not found.")
            raise ValueError(f"Product with ID {command.product_id} not found.")

        new_price = Money(amount=command.new_price_amount, currency=command.new_price_currency)

        product.update_price(new_price)
        logger.info(f"Updated price for product {product.id} to {new_price.amount} {new_price.currency}.")

        await self._product_write_repository.save(product)

        await self._domain_event_dispatcher.dispatch_events(product.domain_events)
        logger.info(f"Dispatched {len(product.domain_events)} domain events for product {product.id} after price update.")
        product.clear_domain_events()
