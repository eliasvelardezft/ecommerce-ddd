import logging
from typing import Optional

from domain.products.dtos.ProductDetailsDTO import ProductDetailsDTO
from domain.products.repositories.IProductReadRepository import IProductReadRepository
from .GetProductByIdQuery import GetProductByIdQuery

logger = logging.getLogger(__name__)

class GetProductByIdHandler:
    def __init__(self, product_read_repository: IProductReadRepository):
        self._product_read_repository = product_read_repository

    async def handle(self, query: GetProductByIdQuery) -> Optional[ProductDetailsDTO]:
        logger.info(f"Handling GetProductByIdQuery for Product ID: {query.product_id}")
        
        product = await self._product_read_repository.get_product_details_by_id(query.product_id)
        
        if not product:
            logger.warning(f"ProductDetailsDTO not found for ID: {query.product_id}")
            return None
            
        logger.info(f"Successfully retrieved ProductDetailsDTO for ID: {query.product_id}")
        return product 