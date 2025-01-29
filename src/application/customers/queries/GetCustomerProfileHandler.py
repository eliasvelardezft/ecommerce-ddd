from typing import Optional
from .GetCustomerProfileQuery import GetCustomerProfileQuery
from src.domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO
from src.infrastructure.customers.persistence.CustomerReadRepository import CustomerReadRepository


class GetCustomerProfileHandler:
    def __init__(self, read_repository: CustomerReadRepository):
        self._repository = read_repository

    async def handle(self, query: GetCustomerProfileQuery) -> Optional[CustomerProfileDTO]:
        return await self._repository.get_customer_profile(query.email)
