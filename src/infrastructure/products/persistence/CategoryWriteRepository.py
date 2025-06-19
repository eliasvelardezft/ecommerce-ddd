import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.products.models.Category import Category as DomainCategory
from domain.products.repositories.ICategoryWriteRepository import ICategoryWriteRepository
from .Category import CategorySQL

logger = logging.getLogger(__name__)

class EntityNotFoundError(Exception):
    """Custom exception for when an entity is not found for update."""
    def __init__(self, entity_id: UUID, entity_name: str = "Entity"):
        super().__init__(f"{entity_name} with ID {entity_id} not found for update.")

class CategoryWriteRepository(ICategoryWriteRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        logger.info("Initialized CategoryWriteRepository with SQLAlchemy session.")

    async def _create_new_sql(self, category: DomainCategory) -> CategorySQL:
        logger.debug(f"Category {category.id} not found in DB, preparing new SQL entry.")
        db_category_sql = CategorySQL(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_category_id=category.parent_category_id,
            created_at=category.created_at,
            updated_at=category.updated_at 
        )
        self._session.add(db_category_sql)
        return db_category_sql

    async def _update_existing_sql(self, existing_db_category: CategorySQL, category: DomainCategory) -> None:
        logger.debug(f"Category {category.id} found in DB, updating SQL fields.")
        existing_db_category.name = category.name
        existing_db_category.description = category.description
        existing_db_category.parent_category_id = category.parent_category_id
        # updated_at is handled by BaseModel event listener
        # No need to add to session, existing_db_category is already tracked.

    async def save(self, category: DomainCategory) -> None:
        logger.info(f"Saving category {category.id} (upsert) with name '{category.name}'.")
        
        existing_db_category = await self._session.get(CategorySQL, category.id)

        if existing_db_category:
            await self._update_existing_sql(existing_db_category, category)
        else:
            await self._create_new_sql(category) # Will add to session
        
        try:
            await self._session.commit()
            logger.info(f"Successfully saved (upserted) category {category.id}.")
        except Exception as e:
            logger.error(f"Error saving (upserting) category {category.id}: {e}")
            await self._session.rollback()
            raise

    async def get_by_id(self, category_id: UUID) -> Optional[DomainCategory]:
        logger.debug(f"Fetching category by ID {category_id} from the database.")
        
        result = await self._session.execute(
            select(CategorySQL).where(CategorySQL.id == category_id)
        )
        db_category: Optional[CategorySQL] = result.scalar_one_or_none()

        if not db_category:
            logger.debug(f"Category with ID {category_id} not found in the database.")
            return None
        
        logger.debug(f"Category {category_id} found, converting to domain model.")
        return DomainCategory(
            _id=db_category.id,
            name=db_category.name,
            description=db_category.description,
            parent_category_id=db_category.parent_category_id,
            created_at=db_category.created_at,
            updated_at=db_category.updated_at
        )
