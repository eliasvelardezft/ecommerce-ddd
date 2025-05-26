import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from api.dependencies import (
    get_domain_event_dispatcher, 
    get_order_integration_event_publisher
)
from api.orders.dependencies import (
    get_order_write_repository,
    get_order_read_repository,
)
from application.orders.commands.PlaceOrderCommand import PlaceOrderCommand
from application.orders.commands.PlaceOrderHandler import PlaceOrderHandler
from application.orders.queries.GetOrderDetailsQuery import GetOrderDetailsQuery
from application.orders.queries.GetOrderDetailsHandler import GetOrderDetailsHandler
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from infrastructure.orders.events.OrderIntegrationPublisher import OrderIntegrationEventPublisher
from domain.orders.repositories.IOrderReadRepository import IOrderReadRepository
from domain.orders.repositories.IOrderWriteRepository import IOrderWriteRepository


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.post("/")
async def place_order(
    command: PlaceOrderCommand,
    write_repository: IOrderWriteRepository = Depends(get_order_write_repository),
    domain_event_dispatcher: DomainEventDispatcher = Depends(get_domain_event_dispatcher),
    order_integration_publisher: OrderIntegrationEventPublisher = Depends(get_order_integration_event_publisher)
):
    logger.info(f"[API /orders POST] Received PlaceOrderCommand for customer {command.customer_id}")

    handler = PlaceOrderHandler(
        write_repository=write_repository,
        domain_event_dispatcher=domain_event_dispatcher,
        integration_event_publisher=order_integration_publisher
    )

    try:
        order = await handler.handle(command)
        logger.info(f"[API /orders POST] Order {order.id} placed successfully.")
    except Exception as e:
        logger.error(
            f"[API /orders POST] Error processing PlaceOrderCommand {command}: {e}", exc_info=True
        )
        raise HTTPException(status_code=400, detail={"message": "Error placing order", "error_details": str(e)})

    return {"message": "Order placed successfully", "order_id": order.id, "customer_id": order.customer_id, "total_amount": order.total_amount}


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
