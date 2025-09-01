from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent


class CategoryCreatedEvent(DomainEvent):
    """Event raised when a new category is created."""
    name: str
    description: str | None
    parent_category_id: UUID | None
    created_at: datetime

    def __init__(
        self,
        aggregate_id: UUID,
        name: str,
        description: str | None,
        parent_category_id: UUID | None,
        created_at: datetime,
    ):
        super().__init__(str(aggregate_id))
        self.name = name
        self.description = description
        self.parent_category_id = parent_category_id
        self.created_at = created_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "aggregate_id": self.aggregate_id,
            "name": self.name,
            "description": self.description,
            "parent_category_id": str(self.parent_category_id) if self.parent_category_id else None,
            "created_at": self.created_at.isoformat(),
        }
