import logging
from typing import List

from domain.products.dtos.ProductDetailsDTO import ProductDetailsDTO
from domain.products.repositories.IProductReadRepository import (
    IProductReadRepository,
)

from .ListActiveProductsQuery import ListActiveProductsQuery

logger = logging.getLogger(__name__)

class ListActiveProductsHandler:
    def __init__(self, repository: IProductReadRepository):
        self._repository = repository

    async def handle(self, query: ListActiveProductsQuery) -> list[ProductDetailsDTO]:
        logger.info("Handling ListActiveProductsQuery")

        active_products = await self._repository.list_active_products(query.category_id)

        logger.info(f"Retrieved {len(active_products)} active products.")
        return active_products
