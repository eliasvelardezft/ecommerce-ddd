import logging
from uuid import UUID

from domain.products.events.CategoryParentChangedEvent import CategoryParentChangedEvent
from domain.products.repositories.ICategoryReadRepository import ICategoryReadRepository


logger = logging.getLogger(__name__)

class UpdateCategoryOnCategoryParentChanged:
    def __init__(self, read_repository: ICategoryReadRepository):
        self._read_repository = read_repository

    async def _update_child_category_parent_id(self, child_category_id: UUID, event: CategoryParentChangedEvent) -> None:
        logger.info(f"Handling CategoryParentChangedEvent for category {child_category_id}")

        child_category = await self._read_repository.get_category(category_id=child_category_id)
        if not child_category:
            logger.warning(f"CategoryDetailsDTO not found for child category ID {child_category_id}. Aborting.")
            return
        child_category.parent_category_id = event.new_parent_category_id
        child_category.updated_at = event.updated_at 
        await self._read_repository.update_read_model(child_category)
        logger.info(f"Successfully updated parent_category_id for child category {child_category_id} to {event.new_parent_category_id}")

    async def _update_prev_parent_children_ids(self, child_category_id: UUID, event: CategoryParentChangedEvent) -> None:
        prev_parent = await self._read_repository.get_category(category_id=event.prev_parent_category_id)
        if prev_parent:
            if child_category_id in prev_parent.children_ids:
                prev_parent.children_ids.remove(child_category_id)
                prev_parent.updated_at = event.updated_at
                await self._read_repository.update_read_model(prev_parent)
                logger.info(f"Removed child {child_category_id} from previous parent {event.prev_parent_category_id}'s children_ids.")
            else:
                logger.warning(f"Child {child_category_id} not found in previous parent {event.prev_parent_category_id}'s children_ids. No removal needed.")
        else:
            logger.warning(f"Previous parent DTO {event.prev_parent_category_id} not found. Cannot update its children_ids.")

    async def _update_new_parent_children_ids(self, child_category_id: UUID, event: CategoryParentChangedEvent) -> None:
        new_parent = await self._read_repository.get_category(category_id=event.new_parent_category_id)
        if new_parent:
            if child_category_id not in new_parent.children_ids:
                new_parent.children_ids.append(child_category_id)
                new_parent.updated_at = event.updated_at
                await self._read_repository.update_read_model(new_parent)
                logger.info(f"Added child {child_category_id} to new parent {event.new_parent_category_id}'s children_ids.")
            else:
                logger.info(f"Child {child_category_id} already present in new parent {event.new_parent_category_id}'s children_ids. No addition needed.")
        else:
            logger.warning(f"New parent DTO {event.new_parent_category_id} not found. Cannot update its children_ids.")

    async def handle(self, event: CategoryParentChangedEvent) -> None:
        child_category_id = UUID(event.aggregate_id)

        await self._update_child_category_parent_id(child_category_id, event)

        if event.prev_parent_category_id:
            await self._update_prev_parent_children_ids(child_category_id, event)

        if event.new_parent_category_id:
            await self._update_new_parent_children_ids(child_category_id, event)
        
        logger.info(f"Finished handling CategoryParentChangedEvent for category {child_category_id}")
