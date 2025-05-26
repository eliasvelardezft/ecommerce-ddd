from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime, timezone

from domain.core.events.DomainEvent import DomainEvent
from domain.orders.models.OrderItem import OrderItem


class OrderPlacedEvent(DomainEvent):
    """Internal Domain Event raised when an order is successfully placed."""
    def __init__(
        self,
        aggregate_id: UUID,
        customer_id: UUID,
        items: List[OrderItem],
    ):
        super().__init__(aggregate_id=str(aggregate_id))
        self.customer_id: UUID = customer_id
        self.items: List[OrderItem] = items

    @property
    def items_count(self) -> int:
        return len(self.items)

    @property
    def total_amount(self) -> float:
        return sum(item.unit_price * item.quantity for item in self.items)

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "customer_id": self.customer_id,
            "total_amount": self.total_amount,
            "items_count": self.items_count
        })
        return base_dict
