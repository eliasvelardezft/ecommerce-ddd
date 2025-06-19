import logging

# --- Import and Setup Structured Logging --- 
from infrastructure.core.logging_config import setup_logging
setup_logging() # Call this early to configure logging for the entire application
# --- End Logging Setup ---

from fastapi import FastAPI
from contextlib import asynccontextmanager

from infrastructure.core.settings import settings
from api.customers.router import router as customer_router
from api.orders.router import router as order_router
from api.products.router.category import router as category_router
from api.products.router.product import router as product_router
from api.dependencies import init_db, get_mongo_db
from infrastructure.customers.services.EmailService import EmailService
from infrastructure.customers.services.AuditService import AuditService
from infrastructure.customers.persistence.CustomerReadRepository import CustomerReadRepository
from infrastructure.orders.persistence.OrderReadRepository import OrderReadRepository
from infrastructure.products.persistence.ProductReadRepository import ProductReadRepository
from infrastructure.products.persistence.CategoryReadRepository import CategoryReadRepository
from domain.core.events.EventStore import EventStore
from infrastructure.core.events.bootstrap import (
    create_domain_event_dispatcher,
    create_integration_event_dispatcher,
)
from infrastructure.core.events.registry import register_all_event_handlers
from infrastructure.orders.events.OrderIntegrationPublisher import OrderIntegrationEventPublisher

# Standard logger for this file, will now use the Rich setup configured by setup_logging()
logger = logging.getLogger(__name__) 

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application lifespan startup...")
    await init_db()
    logger.info("Databases initialized.")

    mongo_database = get_mongo_db()
    logger.info("MongoDB connection established.")

    email_service = EmailService()
    audit_service = AuditService()
    customer_read_repo = CustomerReadRepository(mongo_database)
    order_read_repo = OrderReadRepository(mongo_database)
    product_read_repo = ProductReadRepository(mongo_database)
    category_read_repo = CategoryReadRepository(mongo_database)
    event_store = EventStore()
    logger.info("Core services and repositories instantiated.")

    event_handler_dependencies = {
        "customer_read_repository": customer_read_repo,
        "order_read_repository": order_read_repo,
        "product_read_repository": product_read_repo,
        "category_read_repository": category_read_repo,
        "email_service": email_service,
        "audit_service": audit_service,
        "event_store": event_store, 
    }

    domain_event_dispatcher = create_domain_event_dispatcher(event_handler_dependencies)
    logger.info("DomainEventDispatcher created and core handlers registered.")

    integration_event_dispatcher = create_integration_event_dispatcher()
    logger.info("IntegrationEventDispatcher created.")

    register_all_event_handlers(
        domain_event_dispatcher,
        integration_event_dispatcher,
        event_handler_dependencies
    )
    logger.info("All application event handlers registered.")

    order_integration_publisher = OrderIntegrationEventPublisher(integration_event_dispatcher)
    logger.info("OrderIntegrationEventPublisher instantiated.")

    app.state.domain_event_dispatcher = domain_event_dispatcher
    app.state.integration_event_dispatcher = integration_event_dispatcher
    app.state.order_integration_event_publisher = order_integration_publisher
    logger.info("Event dispatchers and publishers added to app.state.")

    yield
    logger.info("Application lifespan shutdown...")

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.api_debug,
    lifespan=lifespan,
)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.api_title}",
        "version": settings.api_version
    }

app.include_router(customer_router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(category_router, prefix="/api")
app.include_router(product_router, prefix="/api")

logger.info(f"{settings.api_title} application startup complete.")
