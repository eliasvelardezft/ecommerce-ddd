from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.products.dtos.ProductDetailsDTO import ProductDetailsDTO


class IProductReadRepository(ABC):
    @abstractmethod
    async def get_product_details(self, id: UUID) -> ProductDetailsDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_all_product(self) -> List[ProductDetailsDTO]:
        raise NotImplementedError

    @abstractmethod
    async def update_read_model(self, product: ProductDetailsDTO) -> None:
        raise NotImplementedError
