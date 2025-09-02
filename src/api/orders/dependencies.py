from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import (
    get_db_session,
    get_domain_event_dispatcher,
    get_mongo_db,
)
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from infrastructure.orders.persistence.OrderReadRepository import (
    OrderReadRepository,
)
from infrastructure.orders.persistence.OrderWriteRepository import (
    OrderWriteRepository,
)


def get_order_write_repository(db: Annotated[AsyncSession, Depends(get_db_session)]):
    return OrderWriteRepository(session=db)


def get_order_read_repository(mongo_db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)]):
    return OrderReadRepository(database=mongo_db)


def get_order_event_dispatcher(
    dispatcher: Annotated[DomainEventDispatcher, Depends(get_domain_event_dispatcher)],
):
    """Returns the configured event dispatcher from app state"""
    return dispatcher
