from abc import ABC
from typing import Optional

from domain.core.value_objects.EntityId import EntityId
from domain.customers.Customer import Customer


class ICustomerWriteRepository(ABC):
    async def save(self, customer: Customer) -> Customer:
        raise NotImplementedError

    async def delete(self, customer: Customer) -> None:
        raise NotImplementedError

    async def get_by_id(self, id: EntityId) -> Customer | None:
        raise NotImplementedError
