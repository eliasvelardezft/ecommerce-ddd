from typing import List
from uuid import UUID
from src.domain.customers.Customer import Customer
from src.domain.customers.repositories.ICustomerWriteRepository import ICustomerWriteRepository
import logging

logger = logging.getLogger(__name__)

class CustomerWriteRepository(ICustomerWriteRepository):
    """Repository for write operations (commands) on Customer aggregate"""
    
    def __init__(self):
        self._customers = []  # In-memory storage
        logger.info("Initialized CustomerWriteRepository")

    async def save(self, customer: Customer) -> Customer:
        # Check if customer already exists
        existing = next(
            (c for c in self._customers if c.id == customer.id), 
            None
        )
        
        if existing:
            logger.info("[Write] Updating customer: %s", customer.email)
            self._customers.remove(existing)
        else:
            logger.info("[Write] Creating new customer: %s", customer.email)
            
        self._customers.append(customer)
        return customer

    async def delete(self, customer: Customer) -> None:
        self._customers.remove(customer)

    async def get_by_id(self, id: UUID) -> Customer:
        """
        Note: This is mainly used by command handlers to load an aggregate
        before applying changes
        """
        return next(
            (c for c in self._customers if c.id == id), 
            None
        )
