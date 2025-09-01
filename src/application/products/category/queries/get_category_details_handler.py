import logging
from typing import Optional

from domain.products.dtos.CategoryDetailsDTO import CategoryDetailsDTO
from domain.products.repositories.ICategoryReadRepository import (
    ICategoryReadRepository,
)

from .GetCategoryDetailsQuery import GetCategoryDetailsQuery

logger = logging.getLogger(__name__)

class GetCategoryDetailsHandler:
    def __init__(self, category_read_repository: ICategoryReadRepository):
        self._category_read_repository = category_read_repository

    async def handle(self, query: GetCategoryDetailsQuery) -> Optional[CategoryDetailsDTO]:
        logger.info(f"Handling GetCategoryDetailsQuery for Category ID: {query.category_id}, Recursive: {query.recursive_children}")

        category = await self._category_read_repository.get_category(
            category_id=query.category_id,
            recursive=query.recursive_children
        )

        if not category:
            logger.warning(f"CategoryDetailsDTO not found for ID: {query.category_id}")
            return None

        logger.info(f"Successfully retrieved CategoryDetailsDTO for ID: {query.category_id}")
        return category
