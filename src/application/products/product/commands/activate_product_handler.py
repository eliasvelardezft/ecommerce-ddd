import logging
from uuid import UUID

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.products.repositories.IProductWriteRepository import (
    IProductWriteRepository,
)

from .ActivateProductCommand import ActivateProductCommand

logger = logging.getLogger(__name__)

class ActivateProductHandler:
    def __init__(
        self,
        product_write_repository: IProductWriteRepository,
        domain_event_dispatcher: DomainEventDispatcher
    ):
        self._product_write_repository = product_write_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: ActivateProductCommand) -> None:
        logger.info(f"Handling ActivateProductCommand for Product ID: {command.product_id}")

        product = await self._product_write_repository.get_by_id(command.product_id)
        if not product:
            logger.error(f"Product with ID {command.product_id} not found for activation.")
            raise ValueError(f"Product with ID {command.product_id} not found.")

        product.activate()
        logger.info(f"Product {product.id} activated.")

        await self._product_write_repository.save(product)
        
        await self._domain_event_dispatcher.dispatch_events(product.domain_events)
        logger.info(f"Dispatched {len(product.domain_events)} domain events for product {product.id} after activation.")
        product.clear_domain_events()
