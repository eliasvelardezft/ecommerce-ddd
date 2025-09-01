import logging
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.products.dtos.ProductDetailsDTO import ProductDetailsDTO
from domain.products.repositories.IProductReadRepository import IProductReadRepository

logger = logging.getLogger(__name__)

# Define the MongoDB collection name
PRODUCT_DETAILS_COLLECTION = "product_details_view"

class ProductReadRepository(IProductReadRepository):
    """MongoDB implementation for reading ProductDetailsDTO."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._db = database
        self._collection = self._db[PRODUCT_DETAILS_COLLECTION]
        logger.info(f"Initialized ProductReadRepository with MongoDB, collection: {PRODUCT_DETAILS_COLLECTION}")

    async def get_product_details_by_id(self, product_id: str) -> Optional[ProductDetailsDTO]:
        logger.debug(f"[ReadRepo] Fetching product_details by ID: {product_id}")
        # MongoDB stores IDs as strings
        doc = await self._collection.find_one({"_id": product_id})
        if not doc:
            logger.warning(f"[ReadRepo] ProductDetailsDTO not found for ID: {product_id}")
            return None
        # Convert _id to id field and ensure it's a string
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
        return ProductDetailsDTO(**doc)

    async def list_all_products(self, category_id: Optional[str] = None) -> List[ProductDetailsDTO]:
        query_filter = {}
        if category_id:
            query_filter["category_id"] = category_id  # category_id is already a string
        logger.debug(f"[ReadRepo] Listing all product_details with filter: {query_filter}")
        
        cursor = self._collection.find(query_filter)
        products = []
        async for doc in cursor:
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            products.append(ProductDetailsDTO(**doc))
        return products

    async def list_active_products(self, category_id: Optional[str] = None) -> List[ProductDetailsDTO]:
        """List active products, optionally filtered by category."""
        query_filter = {"active": True}
        if category_id:
            query_filter["category_id"] = category_id
        logger.debug(f"[ReadRepo] Listing active product_details with filter: {query_filter}")
        
        cursor = self._collection.find(query_filter)
        products = []
        async for doc in cursor:
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            products.append(ProductDetailsDTO(**doc))
        return products

    async def update_read_model(self, product_dto: ProductDetailsDTO) -> None:
        logger.debug(f"[ReadRepo] Updating read model for product ID: {product_dto.id}")
        # Prepare document for MongoDB with proper JSON serialization (converts Decimal to float)
        update_data = product_dto.model_dump(mode='json')  # This converts Decimal to float for MongoDB

        await self._collection.update_one(
            {"_id": product_dto.id},  # Use string ID directly
            {"$set": update_data},
            upsert=True
        )
        logger.info(f"[ReadRepo] Successfully updated/inserted read model for product ID: {product_dto.id}")