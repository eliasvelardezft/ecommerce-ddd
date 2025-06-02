from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from domain.core.events.DomainEvent import DomainEvent


class OrderCancelledEvent(DomainEvent):
    """Domain Event raised when an order is cancelled."""
    
    def __init__(
        self,
        aggregate_id: UUID,
        order_number: str,
        customer_id: UUID,
        status: str,
        total_amount_str: str,
        currency: str,
        cancellation_reason: Optional[str] = None,
    ):
        super().__init__(aggregate_id=str(aggregate_id))
        self.order_number: str = order_number
        self.customer_id: UUID = customer_id
        self.status: str = status
        self.total_amount_str: str = total_amount_str
        self.currency: str = currency
        self.cancellation_reason: Optional[str] = cancellation_reason

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "order_number": self.order_number,
            "customer_id": str(self.customer_id),
            "status": self.status,
            "total_amount_str": self.total_amount_str,
            "currency": self.currency,
            "cancellation_reason": self.cancellation_reason,
        })
        return base_dict
