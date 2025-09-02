from abc import ABC, abstractmethod

from domain.core.value_objects.EntityId import EntityId
from domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO


class ICustomerReadRepository(ABC):
    @abstractmethod
    async def get_customer_profile_by_email(self, email: str) -> CustomerProfileDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def get_customer_profile_by_id(self, id: EntityId) -> CustomerProfileDTO | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all_customer_profiles(self) -> list[CustomerProfileDTO]:
        raise NotImplementedError

    @abstractmethod
    async def update_read_model(self, customer_profile: CustomerProfileDTO) -> None:
        raise NotImplementedError
