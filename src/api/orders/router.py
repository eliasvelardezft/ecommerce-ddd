import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from src.api.orders.dependencies import (
    get_order_write_repository,
    get_order_read_repository,
    get_order_event_dispatcher,
)
from src.application.orders.commands.PlaceOrderCommand import PlaceOrderCommand
from src.application.orders.commands.PlaceOrderHandler import PlaceOrderHandler
from src.application.orders.queries.GetOrderDetailsQuery import GetOrderDetailsQuery
from src.application.orders.queries.GetOrderDetailsHandler import GetOrderDetailsHandler
from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from src.domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO
from src.domain.orders.repositories.IOrderReadRepository import IOrderReadRepository
from src.domain.orders.repositories.IOrderWriteRepository import IOrderWriteRepository


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.post("/")
async def place_order(
    command: PlaceOrderCommand,
    repository: IOrderWriteRepository = Depends(get_order_write_repository),
    event_dispatcher: DomainEventDispatcher = Depends(get_order_event_dispatcher)
):
    logger.info("[post router] place_order router")

    handler = PlaceOrderHandler(
        write_repository=repository,
        event_dispatcher=event_dispatcher,
    )

    try:
        order = await handler.handle(command)
    except Exception as e:
        logger.error(
            f"[router exception] error with command {command.__dict__}. error: {str(e)}"
        )
        raise HTTPException(status_code=400, detail={"message": "Error placing order"})

    return order


@router.get("/{id}/details")
async def get_order_details(
    id: UUID,
    repository: IOrderReadRepository = Depends(get_order_read_repository),
):
    logger.info("[get router] get_order_details")

    query = GetOrderDetailsQuery(id)
    handler = GetOrderDetailsHandler(read_repository=repository)

    try:
        order_details = await handler.handle(query=query)
    except Exception as e:
        logger.error(
            f"[router exception] error with query {query.__dict__}. error: {str(e)}"
        )
        raise HTTPException(status_code=400, detail={"message": "Error getting order details"})
    
    return order_details
