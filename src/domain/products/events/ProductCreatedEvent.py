from decimal import Decimal
from uuid import UUID

from domain.core.events.DomainEvent import DomainEvent


class ProductCreatedEvent(DomainEvent):
    name: str
    description: str
    sku: str
    active: bool
    stock_quantity: int
    price_amount: Decimal
    price_currency: str
    category_id: UUID
    attributes: list[dict]
    image_url: str | None
    image_alt_text: str | None

    def __init__(
        self,
        aggregate_id: UUID,
        name: str,
        description: str,
        sku: str,
        active: bool,
        stock_quantity: int,
        price_amount: Decimal,
        price_currency: str,
        category_id: UUID,
        attributes: list[dict],
        image_url: str | None = None,
        image_alt_text: str | None = None,
    ):
        super().__init__(str(aggregate_id))
        self.name = name
        self.description = description
        self.sku = sku
        self.active = active
        self.stock_quantity = stock_quantity
        self.price_amount = price_amount
        self.price_currency = price_currency
        self.category_id = category_id
        self.attributes = attributes
        self.image_url = image_url
        self.image_alt_text = image_alt_text

    def to_dict(self) -> dict:
        return {
            "aggregate_id": self.aggregate_id,
            "name": self.name,
            "description": self.description,
            "sku": self.sku,
            "active": self.active,
            "stock_quantity": self.stock_quantity,
            "price_amount": str(self.price_amount),
            "price_currency": self.price_currency,
            "category_id": str(self.category_id),
            "image_url": self.image_url,
            "image_alt_text": self.image_alt_text,
            "attributes": self.attributes,
        }
