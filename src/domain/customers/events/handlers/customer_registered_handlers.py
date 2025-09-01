import logging
from datetime import datetime

from domain.core.events.handlers.DomainEventHandler import DomainEventHandler
from domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO
from domain.customers.events.CustomerRegisteredEvent import (
    CustomerRegisteredEvent,
)
from domain.customers.repositories.ICustomerReadRepository import (
    ICustomerReadRepository,
)
from infrastructure.customers.services.AuditService import AuditService
from infrastructure.customers.services.EmailService import EmailService

logger = logging.getLogger(__name__)


class UpdateReadModelOnCustomerRegisteredEvent(DomainEventHandler[CustomerRegisteredEvent]):
    def __init__(self, read_repository: ICustomerReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: CustomerRegisteredEvent) -> None:
        # Handle new customer registration
        customer_profile = CustomerProfileDTO(
            id=event.aggregate_id,
            name=event.name,
            email=event.email,
            created_at=datetime.now(),
            total_orders=0
        )

        await self._read_repository.update_read_model(customer_profile)


class SendWelcomeEmailOnCustomerRegisteredEvent(DomainEventHandler[CustomerRegisteredEvent]):
    def __init__(self, email_service: EmailService):
        self._email_service = email_service

    async def handle(self, event: CustomerRegisteredEvent) -> None:
        logger.info("[Event] Sending welcome email to: %s", event.email)
        await self._email_service.send_welcome_email(
            email=event.email,
            name=event.name
        )
        logger.info(f"Welcome email sent to: {event.email}")

class AuditNewCustomerOnCustomerRegisteredEvent(DomainEventHandler[CustomerRegisteredEvent]):
    def __init__(self, audit_service: AuditService):
        self._audit_service = audit_service

    async def handle(self, event: CustomerRegisteredEvent) -> None:
        logger.info("[Event] Auditing registration for: %s", event.email)
        await self._audit_service.log_event(
            "New customer registered",
            {"customer_id": event.aggregate_id, "email": event.email}
        )
        logger.info(f"Customer registration audited: {event.email}")
