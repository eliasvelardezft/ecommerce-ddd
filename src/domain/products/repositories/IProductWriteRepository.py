from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from domain.products.models.Product import Product


class IProductWriteRepository(ABC):
    @abstractmethod
    async def save(self, product: Product) -> None:
        """Persists a product, creating it if new or updating if existing."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Retrieves a product by its ID, potentially for updates or checks."""
        raise NotImplementedError
