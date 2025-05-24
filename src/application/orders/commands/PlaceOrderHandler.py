import logging
from uuid import uuid4

from .PlaceOrderCommand import PlaceOrderCommand
from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from src.domain.orders.models.Order import Order
from src.infrastructure.orders.persistence import OrderWriteRepository 


logger = logging.getLogger(__name__)


class PlaceOrderHandler:
    def __init__(
        self,
        write_repository: OrderWriteRepository,
        event_dispatcher: DomainEventDispatcher
    ):
        self._repository = write_repository
        self._dispatcher = event_dispatcher

    async def handle(self, command: PlaceOrderCommand):
        logger.info(f"[Command] Processing PlaceOrderCommand for {command.customer_id}")
        order = Order.create(
            id=uuid4(),
            customer_id=command.customer_id,
            items=command.items
        )

        await self._repository.save(order)
        logger.info(f"Order saved to write repository: {order.id}")

        for event in order.domain_events:
            await self._dispatcher.dispatch(event)
        order.clear_domain_events()

        return order
