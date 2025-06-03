import logging
from uuid import UUID

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.products.repositories.IProductWriteRepository import IProductWriteRepository
from .DeactivateProductCommand import DeactivateProductCommand

logger = logging.getLogger(__name__)

class DeactivateProductHandler:
    def __init__(
        self,
        product_write_repository: IProductWriteRepository,
        domain_event_dispatcher: DomainEventDispatcher
    ):
        self._product_write_repository = product_write_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: DeactivateProductCommand) -> None:
        logger.info(f"Handling DeactivateProductCommand for Product ID: {command.product_id}")

        product = await self._product_write_repository.get_by_id(command.product_id)
        if not product:
            logger.error(f"Product with ID {command.product_id} not found for deactivation.")
            raise ValueError(f"Product with ID {command.product_id} not found.")

        product.deactivate()
        logger.info(f"Product {product.id} deactivated.")

        await self._product_write_repository.save(product)
        
        await self._domain_event_dispatcher.dispatch_events(product.domain_events)
        logger.info(f"Dispatched {len(product.domain_events)} domain events for product {product.id} after deactivation.")
        product.clear_domain_events()
