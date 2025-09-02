from datetime import datetime
from typing import Any
from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent


class CategoryParentChangedEvent(DomainEvent):
    """Event raised when a category's parent is changed."""

    new_parent_category_id: UUID | None
    prev_parent_category_id: UUID | None
    updated_at: datetime

    def __init__(
        self,
        aggregate_id: UUID,
        new_parent_category_id: UUID | None,
        prev_parent_category_id: UUID | None,
        updated_at: datetime,
    ):
        super().__init__(str(aggregate_id))
        self.new_parent_category_id = new_parent_category_id
        self.prev_parent_category_id = prev_parent_category_id
        self.updated_at = updated_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "aggregate_id": self.aggregate_id,
            "new_parent_category_id": str(self.new_parent_category_id)
            if self.new_parent_category_id
            else None,
            "prev_parent_category_id": str(self.prev_parent_category_id)
            if self.prev_parent_category_id
            else None,
            "updated_at": self.updated_at.isoformat(),
        }
