from abc import ABC
from uuid import UUID

from domain.products.models.Product import Product


class IProductWriteRepository(ABC):
    async def save(self, product: Product) -> Product:
        raise NotImplementedError

    async def delete(self, product: Product) -> None:
        raise NotImplementedError

    async def get_by_id(self, id: UUID) -> Product:
        raise NotImplementedError
