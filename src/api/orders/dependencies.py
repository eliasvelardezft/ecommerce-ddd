from fastapi import Depends

from src.api.customers.dependencies import get_customer_read_repository
from src.api.dependencies import (
    get_base_event_dispatcher,
    get_db_session,
    get_mongo_db,
)
from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from src.domain.orders.events.OrderPlacedEvent import OrderPlacedEvent
from src.infrastructure.customers.persistence.CustomerReadRepository import CustomerReadRepository
from src.infrastructure.orders.persistence.OrderReadRepository import OrderReadRepository
from src.infrastructure.orders.persistence.OrderWriteRepository import OrderWriteRepository
from src.domain.customers.events.handlers.CustomerRegisteredHandlers import (
    UpdateReadModelHandler as UpdateCustomerReadModelHandler
)
from src.domain.orders.events.handlers.OrderPlacedHandlers import (
    UpdateReadModelHandler as UpdateOrderReadModelHandler
)

def get_order_write_repository(db=Depends(get_db_session)):
    return OrderWriteRepository(session=db)

def get_order_read_repository(mongo_db=Depends(get_mongo_db)):
    return OrderReadRepository(database=mongo_db)

def get_order_event_dispatcher(
    dispatcher: DomainEventDispatcher = Depends(get_base_event_dispatcher),
    customer_read_repository: CustomerReadRepository = Depends(get_customer_read_repository),
    order_read_repository: OrderReadRepository = Depends(get_order_read_repository),
):
    dispatcher.register_handler(
        OrderPlacedEvent,
        UpdateCustomerReadModelHandler(customer_read_repository)
    )
    dispatcher.register_handler(
        OrderPlacedEvent,
        UpdateOrderReadModelHandler(order_read_repository)
    )

    return dispatcher
