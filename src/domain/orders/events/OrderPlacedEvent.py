from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime

from domain.core.events.DomainEvent import DomainEvent
from domain.orders.models.OrderItem import OrderItem
from domain.core.value_objects.Money import Money


class OrderPlacedEvent(DomainEvent):
    """Internal Domain Event raised when an order is successfully placed."""
    def __init__(
        self,
        aggregate_id: UUID,
        customer_id: UUID,
        order_number: str,
        items_data: List[Dict[str, Any]],
        amount: Money,
        shipping_details_data: Dict[str, Any],
        status: str,
    ):
        super().__init__(aggregate_id=str(aggregate_id))
        self.customer_id: UUID = customer_id
        self.order_number: str = order_number
        self.items_data: list[dict[str, Any]] = items_data
        self.total_amount: float = amount.amount
        self.currency: str = amount.currency
        self.shipping_details_data: Dict[str, Any] = shipping_details_data
        self.status: str = status

    @property
    def items_count(self) -> int:
        return len(self.items_data)

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "customer_id": str(self.customer_id),
            "order_number": self.order_number,
            "items_data": self.items_data,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "shipping_details_data": self.shipping_details_data,
            "status": self.status,
            "items_count": self.items_count
        })
        return base_dict
