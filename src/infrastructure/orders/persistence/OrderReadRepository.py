import logging
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO
from domain.orders.repositories.IOrderReadRepository import (
    IOrderReadRepository,
)

logger = logging.getLogger(__name__)


class OrderReadRepository(IOrderReadRepository):
    """Repository for read operations (queries) on Order data"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._db = database
        self._collection = database.order_details
        logger.info("Initialized OrderReadRepository")

    async def get_order_details(self, id: str) -> Optional[OrderDetailsDTO]:
        """Get order details by id"""
        logger.info("[Read] Fetching order details for: %s", id)
        doc = await self._collection.find_one({"_id": str(id)})
        if not doc:
            logger.error("[Read] Order Details not found for: %s", id)
            return None

        logger.info(f"Order details found for id: {id}")
        return OrderDetailsDTO(**doc)

    async def get_all_detailss(self) -> list[OrderDetailsDTO]:
        """Get all order detailss"""
        cursor = self._collection.find()
        return [OrderDetailsDTO(**doc) async for doc in cursor]

    async def update_read_model(self, order: OrderDetailsDTO) -> None:
        """
        Update the read model when changes occur
        This would be called by event handlers
        """
        logger.info("[Read] Current views before update: %s",
                   [doc["id"] async for doc in self._collection.find()])
        
        await self._collection.update_one(
            {"_id": str(order.id)},
            {"$set": order.model_dump()},
            upsert=True
        )
        
        logger.info("[Read] Current views after update: %s",
                   [doc["id"] async for doc in self._collection.find()])
