from datetime import datetime
from typing import Any
from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent


class CategoryDetailsUpdatedEvent(DomainEvent):
    """Event raised when a category's details (name, description) are updated."""
    updated_details: dict[str, Any]
    updated_at: datetime

    def __init__(self, aggregate_id: UUID, updated_details: dict[str, Any], updated_at: datetime):
        super().__init__(str(aggregate_id))
        self.updated_details: dict[str, Any] = updated_details
        self.updated_at = updated_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "aggregate_id": self.aggregate_id,
            "updated_details": self.updated_details,
            "updated_at": self.updated_at.isoformat(),
        }
