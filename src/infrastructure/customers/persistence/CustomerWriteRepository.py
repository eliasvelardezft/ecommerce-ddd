import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.core.value_objects.EntityId import EntityId
from domain.customers.Customer import Customer
from domain.customers.repositories.ICustomerWriteRepository import (
    ICustomerWriteRepository,
)

from .Customer import CustomerSQL

logger = logging.getLogger(__name__)

class CustomerWriteRepository(ICustomerWriteRepository):
    """Repository for write operations (commands) on Customer aggregate"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
        logger.info("Initialized CustomerWriteRepository")

    async def save(self, customer: Customer) -> Customer:
        logger.info("[Write] Creating new customer: %s", customer.email)
        
        # Convert domain entity to database model
        db_customer = CustomerSQL(
            id=str(customer.id),  # Clean conversion to string for database storage
            name=customer.name,
            email=customer.email,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        )
        
        self._session.add(db_customer)
        await self._session.commit()
        return customer

    async def delete(self, customer: Customer) -> None:
        self._session.delete(customer)
        await self._session.commit()

    async def get_by_id(self, id: EntityId) -> Optional[Customer]:
        """
        Note: This is mainly used by command handlers to load an aggregate
        before applying changes
        """
        result = await self._session.execute(
            select(CustomerSQL).where(CustomerSQL.id == str(id))  # Clean conversion to string
        )
        db_customer = result.scalar_one_or_none()
        if not db_customer:
            return None
            
        # Convert back to domain entity
        return Customer(
            _id=EntityId.from_string(db_customer.id),  # Clean conversion back to EntityId
            name=db_customer.name,
            email=db_customer.email,
            created_at=db_customer.created_at,
            updated_at=db_customer.updated_at
        )
