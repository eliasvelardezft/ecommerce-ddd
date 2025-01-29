from datetime import datetime
import logging

from src.domain.core.events.handlers.DomainEventHandler import DomainEventHandler
from src.domain.customers.events.CustomerRegisteredEvent import CustomerRegisteredEvent
from src.infrastructure.customers.services.EmailService import EmailService
from src.infrastructure.customers.services.AuditService import AuditService
from src.infrastructure.customers.persistence.CustomerReadRepository import CustomerReadRepository
from src.domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO

logger = logging.getLogger(__name__)

class UpdateReadModelHandler(DomainEventHandler[CustomerRegisteredEvent]):
    """Updates the read model when a customer is registered"""
    
    def __init__(self, read_repository: CustomerReadRepository):
        self._read_repository = read_repository

    async def handle(self, event: CustomerRegisteredEvent) -> None:
        logger.info("[Event] Updating read model for customer: %s", event.email)
        customer_profile = CustomerProfileDTO(
            id=event.aggregate_id,
            name=event.name,
            email=event.email,
            created_at=datetime.now(),
            total_orders=0,
            last_order_date=None,
            favorite_products=[],
            loyalty_tier="NEW"
        )
        await self._read_repository.update_read_model(customer_profile)
        logger.info(f"Read model updated for customer: {event.email}")

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
