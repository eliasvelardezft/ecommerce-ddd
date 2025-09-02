from abc import ABC, abstractmethod

from domain.core.value_objects.EntityId import EntityId
from domain.customers.Customer import Customer


class ICustomerWriteRepository(ABC):
    @abstractmethod
    async def save(self, customer: Customer) -> Customer:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, customer: Customer) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: EntityId) -> Customer | None:
        raise NotImplementedError
