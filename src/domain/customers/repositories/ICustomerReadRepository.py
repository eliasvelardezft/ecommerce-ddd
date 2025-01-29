from abc import ABC
from typing import List
from src.domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO


class ICustomerReadRepository(ABC):
    async def get_customer_profile(self, email: str) -> CustomerProfileDTO:
        raise NotImplementedError

    async def get_all_customer_profiles(self) -> List[CustomerProfileDTO]:
        raise NotImplementedError

    async def update_read_model(self, customer_profile: CustomerProfileDTO) -> None:
        raise NotImplementedError
