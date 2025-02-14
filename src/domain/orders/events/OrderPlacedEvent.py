from typing import Dict, Any
from uuid import UUID

from src.domain.core.events.DomainEvent import DomainEvent


class OrderPlacedEvent(DomainEvent):
    def __init__(
        self,
        aggregate_id: UUID,
        customer_id: UUID,
        total_amount: float,
        items_count: int,
    ):
        super().__init__(aggregate_id=aggregate_id)
        self.customer_id = customer_id
        self.total_amount = total_amount
        self.items_count = items_count

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "customer_id": self.customer_id,
            "total_amount": self.total_amount,
            "items_count": self.items_count
        })
        return base_dict
