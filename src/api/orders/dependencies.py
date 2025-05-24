from fastapi import Depends

from src.api.dependencies import (
    get_event_dispatcher,
    get_db_session,
    get_mongo_db,
)
from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from src.infrastructure.orders.persistence.OrderReadRepository import OrderReadRepository
from src.infrastructure.orders.persistence.OrderWriteRepository import OrderWriteRepository

def get_order_write_repository(db=Depends(get_db_session)):
    return OrderWriteRepository(session=db)

def get_order_read_repository(mongo_db=Depends(get_mongo_db)):
    return OrderReadRepository(database=mongo_db)

def get_order_event_dispatcher(
    dispatcher: DomainEventDispatcher = Depends(get_event_dispatcher),
):
    """Returns the configured event dispatcher from app state"""
    return dispatcher
