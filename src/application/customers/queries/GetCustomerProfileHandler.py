from typing import Optional

from domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO
from infrastructure.customers.persistence.CustomerReadRepository import (
    CustomerReadRepository,
)

from .GetCustomerProfileQuery import GetCustomerProfileQuery


class GetCustomerProfileHandler:
    def __init__(self, read_repository: CustomerReadRepository):
        self._repository = read_repository

    async def handle(self, query: GetCustomerProfileQuery) -> Optional[CustomerProfileDTO]:
        return await self._repository.get_customer_profile_by_email(query.email)
