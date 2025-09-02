from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent


class ProductActivatedEvent(DomainEvent):
    """Event raised when a product is activated."""

    def __init__(self, aggregate_id: UUID):
        super().__init__(aggregate_id=str(aggregate_id))
