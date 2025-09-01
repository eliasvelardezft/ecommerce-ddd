import logging

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.core.value_objects.EntityId import EntityId
from domain.products.repositories.ICategoryWriteRepository import (
    ICategoryWriteRepository,
)

from .ChangeCategoryParentCommand import ChangeCategoryParentCommand

logger = logging.getLogger(__name__)

class ChangeCategoryParentHandler:
    def __init__(
        self,
        category_write_repository: ICategoryWriteRepository,
        domain_event_dispatcher: DomainEventDispatcher
    ):
        self._category_write_repository = category_write_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: ChangeCategoryParentCommand) -> None:
        logger.info(f"Handling ChangeCategoryParentCommand for category ID: {command.category_id}")

        category_id = EntityId.from_string(command.category_id)
        category = await self._category_write_repository.get_by_id(category_id)
        if not category:
            logger.error(f"Category with ID {command.category_id} not found for parent change.")
            raise ValueError(f"Category with ID {command.category_id} not found.")

        # Validate new parent exists if provided (None is allowed for top-level categories)
        new_parent_id = None
        if command.new_parent_category_id:
            new_parent_id = EntityId.from_string(command.new_parent_category_id)
            new_parent = await self._category_write_repository.get_by_id(new_parent_id)
            if not new_parent:
                logger.error(f"New parent category with ID {command.new_parent_category_id} not found.")
                raise ValueError(f"New parent category with ID {command.new_parent_category_id} not found.")

            # Business rule: Category cannot be its own parent
            if command.new_parent_category_id == command.category_id:
                logger.error(f"Category {command.category_id} cannot be its own parent.")
                raise ValueError("A category cannot be its own parent.")

        category.change_parent(new_parent_id)
        logger.info(f"Parent changed for category {category.id} to {command.new_parent_category_id}.")

        await self._category_write_repository.save(category)
        
        await self._domain_event_dispatcher.dispatch_events(category.domain_events)
        logger.info(f"Dispatched {len(category.domain_events)} domain events for category {category.id} after parent change.")
        category.clear_domain_events()
