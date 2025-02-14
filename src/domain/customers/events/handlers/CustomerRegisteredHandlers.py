from datetime import datetime
import logging
from typing import Union

from src.domain.core.events.handlers.DomainEventHandler import DomainEventHandler
from src.domain.customers.events.CustomerRegisteredEvent import CustomerRegisteredEvent
from src.domain.orders.events.OrderPlacedEvent import OrderPlacedEvent
from src.infrastructure.customers.services.EmailService import EmailService
from src.infrastructure.customers.services.AuditService import AuditService
from src.domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO
from src.domain.customers.repositories.ICustomerReadRepository import ICustomerReadRepository

logger = logging.getLogger(__name__)

class UpdateReadModelHandler:
    def __init__(self, read_repository: ICustomerReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: Union[CustomerRegisteredEvent, OrderPlacedEvent]) -> None:
        if isinstance(event, CustomerRegisteredEvent):
            # Handle new customer registration
            customer_profile = CustomerProfileDTO(
                id=event.aggregate_id,
                name=event.name,
                email=event.email,
                created_at=datetime.now(),
                total_orders=0
            )
        elif isinstance(event, OrderPlacedEvent):
            # Handle order placed
            profile = await self._read_repository.get_customer_profile_by_id(id=event.customer_id)
            if not profile:
                logger.error(f"Customer profile not found for ID: {event.customer_id}")
                return
                
            profile.total_orders += 1
            customer_profile = profile

        await self._read_repository.update_read_model(customer_profile)

class SendWelcomeEmailHandler(DomainEventHandler[CustomerRegisteredEvent]):
    def __init__(self, email_service: EmailService):
        self._email_service = email_service

    async def handle(self, event: CustomerRegisteredEvent) -> None:
        logger.info("[Event] Sending welcome email to: %s", event.email)
        await self._email_service.send_welcome_email(
            email=event.email,
            name=event.name
        )
        logger.info(f"Welcome email sent to: {event.email}")

class AuditNewCustomerHandler(DomainEventHandler[CustomerRegisteredEvent]):
    def __init__(self, audit_service: AuditService):
        self._audit_service = audit_service

    async def handle(self, event: CustomerRegisteredEvent) -> None:
        logger.info("[Event] Auditing registration for: %s", event.email)
        await self._audit_service.log_event(
            "New customer registered",
            {"customer_id": event.aggregate_id, "email": event.email}
        )
        logger.info(f"Customer registration audited: {event.email}")
