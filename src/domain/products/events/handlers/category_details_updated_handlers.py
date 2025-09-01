import logging
from uuid import UUID

from domain.products.dtos.CategoryDetailsDTO import CategoryDetailsDTO
from domain.products.events.CategoryDetailsUpdatedEvent import (
    CategoryDetailsUpdatedEvent,
)
from domain.products.repositories.ICategoryReadRepository import (
    ICategoryReadRepository,
)

logger = logging.getLogger(__name__)

class UpdateCategoryOnCategoryDetailsUpdated:
    def __init__(self, read_repository: ICategoryReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: CategoryDetailsUpdatedEvent) -> None:
        logger.info(f"Updating category details on event: {event.aggregate_id}")
        category_dto = await self._read_repository.get_category(category_id=UUID(event.aggregate_id))
        
        if category_dto:
            if "name" in event.updated_details:
                category_dto.name = event.updated_details["name"]
            if "description" in event.updated_details:
                # This handles setting description to None if it's in updated_details with a None value
                category_dto.description = event.updated_details["description"]
            
            category_dto.updated_at = event.updated_at # Update timestamp from event
            await self._read_repository.update_read_model(category_dto)
            logger.info(f"Successfully updated details for category {event.aggregate_id}")
        else:
            logger.warning(f"CategoryDetailsDTO not found for category ID {event.aggregate_id} during details update.")
