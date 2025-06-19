import logging
from uuid import UUID

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.products.repositories.ICategoryWriteRepository import ICategoryWriteRepository
from domain.products.repositories.ICategoryReadRepository import ICategoryReadRepository # To validate new parent
from .ChangeCategoryParentCommand import ChangeCategoryParentCommand

logger = logging.getLogger(__name__)

class ChangeCategoryParentHandler:
    def __init__(
        self,
        category_write_repository: ICategoryWriteRepository,
        category_read_repository: ICategoryReadRepository, # For new parent validation
        domain_event_dispatcher: DomainEventDispatcher
    ):
        self._category_write_repository = category_write_repository
        self._category_read_repository = category_read_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: ChangeCategoryParentCommand) -> None:
        logger.info(f"Handling ChangeCategoryParentCommand for category ID: {command.category_id}")

        category_to_reparent = await self._category_write_repository.get_by_id(command.category_id)
        if not category_to_reparent:
            logger.error(f"Category with ID {command.category_id} not found to change parent.")
            raise ValueError(f"Category with ID {command.category_id} not found.")

        if command.new_parent_category_id == category_to_reparent.id:
            logger.error(f"Category {command.category_id} cannot be its own parent.")
            raise ValueError("A category cannot be its own parent.")

        # Validate new_parent_category_id if provided
        if command.new_parent_category_id:
            new_parent_category = await self._category_read_repository.get_category(command.new_parent_category_id)
            if not new_parent_category:
                logger.error(f"New parent category with ID {command.new_parent_category_id} not found.")
                raise ValueError(f"New parent category with ID {command.new_parent_category_id} not found.")

        category_to_reparent.change_parent(new_parent_category_id=command.new_parent_category_id)

        if category_to_reparent.domain_events:
            await self._category_write_repository.save(category_to_reparent)
            logger.info(f"Category {category_to_reparent.id} parent changed successfully.")
            
            await self._domain_event_dispatcher.dispatch_events(category_to_reparent.domain_events)
            logger.info(f"Dispatched {len(category_to_reparent.domain_events)} domain events for category {category_to_reparent.id} after parent change.")
            category_to_reparent.clear_domain_events()
        else:
            logger.info(f"No change in parent for category {command.category_id}. No update performed.")
