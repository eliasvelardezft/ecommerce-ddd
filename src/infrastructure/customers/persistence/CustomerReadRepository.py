from typing import List, Optional
from src.domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO
from src.domain.customers.repositories.ICustomerReadRepository import ICustomerReadRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class CustomerReadRepository(ICustomerReadRepository):
    """Repository for read operations (queries) on Customer data"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._db = database
        self._collection = database.customer_profiles
        logger.info("Initialized CustomerReadRepository")

    async def get_customer_profile(self, email: str) -> Optional[CustomerProfileDTO]:
        """Get customer profile by email"""
        logger.info("[Read] Fetching profile for: %s", email)
        doc = await self._collection.find_one({"email": email})
        if not doc:
            logger.info("[Read] Profile not found for: %s", email)
            return None
            
        logger.info(f"Customer profile found for email: {email}")
        return CustomerProfileDTO(**doc)

    async def get_all_profiles(self) -> List[CustomerProfileDTO]:
        """Get all customer profiles"""
        cursor = self._collection.find()
        return [CustomerProfileDTO(**doc) async for doc in cursor]

    async def update_read_model(self, customer: CustomerProfileDTO) -> None:
        """
        Update the read model when changes occur
        This would be called by event handlers
        """
        logger.info("[Read] Current views before update: %s", 
                   [doc["email"] async for doc in self._collection.find()])
        
        await self._collection.update_one(
            {"_id": customer.id},
            {"$set": customer.model_dump()},
            upsert=True
        )
        
        logger.info("[Read] Current views after update: %s", 
                   [doc["email"] async for doc in self._collection.find()])
