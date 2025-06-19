import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.products.repositories.ICategoryWriteRepository import ICategoryWriteRepository
from domain.products.repositories.ICategoryReadRepository import ICategoryReadRepository

# Category Commands and Handlers
from application.products.category.commands.CreateCategoryCommand import CreateCategoryCommand
from application.products.category.commands.create_category_handler import CreateCategoryHandler
from application.products.category.commands.UpdateCategoryDetailsCommand import UpdateCategoryDetailsCommand
from application.products.category.commands.update_category_details_handler import UpdateCategoryDetailsHandler
from application.products.category.commands.ChangeCategoryParentCommand import ChangeCategoryParentCommand
from application.products.category.commands.change_category_parent_handler import ChangeCategoryParentHandler

# Category Queries and Handlers
from application.products.category.queries.GetCategoryDetailsQuery import GetCategoryDetailsQuery
from application.products.category.queries.get_category_details_handler import GetCategoryDetailsHandler
from application.products.category.queries.ListCategoriesQuery import ListCategoriesQuery
from application.products.category.queries.list_categories_handler import ListCategoriesHandler

from api.products.dependencies import (
    get_category_write_repository,
    get_category_read_repository,
    get_products_event_dispatcher,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/category",
    tags=["category"]
)


@router.post("/")
async def create_category(
    command: CreateCategoryCommand,
    repository: ICategoryWriteRepository = Depends(get_category_write_repository),
    event_dispatcher: DomainEventDispatcher = Depends(get_products_event_dispatcher)
):
    """Create a new category"""
    logger.info(f"Creating category '{command.name}'")
    handler = CreateCategoryHandler(repository, event_dispatcher)
    try:
        category = await handler.handle(command)
        logger.info(f"Successfully created category {category.id}")
        return {
            "message": "Category created successfully",
            "category_id": category.id,
            "name": category.name
        }
    except Exception as e:
        logger.error(f"Error creating category: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{category_id}")
async def get_category(
    category_id: UUID,
    repository: ICategoryReadRepository = Depends(get_category_read_repository)
):
    """Get category by ID"""
    logger.info(f"Fetching category {category_id}")
    query = GetCategoryDetailsQuery(category_id=category_id)
    handler = GetCategoryDetailsHandler(repository)
    try:
        category = await handler.handle(query)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category {category_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
async def list_categories(
    include_parent_id: bool = None,
    repository: ICategoryReadRepository = Depends(get_category_read_repository)
):
    """List categories with optional filtering"""
    logger.info("Fetching categories list")
    query = ListCategoriesQuery(include_parent_id=include_parent_id)
    handler = ListCategoriesHandler(repository)
    try:
        categories = await handler.handle(query)
        return {
            "categories": categories,
            "count": len(categories)
        }
    except Exception as e:
        logger.error(f"Error listing categories: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{category_id}")
async def update_category_details(
    category_id: UUID,
    command: UpdateCategoryDetailsCommand,
    repository: ICategoryWriteRepository = Depends(get_category_write_repository),
    event_dispatcher: DomainEventDispatcher = Depends(get_products_event_dispatcher)
):
    """Update category details"""
    logger.info(f"Updating details for category {category_id}")
    # Inject URL ID into command - REST compliant but works with existing handlers
    command.category_id = category_id
    handler = UpdateCategoryDetailsHandler(repository, event_dispatcher)
    try:
        await handler.handle(command)
        logger.info(f"Successfully updated category {category_id}")
        return {
            "message": "Category details updated successfully",
            "category_id": category_id
        }
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

# Business-oriented action
@router.put("/{category_id}/parent")
async def change_category_parent(
    category_id: UUID,
    command: ChangeCategoryParentCommand,
    repository: ICategoryWriteRepository = Depends(get_category_write_repository),
    event_dispatcher: DomainEventDispatcher = Depends(get_products_event_dispatcher)
):
    """Change category parent - business action"""
    logger.info(f"Changing parent for category {category_id}")
    # Inject URL ID into command - REST compliant but works with existing handlers
    command.category_id = category_id
    handler = ChangeCategoryParentHandler(repository, event_dispatcher)
    try:
        await handler.handle(command)
        logger.info(f"Successfully changed parent for category {category_id}")
        return {
            "message": "Category parent changed successfully",
            "category_id": category_id,
            "new_parent_id": command.new_parent_category_id
        }
    except Exception as e:
        logger.error(f"Error changing parent for category {category_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
