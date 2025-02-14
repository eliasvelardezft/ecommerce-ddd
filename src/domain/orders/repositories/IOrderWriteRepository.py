from abc import ABC
from uuid import UUID

from src.domain.orders.models.Order import Order


class IOrderWriteRepository(ABC):
    async def save(self, order: Order) -> Order:
        raise NotImplementedError

    async def delete(self, order: Order) -> None:
        raise NotImplementedError

    async def get_by_id(self, id: UUID) -> Order:
        raise NotImplementedError
