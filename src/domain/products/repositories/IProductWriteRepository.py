from abc import ABC, abstractmethod
from typing import Optional

from domain.core.value_objects.EntityId import EntityId
from domain.products.models.Product import Product


class IProductWriteRepository(ABC):
    @abstractmethod
    async def save(self, product: Product) -> None:
        """Persists a product, creating it if new or updating if existing."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: EntityId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, product_id: EntityId) -> Product | None:
        """Retrieves a product by its ID, potentially for updates or checks."""
        raise NotImplementedError
