import logging
from typing import Optional, List
from uuid import uuid4 # Import uuid4 for AttributeSQL IDs
from decimal import Decimal # For price conversion

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload # For eager loading

from domain.core.value_objects.EntityId import EntityId
from domain.products.models.Product import Product as DomainProduct
from domain.products.repositories.IProductWriteRepository import IProductWriteRepository
from domain.core.value_objects.Money import Money
from domain.products.value_objects.ImageUrl import ImageUrl as DomainImageUrl
from domain.products.value_objects.Attribute import Attribute as DomainAttribute

from .Product import ProductSQL, AttributeSQL


logger = logging.getLogger(__name__)


class ProductWriteRepository(IProductWriteRepository):
    """SQLAlchemy implementation of the Product Write Repository."""

    def __init__(self, session: AsyncSession):
        self._session = session
        logger.info("Initialized ProductWriteRepository with SQLAlchemy session.")

    async def _create_new_sql(self, product: DomainProduct) -> ProductSQL:
        logger.debug(f"Product {product.id} not found in DB, preparing new SQL entry.")
        db_attributes_sql = []
        for attr_domain in product.attributes:
            db_attributes_sql.append(
                AttributeSQL(
                    id=uuid4(), # New UUID for each AttributeSQL primary key
                    name=attr_domain.name,
                    value=attr_domain.value
                    # product_id is set by relationship when ProductSQL is created
                )
            )

        db_product_sql = ProductSQL(
            id=str(product.id),  # Convert EntityId to string
            name=product.name,
            description=product.description,
            sku=product.sku,
            active=product.active,
            stock_quantity=product.stock_quantity,
            price_amount=float(product.price.amount), # SQLAlchemy Numeric might prefer float or Decimal
            price_currency=product.price.currency,
            category_id=str(product.category_id),  # Convert EntityId to string
            image_url_url=str(product.image_url.url) if product.image_url else None,
            image_alt_text=product.image_url.alt_text if product.image_url else None,
            attributes=db_attributes_sql, # Assign list of new AttributeSQL instances
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        self._session.add(db_product_sql)
        return db_product_sql

    async def _update_existing_sql(self, existing_db_product: ProductSQL, product: DomainProduct) -> None:
        logger.debug(f"Product {product.id} found in DB, updating SQL fields.")
        existing_db_product.name = product.name
        existing_db_product.description = product.description
        existing_db_product.sku = product.sku
        existing_db_product.active = product.active
        existing_db_product.stock_quantity = product.stock_quantity
        existing_db_product.price_amount = float(product.price.amount) # Ensure type consistency
        existing_db_product.price_currency = product.price.currency
        existing_db_product.category_id = product.category_id
        
        if product.image_url:
            existing_db_product.image_url_url = str(product.image_url.url)
            existing_db_product.image_alt_text = product.image_url.alt_text
        else:
            existing_db_product.image_url_url = None
            existing_db_product.image_alt_text = None

        # Attribute handling: clear and re-add for simplicity with new UUIDs for AttributeSQL PKs
        # This leverages cascade="all, delete-orphan" on the ProductSQL.attributes relationship
        existing_db_product.attributes.clear()
        for attr_domain in product.attributes:
            existing_db_product.attributes.append(
                AttributeSQL(
                    id=uuid4(), # New UUID for each AttributeSQL PK, even on update of product attributes
                    name=attr_domain.name,
                    value=attr_domain.value
                    # product_id will be set by the back-reference/relationship
                )
            )
        # updated_at is handled by BaseModel event listener
        # No need to add existing_db_product to session, it's already tracked.

    async def save(self, product: DomainProduct) -> None:
        logger.info(f"Saving product {product.id} (upsert) with SKU '{product.sku}'.")

        # Eager load attributes when checking for existing product to avoid separate queries if updating attributes
        existing_db_product = await self._session.get(
            ProductSQL,
            str(product.id),
            options=[selectinload(ProductSQL.attributes)]
        )

        if existing_db_product:
            await self._update_existing_sql(existing_db_product, product)
        else:
            await self._create_new_sql(product) # Will add to session
        
        try:
            await self._session.commit()
            logger.info(f"Successfully saved (upserted) product {product.id}.")
        except Exception as e:
            logger.error(f"Error saving (upserting) product {product.id}: {e}")
            await self._session.rollback()
            raise
    
    async def delete(self, product_id: EntityId) -> None:
        logger.info(f"Attempting to delete product {product_id}.")
        db_product = await self._session.get(ProductSQL, str(product_id))
        if db_product:
            await self._session.delete(db_product)
            try:
                await self._session.commit()
                logger.info(f"Successfully deleted product {product_id}.")
            except Exception as e:
                logger.error(f"Error deleting product {product_id}: {e}")
                await self._session.rollback()
                raise
        else:
            logger.warning(f"Product {product_id} not found in database for deletion.")

    async def get_by_id(self, product_id: EntityId) -> Optional[DomainProduct]:
        logger.debug(f"Fetching product by ID {product_id} from the database.")
        
        result = await self._session.execute(
            select(ProductSQL)
            .options(
                selectinload(ProductSQL.attributes), # Eager load attributes
                selectinload(ProductSQL.category)    # Eager load category
            )
            .where(ProductSQL.id == str(product_id))
        )
        db_product: Optional[ProductSQL] = result.scalar_one_or_none()

        if not db_product:
            logger.debug(f"Product with ID {product_id} not found.")
            return None
        
        logger.debug(f"Product {product_id} found, converting to domain model.")

        domain_price = Money(amount=Decimal(str(db_product.price_amount)), currency=db_product.price_currency)
        
        domain_image_url = None
        if db_product.image_url_url:
            # Ensure HttpUrl conversion if DomainImageUrl expects it
            domain_image_url = DomainImageUrl(url=str(db_product.image_url_url), alt_text=db_product.image_alt_text)
            
        domain_attributes: List[DomainAttribute] = []
        if db_product.attributes: # Check if attributes were loaded and exist
            for attr_sql in db_product.attributes:
                domain_attributes.append(DomainAttribute(name=attr_sql.name, value=attr_sql.value))

        return DomainProduct(
            _id=EntityId.from_string(db_product.id),
            name=db_product.name,
            description=db_product.description,
            sku=db_product.sku,
            active=db_product.active,
            stock_quantity=db_product.stock_quantity,
            price=domain_price,
            category_id=EntityId.from_string(db_product.category_id),
            image_url=domain_image_url,
            attributes=domain_attributes,
            created_at=db_product.created_at,
            updated_at=db_product.updated_at
        )
