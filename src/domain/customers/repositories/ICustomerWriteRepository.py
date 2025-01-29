from abc import ABC
from uuid import UUID

from src.domain.customers.Customer import Customer


class ICustomerWriteRepository(ABC):
    async def save(self, customer: Customer) -> Customer:
        raise NotImplementedError

    async def delete(self, customer: Customer) -> None:
        raise NotImplementedError

    async def get_by_id(self, id: UUID) -> Customer:
        raise NotImplementedError
