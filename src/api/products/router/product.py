import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.products.dependencies import (
    get_category_write_repository,
    get_product_read_repository,
    get_product_write_repository,
    get_products_event_dispatcher,
)
from application.products.product.commands.activate_product_handler import (
    ActivateProductHandler,
)
from application.products.product.commands.ActivateProductCommand import (
    ActivateProductCommand,
)
from application.products.product.commands.create_product_handler import (
    CreateProductHandler,
)

# Product Commands and Handlers
from application.products.product.commands.CreateProductCommand import (
    CreateProductCommand,
)
from application.products.product.commands.deactivate_product_handler import (
    DeactivateProductHandler,
)
from application.products.product.commands.DeactivateProductCommand import (
    DeactivateProductCommand,
)
from application.products.product.commands.update_product_price_handler import (
    UpdateProductPriceHandler,
)
from application.products.product.commands.update_product_stock_handler import (
    UpdateProductStockHandler,
)
from application.products.product.commands.UpdateProductPriceCommand import (
    UpdateProductPriceCommand,
)
from application.products.product.commands.UpdateProductStockCommand import (
    UpdateProductStockCommand,
)
from application.products.product.queries.get_product_by_id_handler import (
    GetProductByIdHandler,
)

# Product Queries and Handlers
from application.products.product.queries.GetProductByIdQuery import (
    GetProductByIdQuery,
)
from application.products.product.queries.list_active_products_handler import (
    ListActiveProductsHandler,
)
from application.products.product.queries.ListActiveProductsQuery import (
    ListActiveProductsQuery,
)
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.products.repositories.ICategoryWriteRepository import (
    ICategoryWriteRepository,
)
from domain.products.repositories.IProductReadRepository import (
    IProductReadRepository,
)
from domain.products.repositories.IProductWriteRepository import (
    IProductWriteRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# ========================================
# PRODUCT ENDPOINTS
# ========================================

# Resource-oriented CRUD
@router.post("/")
async def create_product(
    command: CreateProductCommand,
    product_write_repository: Annotated[IProductWriteRepository, Depends(get_product_write_repository)],
    category_write_repository: Annotated[ICategoryWriteRepository, Depends(get_category_write_repository)],
    event_dispatcher: Annotated[DomainEventDispatcher, Depends(get_products_event_dispatcher)]
):
    """Create a new product"""
    logger.info(f"Creating product with SKU '{command.sku}'")
    handler = CreateProductHandler(
        product_write_repository=product_write_repository,
        category_write_repository=category_write_repository,
        domain_event_dispatcher=event_dispatcher
    )
    try:
        product = await handler.handle(command)
        logger.info(f"Successfully created product {product.id}")
        return {
            "message": "Product created successfully",
            "product_id": str(product.id),  # Convert EntityId to string
            "sku": product.sku,
            "name": product.name
        }
    except Exception as e:
        logger.error(f"Error creating product: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/{product_id}")
async def get_product(
    product_id: str,
    repository: Annotated[IProductReadRepository, Depends(get_product_read_repository)]
):
    """Get product by ID"""
    logger.info(f"Fetching product {product_id}")
    query = GetProductByIdQuery(product_id=product_id)
    handler = GetProductByIdHandler(repository)
    try:
        product = await handler.handle(query)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/")
async def list_active_products(
    repository: Annotated[IProductReadRepository, Depends(get_product_read_repository)]
):
    """List all active products"""
    logger.info("Fetching active products list")
    query = ListActiveProductsQuery()
    handler = ListActiveProductsHandler(repository)
    try:
        products = await handler.handle(query)
        return {
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        logger.error(f"Error listing active products: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.delete("/{product_id}")
async def delete_product(
    product_id: UUID,
    repository: Annotated[IProductWriteRepository, Depends(get_product_write_repository)]
):
    """Delete a product"""
    logger.info(f"Deleting product {product_id}")
    try:
        await repository.delete(product_id)
        logger.info(f"Successfully deleted product {product_id}")
        return {"message": "Product deleted successfully", "product_id": product_id}
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e

# Business-oriented actions
@router.put("/{product_id}/price")
async def update_product_price(
    product_id: UUID,
    command: UpdateProductPriceCommand,
    repository: Annotated[IProductWriteRepository, Depends(get_product_write_repository)],
    event_dispatcher: Annotated[DomainEventDispatcher, Depends(get_products_event_dispatcher)]
):
    """Update product price - business action"""
    logger.info(f"Updating price for product {product_id}")
    # Inject URL ID into command - REST compliant but works with existing handlers
    command.product_id = product_id
    handler = UpdateProductPriceHandler(repository, event_dispatcher)
    try:
        await handler.handle(command)
        logger.info(f"Successfully updated price for product {product_id}")
        return {
            "message": "Product price updated successfully",
            "product_id": product_id,
            "new_price": {
                "amount": float(command.new_price_amount),
                "currency": command.new_price_currency
            }
        }
    except Exception as e:
        logger.error(f"Error updating price for product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.put("/{product_id}/stock")
async def update_product_stock(
    product_id: UUID,
    command: UpdateProductStockCommand,
    repository: Annotated[IProductWriteRepository, Depends(get_product_write_repository)],
    event_dispatcher: Annotated[DomainEventDispatcher, Depends(get_products_event_dispatcher)]
):
    """Update product stock - business action"""
    logger.info(f"Updating stock for product {product_id}")
    # Inject URL ID into command - REST compliant but works with existing handlers
    command.product_id = product_id
    handler = UpdateProductStockHandler(repository, event_dispatcher)
    try:
        await handler.handle(command)
        logger.info(f"Successfully updated stock for product {product_id}")
        return {
            "message": "Product stock updated successfully",
            "product_id": product_id,
            "stock_change": command.change_in_quantity
        }
    except Exception as e:
        logger.error(f"Error updating stock for product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/{product_id}/activate")
async def activate_product(
    product_id: UUID,
    repository: Annotated[IProductWriteRepository, Depends(get_product_write_repository)],
    event_dispatcher: Annotated[DomainEventDispatcher, Depends(get_products_event_dispatcher)]
):
    """Activate product - business action"""
    logger.info(f"Activating product {product_id}")
    # Create command with URL ID - REST compliant but works with existing handlers
    command = ActivateProductCommand(product_id=product_id)
    handler = ActivateProductHandler(repository, event_dispatcher)
    try:
        await handler.handle(command)
        logger.info(f"Successfully activated product {product_id}")
        return {
            "message": "Product activated successfully",
            "product_id": product_id
        }
    except Exception as e:
        logger.error(f"Error activating product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/{product_id}/deactivate")
async def deactivate_product(
    product_id: UUID,
    repository: Annotated[IProductWriteRepository, Depends(get_product_write_repository)],
    event_dispatcher: Annotated[DomainEventDispatcher, Depends(get_products_event_dispatcher)]
):
    """Deactivate product - business action"""
    logger.info(f"Deactivating product {product_id}")
    # Create command with URL ID - REST compliant but works with existing handlers
    command = DeactivateProductCommand(product_id=product_id)
    handler = DeactivateProductHandler(repository, event_dispatcher)
    try:
        await handler.handle(command)
        logger.info(f"Successfully deactivated product {product_id}")
        return {
            "message": "Product deactivated successfully",
            "product_id": product_id
        }
    except Exception as e:
        logger.error(f"Error deactivating product {product_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e
