from abc import ABC, abstractmethod
from typing import List, Optional

from domain.products.dtos.ProductDetailsDTO import ProductDetailsDTO


class IProductReadRepository(ABC):
    @abstractmethod
    async def get_product_details_by_id(self, product_id: str) -> Optional[ProductDetailsDTO]:
        """Retrieves product details by its ID. Returns None if not found."""
        raise NotImplementedError

    @abstractmethod
    async def list_all_products(self, category_id: Optional[str] = None) -> List[ProductDetailsDTO]:
        """Lists all products, regardless of status."""
        raise NotImplementedError

    @abstractmethod
    async def list_active_products(self, category_id: Optional[str] = None) -> List[ProductDetailsDTO]:
        """Lists all active products."""
        raise NotImplementedError

    @abstractmethod
    async def update_read_model(self, product_dto: ProductDetailsDTO) -> None:
        """Creates or updates the product read model. Used by event handlers."""
        raise NotImplementedError
