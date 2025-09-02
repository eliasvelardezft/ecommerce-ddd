from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent


class ProductStockUpdatedEvent(DomainEvent):
    """Event raised when the stock quantity of a product is updated."""

    def __init__(self, aggregate_id: UUID, stock_quantity: int):
        super().__init__(aggregate_id=str(aggregate_id))
        self.stock_quantity: int = stock_quantity

    def to_dict(self) -> dict:
        return {
            "aggregate_id": self.aggregate_id,
            "stock_quantity": self.stock_quantity,
        }
