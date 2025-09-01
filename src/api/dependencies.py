"""Core/infrastructure dependencies"""
from typing import AsyncGenerator

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.core.events.EventStore import EventStore
from infrastructure.core.events.bootstrap import (
    create_domain_event_dispatcher,
    create_integration_event_dispatcher,
)
from infrastructure.core.events.integration_event_dispatcher import (
    IntegrationEventDispatcher,
)
from infrastructure.core.events.registry import register_all_event_handlers
from infrastructure.core.persistence.base import BaseModel
from infrastructure.core.settings import settings
from infrastructure.orders.events.OrderIntegrationPublisher import (
    OrderIntegrationEventPublisher,
)

# MongoDB client for read model
mongo_client = AsyncIOMotorClient(
    settings.mongo_url,
    uuidRepresentation="standard"
)
mongo_db = mongo_client[settings.mongo_db]

# PostgreSQL engine for write model
write_engine = create_async_engine(
    settings.postgres_url,
    echo=settings.api_debug,  # Log SQL queries in debug mode
    pool_size=10,            # Connection pool size
    max_overflow=20,         # Additional connections beyond pool_size
    pool_pre_ping=True,      # Validate connections before use
    pool_recycle=3600        # Recycle connections after 1 hour
)
AsyncSessionLocal = sessionmaker(
    write_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_mongo_db():
    return mongo_db

# Event System Dependencies
def get_domain_event_dispatcher(mongo_db = Depends(get_mongo_db)) -> DomainEventDispatcher:
    """Create a fresh DomainEventDispatcher with all handlers registered."""
    from infrastructure.customers.persistence.CustomerReadRepository import (
        CustomerReadRepository,
    )
    from infrastructure.customers.services.AuditService import AuditService
    from infrastructure.customers.services.EmailService import EmailService
    from infrastructure.orders.persistence.OrderReadRepository import (
        OrderReadRepository,
    )
    from infrastructure.products.persistence.CategoryReadRepository import (
        CategoryReadRepository,
    )
    from infrastructure.products.persistence.ProductReadRepository import (
        ProductReadRepository,
    )

    # Create event handler dependencies using injected mongo_db
    event_handler_dependencies = {
        "customer_read_repository": CustomerReadRepository(mongo_db),
        "order_read_repository": OrderReadRepository(mongo_db),
        "product_read_repository": ProductReadRepository(mongo_db),
        "category_read_repository": CategoryReadRepository(mongo_db),
        "email_service": EmailService(),
        "audit_service": AuditService(),
        "event_store": EventStore(),
    }

    # Create and configure domain event dispatcher
    domain_event_dispatcher = create_domain_event_dispatcher(event_handler_dependencies)

    # Register all event handlers
    integration_event_dispatcher = get_integration_event_dispatcher()
    register_all_event_handlers(
        domain_event_dispatcher,
        integration_event_dispatcher,
        event_handler_dependencies
    )

    return domain_event_dispatcher

def get_integration_event_dispatcher() -> IntegrationEventDispatcher:
    """Create a fresh IntegrationEventDispatcher."""
    return create_integration_event_dispatcher()

def get_order_integration_event_publisher(
    integration_dispatcher: IntegrationEventDispatcher = Depends(get_integration_event_dispatcher)
) -> OrderIntegrationEventPublisher:
    """Create a fresh OrderIntegrationEventPublisher."""
    return OrderIntegrationEventPublisher(integration_dispatcher)

def get_event_store() -> EventStore:
    """Create a fresh EventStore instance."""
    return EventStore()
