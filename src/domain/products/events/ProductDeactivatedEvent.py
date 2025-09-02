from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent


class ProductDeactivatedEvent(DomainEvent):
    """Event raised when a product is deactivated."""

    def __init__(self, aggregate_id: UUID):
        super().__init__(aggregate_id=str(aggregate_id))
