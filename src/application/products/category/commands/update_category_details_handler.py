import logging
from uuid import UUID

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.products.repositories.ICategoryWriteRepository import ICategoryWriteRepository
from .UpdateCategoryDetailsCommand import UpdateCategoryDetailsCommand

logger = logging.getLogger(__name__)

class UpdateCategoryDetailsHandler:
    def __init__(
        self,
        category_write_repository: ICategoryWriteRepository,
        domain_event_dispatcher: DomainEventDispatcher
    ):
        self._category_write_repository = category_write_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: UpdateCategoryDetailsCommand) -> None:
        logger.info(f"Handling UpdateCategoryDetailsCommand for category ID: {command.category_id}")

        category = await self._category_write_repository.get_by_id(command.category_id)
        if not category:
            logger.error(f"Category with ID {command.category_id} not found for details update.")
            raise ValueError(f"Category with ID {command.category_id} not found.")

        category.update_details(
            name=command.name,
            description=command.description
        )

        if category.domain_events:
            await self._category_write_repository.save(category)
            logger.info(f"Category {category.id} details updated successfully.")
            
            await self._domain_event_dispatcher.dispatch_events(category.domain_events)
            logger.info(f"Dispatched {len(category.domain_events)} domain events for category {category.id} after details update.")
            category.clear_domain_events()
        else:
            logger.info(f"No changes detected for category {command.category_id}. No update performed.") 