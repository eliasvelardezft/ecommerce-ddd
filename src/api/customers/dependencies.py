"""Customer-specific dependencies"""

from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import (
    get_db_session,
    get_mongo_db,
)
from infrastructure.customers.persistence.CustomerReadRepository import (
    CustomerReadRepository,
)
from infrastructure.customers.persistence.CustomerWriteRepository import (
    CustomerWriteRepository,
)
from infrastructure.customers.services.AuditService import AuditService
from infrastructure.customers.services.EmailService import EmailService


def get_customer_write_repository(session: Annotated[AsyncSession, Depends(get_db_session)]):
    return CustomerWriteRepository(session)


def get_customer_read_repository(db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)]):
    return CustomerReadRepository(db)


def get_email_service():
    return EmailService()


def get_audit_service():
    return AuditService()
