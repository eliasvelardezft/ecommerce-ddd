import logging
from typing import List, Optional
from uuid import UUID

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

    async def get_product_details_by_id(self, product_id: UUID) -> Optional[ProductDetailsDTO]:
        logger.debug(f"[ReadRepo] Fetching product_details by ID: {product_id}")
        # MongoDB typically stores UUIDs as strings or BinData. Assuming string representation for _id.
        doc = await self._collection.find_one({"_id": str(product_id)})
        if not doc:
            logger.warning(f"[ReadRepo] ProductDetailsDTO not found for ID: {product_id}")
            return None
        # The DTO might store id as UUID, ensure conversion if Mongo doc stores it as str
        if isinstance(doc.get("_id"), str):
            doc["id"] = UUID(doc["_id"])
        elif isinstance(doc.get("id"), str): # if the field got named 'id' not '_id' in mongo
             doc["id"] = UUID(doc["id"]) 
        return ProductDetailsDTO(**doc)

    async def list_all_products(self, category_id: Optional[UUID] = None) -> List[ProductDetailsDTO]:
        query_filter = {}
        if category_id:
            query_filter["category_id"] = str(category_id) # Assuming category_id is stored as string in DTO/Mongo
        logger.debug(f"[ReadRepo] Listing all product_details with filter: {query_filter}")
        
        cursor = self._collection.find(query_filter)
        products = []
        async for doc in cursor:
            if isinstance(doc.get("_id"), str):
                doc["id"] = UUID(doc["_id"])
            elif isinstance(doc.get("id"), str):
                doc["id"] = UUID(doc["id"])
            products.append(ProductDetailsDTO(**doc))
        return products

    async def list_active_products(self, category_id: Optional[UUID] = None) -> List[ProductDetailsDTO]:
        query_filter = {"active": True} # DTO field is 'active', not 'is_active'
        if category_id:
            query_filter["category_id"] = str(category_id)
        logger.debug(f"[ReadRepo] Listing active product_details with filter: {query_filter}")

        cursor = self._collection.find(query_filter)
        products = []
        async for doc in cursor:
            if isinstance(doc.get("_id"), str):
                doc["id"] = UUID(doc["_id"])
            elif isinstance(doc.get("id"), str):
                doc["id"] = UUID(doc["id"])
            products.append(ProductDetailsDTO(**doc))
        return products

    async def update_read_model(self, product_dto: ProductDetailsDTO) -> None:
        logger.debug(f"[ReadRepo] Updating read model for product ID: {product_dto.id}")
        # Prepare document for MongoDB, ensuring UUIDs are stored as strings if that's the convention
        product_doc = product_dto.model_dump(mode='json') # use .model_dump() for Pydantic v2
        
        # Convert UUIDs to strings for MongoDB storage if necessary.
        # ProductDetailsDTO fields like id, category_id are UUIDs.
        # The DTO structure defines how these are serialized; model_dump(mode='json') often handles this.
        # However, explicit conversion for _id might be good.
        if "id" in product_doc and isinstance(product_doc["id"], UUID):
             product_doc["id"] = str(product_doc["id"]) # for the query part
        
        update_data = product_dto.model_dump() # Get dict for $set
        if "id" in update_data and isinstance(update_data["id"], UUID):
            update_data["id"] = str(update_data["id"]) # if 'id' field is also UUID

        await self._collection.update_one(
            {"_id": str(product_dto.id)}, # Query by string representation of UUID for _id
            {"$set": update_data},
            upsert=True
        )
        logger.info(f"[ReadRepo] Successfully updated/inserted read model for product ID: {product_dto.id}") 