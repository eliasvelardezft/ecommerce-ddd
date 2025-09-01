"""Customer-specific dependencies"""
from fastapi import Depends

from api.dependencies import get_db_session, get_mongo_db, get_domain_event_dispatcher
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from infrastructure.customers.persistence.CustomerWriteRepository import CustomerWriteRepository
from infrastructure.customers.persistence.CustomerReadRepository import CustomerReadRepository
from infrastructure.customers.services.EmailService import EmailService
from infrastructure.customers.services.AuditService import AuditService

def get_customer_write_repository(session = Depends(get_db_session)):
    return CustomerWriteRepository(session)

def get_customer_read_repository(db = Depends(get_mongo_db)):
    return CustomerReadRepository(db)

def get_email_service():
    return EmailService()

def get_audit_service():
    return AuditService()
