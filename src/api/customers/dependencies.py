"""Customer-specific dependencies"""
from fastapi import Depends
from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from src.domain.customers.events.CustomerRegisteredEvent import CustomerRegisteredEvent
from src.domain.customers.events.handlers.CustomerRegisteredHandlers import (
    UpdateReadModelHandler,
    SendWelcomeEmailHandler,
    AuditNewCustomerHandler
)
from src.infrastructure.customers.persistence.CustomerWriteRepository import CustomerWriteRepository
from src.infrastructure.customers.persistence.CustomerReadRepository import CustomerReadRepository
from src.infrastructure.customers.services.EmailService import EmailService
from src.infrastructure.customers.services.AuditService import AuditService
from src.api.dependencies import get_base_event_dispatcher

# Create singleton instances
# TODO: THIS IS ONLY BECAUSE THE REPOSITORIES ARE IN-MEMORY FOR TESTING PURPOSES
# TODO: IN A REAL APP, WE WOULDNT MAKE THEM SINGLETONS
_write_repository = CustomerWriteRepository()
_read_repository = CustomerReadRepository()
_email_service = EmailService()
_audit_service = AuditService()

def get_customer_write_repository():
    return _write_repository

def get_customer_read_repository():
    return _read_repository

def get_email_service():
    return _email_service

def get_audit_service():
    return _audit_service

def get_customer_event_dispatcher(
    dispatcher: DomainEventDispatcher = Depends(get_base_event_dispatcher),
    read_repository: CustomerReadRepository = Depends(get_customer_read_repository),
    email_service: EmailService = Depends(get_email_service),
    audit_service: AuditService = Depends(get_audit_service)
) -> DomainEventDispatcher:
    """Extends base dispatcher with customer-specific event handlers"""
    
    # Register customer-specific handlers
    dispatcher.register_handler(
        CustomerRegisteredEvent,
        UpdateReadModelHandler(read_repository)
    )
    dispatcher.register_handler(
        CustomerRegisteredEvent,
        SendWelcomeEmailHandler(email_service)
    )
    dispatcher.register_handler(
        CustomerRegisteredEvent,
        AuditNewCustomerHandler(audit_service)
    )
    
    return dispatcher
