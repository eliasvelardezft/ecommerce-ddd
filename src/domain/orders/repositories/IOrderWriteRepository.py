from abc import ABC
from typing import Optional

from domain.core.value_objects.EntityId import EntityId
from domain.orders.models.Order import Order


class IOrderWriteRepository(ABC):
    async def save(self, order: Order) -> Order:
        raise NotImplementedError

    async def delete(self, order: Order) -> None:
        raise NotImplementedError

    async def get_by_id(self, id: EntityId) -> Order | None:
        raise NotImplementedError
