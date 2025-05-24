"""Customer-specific dependencies"""
from fastapi import Depends

from api.dependencies import get_db_session, get_mongo_db, get_event_dispatcher
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from infrastructure.customers.persistence.CustomerWriteRepository import CustomerWriteRepository
from infrastructure.customers.persistence.CustomerReadRepository import CustomerReadRepository
from infrastructure.customers.services.EmailService import EmailService
from infrastructure.customers.services.AuditService import AuditService

# Create singleton instances
# TODO: THIS IS ONLY BECAUSE THE SERVICES ARE IN-MEMORY FOR TESTING PURPOSES
# TODO: IN A REAL APP, WE WOULDNT MAKE THEM SINGLETONS
_email_service = EmailService()
_audit_service = AuditService()


def get_customer_write_repository(session = Depends(get_db_session)):
    return CustomerWriteRepository(session)

def get_customer_read_repository(db = Depends(get_mongo_db)):
    return CustomerReadRepository(db)

def get_email_service():
    return _email_service

def get_audit_service():
    return _audit_service

def get_customer_event_dispatcher(
    dispatcher: DomainEventDispatcher = Depends(get_event_dispatcher),
) -> DomainEventDispatcher:
    """Returns the configured event dispatcher from app state"""
    return dispatcher
