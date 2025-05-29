from datetime import datetime
from typing import List
from uuid import UUID

from domain.core.AggregateRoot import AggregateRoot
from domain.orders.events.OrderPlacedEvent import OrderPlacedEvent
from domain.orders.events.OrderProcessingEvent import OrderProcessingEvent
from domain.orders.events.OrderCompletedEvent import OrderCompletedEvent
from domain.orders.events.OrderCancelledEvent import OrderCancelledEvent
from domain.orders.exceptions import OrderValidationException
from domain.orders.models.OrderItem import OrderItem
from domain.orders.models.OrderStatus import OrderStatus
from domain.orders.value_objects.ShippingDetails import ShippingDetails


class Order(AggregateRoot):
    def __init__(
        self,
        id: UUID,
        customer_id: UUID,
        items: List[OrderItem],
        shipping_details: ShippingDetails,
    ):
        super().__init__()
        self.id = id
        self.items = items
        self.customer_id = customer_id
        self.shipping_details = shipping_details
        self.created_at = datetime.now()
        self.updated_at = None
        self.status = OrderStatus.DRAFT

    @property
    def total_amount(self):
        return sum([item.subtotal for item in self.items])

    @staticmethod
    def create(
        id: UUID,
        customer_id: UUID,
        items: List[OrderItem],
        shipping_details: ShippingDetails,
    ) -> "Order":
        if not items:
            raise OrderValidationException("order has no items")
        
        order = Order(
            id=id,
            customer_id=customer_id,
            items=items,
            shipping_details=shipping_details,
        )

        order.add_domain_event(
            OrderPlacedEvent(
                aggregate_id=order.id,
                customer_id=order.customer_id,
                order_number=str(order.id),
                items_data=[item.model_dump() for item in items],
                total_amount_str=f"{order.total_amount:.2f}",
                currency="USD",
                shipping_details_data=order.shipping_details.model_dump(),
                status=order.status.value
            )
        )

        return order

    def processing(self):
        if self.status != OrderStatus.DRAFT:
            raise OrderValidationException("can only process draft orders")

        self.status = OrderStatus.PROCESSING
        self.updated_at = datetime.now()

        self.add_domain_event(
            OrderProcessingEvent(aggregate_id=self.id)
        )

    def cancelled(self):
        if self.status not in [OrderStatus.DRAFT, OrderStatus.PROCESSING]:
            raise OrderValidationException("can only process draft/processing orders")

        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now()

        self.add_domain_event(
            OrderCancelledEvent(aggregate_id=self.id)
        )

    def completed(self):
        if self.status != OrderStatus.PROCESSING:
            raise OrderValidationException("can only complete processing orders")

        self.status = OrderStatus.COMPLETED
        self.updated_at = datetime.now()

        self.add_domain_event(
            OrderCompletedEvent(aggregate_id=self.id)
        )
