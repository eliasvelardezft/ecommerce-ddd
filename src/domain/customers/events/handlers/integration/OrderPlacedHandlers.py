import logging

from domain.core.events.handlers import DomainEventHandler
from domain.customers.repositories.ICustomerReadRepository import ICustomerReadRepository


logger = logging.getLogger(__name__)


class UpdateReadModelOnOrderPlacedEvent(DomainEventHandler["OrderPlacedEvent"]):
    def __init__(self, read_repository: ICustomerReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: "OrderPlacedEvent") -> None:
        # Handle order placed
        profile = await self._read_repository.get_customer_profile_by_id(
            id=event.get("customer_id")
        )
        if not profile:
            logger.error(f"Customer profile not found for ID: {event.get("customer_id")}")
            return

        profile.total_orders += 1
        customer_profile = profile

        await self._read_repository.update_read_model(customer_profile)
