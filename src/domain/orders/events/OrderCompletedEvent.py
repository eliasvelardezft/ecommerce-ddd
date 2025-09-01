from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent
from domain.core.value_objects.Money import Money


class OrderCompletedEvent(DomainEvent):
    """Domain Event raised when an order is successfully completed."""
    
    def __init__(
        self,
        aggregate_id: UUID,
        order_number: str,
        customer_id: UUID,
        status: str,
        amount: Money,
        currency: str,
        tracking_number: Optional[str] = None,
    ):
        super().__init__(aggregate_id=str(aggregate_id))
        self.order_number: str = order_number
        self.customer_id: UUID = customer_id
        self.status: str = status
        self.total_amount: float = amount.amount
        self.currency: str = amount.currency
        self.currency: str = currency
        self.tracking_number: Optional[str] = tracking_number

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "order_number": self.order_number,
            "customer_id": str(self.customer_id),
            "status": self.status,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "tracking_number": self.tracking_number,
        })
        return base_dict
