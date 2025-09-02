from abc import ABC, abstractmethod

from domain.core.value_objects.EntityId import EntityId
from domain.orders.models.Order import Order


class IOrderWriteRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, order: Order) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: EntityId) -> Order | None:
        raise NotImplementedError
