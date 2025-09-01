from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent
from domain.core.value_objects.Money import Money


class OrderCancelledEvent(DomainEvent):
    """Domain Event raised when an order is cancelled."""

    def __init__(
        self,
        aggregate_id: UUID,
        order_number: str,
        customer_id: UUID,
        status: str,
        amount: Money,
        cancellation_reason: Optional[str] = None,
    ):
        super().__init__(aggregate_id=str(aggregate_id))
        self.order_number: str = order_number
        self.customer_id: UUID = customer_id
        self.status: str = status
        self.total_amount: float = amount.amount
        self.currency: str = amount.currency
        self.cancellation_reason: Optional[str] = cancellation_reason

    def to_dict(self) -> dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "order_number": self.order_number,
            "customer_id": str(self.customer_id),
            "status": self.status,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "cancellation_reason": self.cancellation_reason,
        })
        return base_dict
