from abc import ABC
from typing import List
from uuid import UUID
from src.domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO


class ICustomerReadRepository(ABC):
    async def get_customer_profile_by_email(self, email: str) -> CustomerProfileDTO:
        raise NotImplementedError

    async def get_customer_profile_by_id(self, id: UUID) -> CustomerProfileDTO:
        raise NotImplementedError

    async def get_all_customer_profiles(self) -> List[CustomerProfileDTO]:
        raise NotImplementedError

    async def update_read_model(self, customer_profile: CustomerProfileDTO) -> None:
        raise NotImplementedError
