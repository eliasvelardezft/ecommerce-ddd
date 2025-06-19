import logging
from typing import List

from domain.products.dtos.CategoryDetailsDTO import CategoryDetailsDTO
from domain.products.repositories.ICategoryReadRepository import ICategoryReadRepository
from .ListCategoriesQuery import ListCategoriesQuery

logger = logging.getLogger(__name__)

class ListCategoriesHandler:
    def __init__(self, category_read_repository: ICategoryReadRepository):
        self._category_read_repository = category_read_repository

    async def handle(self, query: ListCategoriesQuery) -> List[CategoryDetailsDTO]:
        if query.parent_category_id:
            logger.info(f"Handling ListCategoriesQuery for children of parent ID: {query.parent_category_id}")
            categories = await self._category_read_repository.list_children(query.parent_category_id)
            logger.info(f"Retrieved {len(categories)} children for parent ID: {query.parent_category_id}")
        else:
            logger.info("Handling ListCategoriesQuery for top-level categories")
            categories = await self._category_read_repository.list_top_level()
            logger.info(f"Retrieved {len(categories)} top-level categories.")
            
        return categories
