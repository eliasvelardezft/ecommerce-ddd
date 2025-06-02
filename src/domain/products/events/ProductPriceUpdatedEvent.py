from uuid import UUID
from domain.core.events.DomainEvent import DomainEvent
from domain.core.value_objects.Money import Money # Assuming Money is needed

class ProductPriceUpdatedEvent(DomainEvent):
    """Event raised when the price of a product is updated."""
    def __init__(self, aggregate_id: UUID, price: Money):
        super().__init__(aggregate_id=str(aggregate_id))
        self.price: Money = price

    def to_dict(self) -> dict:
        return {
            "aggregate_id": self.aggregate_id,
            "price": self.price.to_dict(),
        }
