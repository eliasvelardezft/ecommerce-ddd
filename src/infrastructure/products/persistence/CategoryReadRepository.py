import logging
from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.products.dtos.CategoryDetailsDTO import CategoryDetailsDTO
from domain.products.repositories.ICategoryReadRepository import ICategoryReadRepository

logger = logging.getLogger(__name__)


class CategoryReadRepository(ICategoryReadRepository):
    """MongoDB implementation for reading CategoryDetailsDTO."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._db = database
        self._collection = self._db.category_details_view
        logger.info(f"Initialized CategoryReadRepository with MongoDB, collection: {self._collection}")

    async def _doc_to_dto(self, doc: dict) -> Optional[CategoryDetailsDTO]:
        if not doc:
            return None
        # Ensure _id (or id) from Mongo is converted to UUID for the DTO
        if isinstance(doc.get("_id"), str):
            doc["id"] = UUID(doc["_id"])
        elif isinstance(doc.get("id"), str):
            doc["id"] = UUID(doc["id"])
        
        # Recursively convert children if they exist
        if "children" in doc and isinstance(doc["children"], list):
            children_dtos = []
            for child_doc in doc["children"]:
                child_dto = await self._doc_to_dto(child_doc) # Recursive call
                if child_dto:
                    children_dtos.append(child_dto)
            doc["children"] = children_dtos
        elif "children" not in doc: # Ensure children list exists even if empty
            doc["children"] = []

        if "children_ids" not in doc: # Ensure children_ids list exists even if empty
            doc["children_ids"] = []
        else: # Ensure children_ids are UUIDs
            doc["children_ids"] = [UUID(cid) for cid in doc["children_ids"] if isinstance(cid, str)]
        
        if "parent_category_id" in doc and isinstance(doc["parent_category_id"], str):
            doc["parent_category_id"] = UUID(doc["parent_category_id"])
        
        return CategoryDetailsDTO(**doc)

    async def get_category(self, category_id: UUID, recursive: bool = False) -> Optional[CategoryDetailsDTO]:
        logger.debug(f"[ReadRepo] Fetching category_details by ID: {category_id}, Recursive: {recursive}")
        doc = await self._collection.find_one({"_id": str(category_id)})
        if not doc:
            logger.warning(f"[ReadRepo] CategoryDetailsDTO not found for ID: {category_id}")
            return None

        # If not recursive, we might want to clear children that might have been stored from a previous recursive fetch
        # However, the DTO itself has children. If Mongo stores the full tree, `recursive` flag might be about
        # how deep the _doc_to_dto conversion goes, or a projection in find_one.
        # For now, _doc_to_dto will hydrate based on what's in the doc. 
        # A more sophisticated recursive fetch would build the tree if not stored as such.
        # If `recursive=False` implies only direct children or specific depth, the query/projection would change.
        # Assuming for now that if recursive=False, the stored doc might only have direct children or children_ids.
        # The current _doc_to_dto will try to build children if they are in the doc.

        # If the stored document itself is recursive, and `recursive=False` means shallow, this logic needs adjustment.
        # For this iteration, we assume `get_category` fetches what it needs and `_doc_to_dto` hydrates it.
        # The `recursive` flag here is more of a hint to the caller or a future optimization point for the query itself.
        return await self._doc_to_dto(doc)

    async def list_categories(self) -> List[CategoryDetailsDTO]:
        logger.debug("[ReadRepo] Listing all category_details")
        cursor = self._collection.find()
        categories = []
        async for doc in cursor:
            dto = await self._doc_to_dto(doc)
            if dto:
                categories.append(dto)
        return categories

    async def list_children(self, parent_category_id: UUID) -> List[CategoryDetailsDTO]:
        logger.debug(f"[ReadRepo] Listing children for parent ID: {parent_category_id}")
        # This assumes children are stored nested or queried by parent_category_id field
        cursor = self._collection.find({"parent_category_id": str(parent_category_id)})
        categories = []
        async for doc in cursor:
            dto = await self._doc_to_dto(doc)
            if dto:
                categories.append(dto)
        return categories

    async def list_top_level(self) -> List[CategoryDetailsDTO]:
        logger.debug("[ReadRepo] Listing top-level category_details")
        cursor = self._collection.find({"parent_category_id": None})
        categories = []
        async for doc in cursor:
            dto = await self._doc_to_dto(doc)
            if dto:
                categories.append(dto)
        return categories

    async def update_read_model(self, category_dto: CategoryDetailsDTO) -> None:
        logger.debug(f"[ReadRepo] Updating read model for category ID: {category_dto.id}")
        
        # Prepare document for MongoDB
        # For CategoryDetailsDTO, children is List[CategoryDetailsDTO]. 
        # model_dump will recursively dump them.
        category_doc_for_set = category_dto.model_dump()

        # Convert main ID and parent_category_id to string for $set if they are UUIDs in the DTO
        if "id" in category_doc_for_set and isinstance(category_doc_for_set["id"], UUID):
            category_doc_for_set["id"] = str(category_doc_for_set["id"])
        if "parent_category_id" in category_doc_for_set and category_doc_for_set["parent_category_id"] is not None and isinstance(category_doc_for_set["parent_category_id"], UUID):
            category_doc_for_set["parent_category_id"] = str(category_doc_for_set["parent_category_id"])
        
        # children_ids are List[UUID], convert them to List[str]
        if "children_ids" in category_doc_for_set and isinstance(category_doc_for_set["children_ids"], list):
            category_doc_for_set["children_ids"] = [str(cid) for cid in category_doc_for_set["children_ids"]]

        # For the 'children' field (List[CategoryDetailsDTO]), model_dump should handle nested serialization.
        # We need to ensure UUIDs within those nested DTOs are also stringified if that's the storage convention.
        # Pydantic's model_dump(mode='json') usually handles UUID to str for JSON-like structures.
        # If direct dict is used, manual conversion might be needed for nested UUIDs.
        # Let's assume model_dump is sufficient for nested structures for now.

        await self._collection.update_one(
            {"_id": str(category_dto.id)}, # Query by string representation of UUID for _id
            {"$set": category_doc_for_set},
            upsert=True
        )
        logger.info(f"[ReadRepo] Successfully updated/inserted read model for category ID: {category_dto.id}")
