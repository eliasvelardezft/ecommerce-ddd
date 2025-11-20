import logging

from fastapi import FastAPI

from api.customers.router import router as customer_router
from api.orders.router import router as order_router
from api.products.router.category import router as category_router
from api.products.router.product import router as product_router
from infrastructure.core.logging_config import setup_logging
from infrastructure.core.settings import settings

setup_logging()  # Call this early to configure logging for the entire application

# Standard logger for this file, will now use the Rich setup configured by setup_logging()
logger = logging.getLogger(__name__)

# Enhanced API Documentation Configuration
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.api_debug,
    description="""
    🛒 **E-Commerce DDD API**
    
    A Domain-Driven Design e-commerce platform showcasing modern Python architecture with CQRS and Event Sourcing patterns.
    
    ## 🏗️ Architecture
    
    - **Domain-Driven Design**: Clean separation of business logic and infrastructure
    - **CQRS**: Command Query Responsibility Segregation for scalable reads/writes
    - **Event Sourcing**: Domain events and integration events for loose coupling
    - **Write Model**: PostgreSQL with SQLAlchemy for transactional consistency
    - **Read Model**: MongoDB for optimized query performance
    
    ## 🎯 Core Features
    
    ### Customer Management
    - Customer registration with domain validation
    - Profile management and retrieval
    - Event-driven customer lifecycle
    
    ### Product Catalog
    - Hierarchical category management
    - Product lifecycle (create, activate, deactivate)
    - Inventory tracking and price management
    - Rich product attributes and metadata
    
    ### Order Processing
    - Multi-item order placement
    - Real-time inventory validation
    - Order status tracking
    - Event-driven order fulfillment
    
    ## 🔄 Event-Driven Architecture
    
    The system uses domain events for internal consistency and integration events for external communication:
    
    - **Domain Events**: Customer registration, product creation, order placement
    - **Integration Events**: Cross-bounded-context communication
    - **Event Store**: Persistent event log for audit and replay capabilities
    
    ## 🛡️ Security & Quality
    
    - Type-safe with MyPy static analysis
    - Code quality enforced with Ruff linting
    - Comprehensive test coverage
    - Repository pattern for data access abstraction
    - Dependency injection for testability
    """,
    summary="Domain-Driven E-Commerce API with CQRS and Event Sourcing",
    contact={
        "name": settings.api_contact_name,
        "email": settings.api_contact_email,
        "url": settings.api_contact_url,
    },
    license_info={
        "name": settings.api_license_name,
        "url": settings.api_license_url,
    },
    openapi_tags=[
        {
            "name": "health",
            "description": "System health and status endpoints for monitoring and service discovery.",
        },
        {
            "name": "customers",
            "description": "Customer registration, authentication, and profile management. Handles the customer lifecycle from registration to profile updates.",
            "externalDocs": {
                "description": "Customer Domain Documentation",
                "url": "https://github.com/eliasvelardezft/ecommerce-ddd/wiki/customer-domain",
            },
        },
        {
            "name": "category",
            "description": "Product category hierarchy management. Create, update, and organize product categories in a tree structure.",
            "externalDocs": {
                "description": "Category Management Guide",
                "url": "https://github.com/eliasvelardezft/ecommerce-ddd/wiki/product-catalog",
            },
        },
        {
            "name": "products",
            "description": "Product catalog management including creation, pricing, inventory, and lifecycle operations (activate/deactivate).",
            "externalDocs": {
                "description": "Product Management Guide",
                "url": "https://github.com/eliasvelardezft/ecommerce-ddd/wiki/product-catalog",
            },
        },
        {
            "name": "orders",
            "description": "Order processing and management. Place orders, track status, and handle order lifecycle events.",
            "externalDocs": {
                "description": "Order Processing Guide",
                "url": "https://github.com/eliasvelardezft/ecommerce-ddd/wiki/order-processing",
            },
        },
    ],
    servers=[
        {
            "url": "http://localhost:8008",
            "description": "Local development server",
        },
        {
            "url": "https://api.ecommerce-ddd.com",
            "description": "Production server (when deployed)",
        },
    ],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get(
    "/",
    summary="API Welcome",
    description="Welcome endpoint providing basic API information",
    tags=["health"],
)
async def root():
    """Root endpoint that provides basic API information and status."""
    return {
        "message": f"Welcome to {settings.api_title}",
        "version": settings.api_version,
        "status": "operational",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get(
    "/health",
    summary="Health Check",
    description="""
    Health check endpoint for monitoring and load balancer probes.
    
    **Response Codes:**
    - `200`: Service is healthy and operational
    - `503`: Service is experiencing issues (if implemented with dependency checks)
    
    **Use Cases:**
    - Load balancer health checks
    - Monitoring and alerting systems
    - Container orchestration readiness probes
    """,
    tags=["health"],
)
async def health_check():
    """Health check endpoint for service monitoring."""
    return {
        "status": "healthy",
        "version": settings.api_version,
        "service": "ecommerce-ddd-api",
        "timestamp": "2025-09-15T00:00:00Z",  # In production, use datetime.utcnow()
    }


app.include_router(customer_router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(category_router, prefix="/api")
app.include_router(product_router, prefix="/api")

logger.info(f"{settings.api_title} application startup complete.")
