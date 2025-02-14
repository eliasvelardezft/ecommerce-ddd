"""Core/infrastructure dependencies"""
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.infrastructure.core.settings import settings
from typing import AsyncGenerator

from src.domain.core.events.DomainEvent import DomainEvent
from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from src.domain.core.events.EventStore import EventStore
from src.domain.core.events.handlers.EventStoreHandler import EventStoreHandler
from src.infrastructure.core.persistence.base import BaseModel


# MongoDB client for read model
mongo_client = AsyncIOMotorClient(
    settings.mongo_url,
    uuidRepresentation="standard"
)
mongo_db = mongo_client[settings.mongo_db]

# SQLite engine for write model
write_engine = create_async_engine(settings.sqlite_url)
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

def get_event_store():
    return EventStore()


def get_base_event_dispatcher(
    event_store: EventStore = Depends(get_event_store)
):
    """Creates a base event dispatcher with common handlers like event store"""
    dispatcher = DomainEventDispatcher()
    
    # Register event store handler for all events
    dispatcher.register_handler(
        DomainEvent,  # Base event type to handle all events
        EventStoreHandler(event_store)
    )
    
    return dispatcher
