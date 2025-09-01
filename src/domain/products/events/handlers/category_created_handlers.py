import logging

from domain.products.dtos.CategoryDetailsDTO import CategoryDetailsDTO
from domain.products.events.CategoryCreatedEvent import CategoryCreatedEvent
from domain.products.repositories.ICategoryReadRepository import (
    ICategoryReadRepository,
)

logger = logging.getLogger(__name__)

class UpdateCategoryOnCategoryCreated:
    def __init__(self, read_repository: ICategoryReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: CategoryCreatedEvent) -> None:
        logger.info(f"Creating category read model on CategoryCreatedEvent: {event.aggregate_id}")

        category_dto = CategoryDetailsDTO(
            id=str(event.aggregate_id),  # Convert EntityId to string
            name=event.name,
            description=event.description,
            parent_category_id=str(event.parent_category_id) if event.parent_category_id else None,
            children_ids=[],
            children=[],
            created_at=event.created_at,
            updated_at=event.created_at
        )

        await self._read_repository.update_read_model(category_dto)
        logger.info(f"Successfully created/updated read model for category {event.aggregate_id}")
