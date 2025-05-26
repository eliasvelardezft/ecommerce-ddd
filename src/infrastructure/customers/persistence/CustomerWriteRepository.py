from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.customers.Customer import Customer
from domain.customers.repositories.ICustomerWriteRepository import ICustomerWriteRepository
from .Customer import CustomerSQL
import logging

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
            id=customer.id,
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

    async def get_by_id(self, id: UUID) -> Optional[Customer]:
        """
        Note: This is mainly used by command handlers to load an aggregate
        before applying changes
        """
        result = await self._session.execute(
            select(CustomerSQL).where(CustomerSQL.id == id)
        )
        db_customer = result.scalar_one_or_none()
        if not db_customer:
            return None
            
        # Convert back to domain entity
        return Customer(
            id=db_customer.id,
            name=db_customer.name,
            email=db_customer.email,
            created_at=db_customer.created_at,
            updated_at=db_customer.updated_at
        )
