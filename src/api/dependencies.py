"""Core/infrastructure dependencies"""
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from infrastructure.core.settings import settings
from typing import AsyncGenerator

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.core.events.EventStore import EventStore
from infrastructure.orders.events.OrderIntegrationPublisher import OrderIntegrationEventPublisher
from infrastructure.core.persistence.base import BaseModel


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


async def init_db():
    async with write_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

def get_mongo_db():
    return mongo_db

def get_event_store(request: Request) -> EventStore:
    if hasattr(request.app.state, 'event_store'):
        return request.app.state.event_store
    return EventStore()

def get_domain_event_dispatcher(request: Request) -> DomainEventDispatcher:
    """Get the configured DomainEventDispatcher from app state."""
    if not hasattr(request.app.state, 'domain_event_dispatcher'):
        raise RuntimeError("DomainEventDispatcher not found in application state. Ensure it is initialized during startup.")
    return request.app.state.domain_event_dispatcher

def get_order_integration_event_publisher(request: Request) -> OrderIntegrationEventPublisher:
    """Get the configured OrderIntegrationEventPublisher from app state."""
    if not hasattr(request.app.state, 'order_integration_event_publisher'):
        raise RuntimeError("OrderIntegrationEventPublisher not found in application state. Ensure it is initialized during startup.")
    return request.app.state.order_integration_event_publisher
