import logging

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.products.repositories.IProductWriteRepository import (
    IProductWriteRepository,
)

from .UpdateProductStockCommand import UpdateProductStockCommand

logger = logging.getLogger(__name__)

class UpdateProductStockHandler:
    def __init__(
        self,
        product_write_repository: IProductWriteRepository,
        domain_event_dispatcher: DomainEventDispatcher
    ):
        self._product_write_repository = product_write_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: UpdateProductStockCommand) -> None:
        logger.info(f"Handling UpdateProductStockCommand for Product ID: {command.product_id}, Change: {command.change_in_quantity}")

        product = await self._product_write_repository.get_by_id(command.product_id)
        if not product:
            logger.error(f"Product with ID {command.product_id} not found.")
            raise ValueError(f"Product with ID {command.product_id} not found.")

        if command.change_in_quantity > 0:
            product.add_stock(command.change_in_quantity)
            logger.info(f"Added {command.change_in_quantity} to stock for product {product.id}. New stock: {product.stock_quantity}")
        elif command.change_in_quantity < 0:
            product.remove_stock(abs(command.change_in_quantity))
            logger.info(f"Removed {abs(command.change_in_quantity)} from stock for product {product.id}. New stock: {product.stock_quantity}")
        else:
            logger.info(f"Stock change is zero for product {product.id}. No action taken.")
            return

        await self._product_write_repository.save(product)

        await self._domain_event_dispatcher.dispatch_events(product.domain_events)
        logger.info(f"Dispatched {len(product.domain_events)} domain events for product {product.id} after stock update.")
        product.clear_domain_events()
