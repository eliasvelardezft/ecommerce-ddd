from datetime import datetime
from typing import Any, Dict, List, Optional

from domain.core.AggregateRoot import AggregateRoot
from domain.core.value_objects.EntityId import EntityId
from domain.core.value_objects.Money import Money
from domain.products.events.ProductActivatedEvent import ProductActivatedEvent
from domain.products.events.ProductCreatedEvent import ProductCreatedEvent
from domain.products.events.ProductDeactivatedEvent import (
    ProductDeactivatedEvent,
)
from domain.products.events.ProductPriceUpdatedEvent import (
    ProductPriceUpdatedEvent,
)
from domain.products.events.ProductStockUpdatedEvent import (
    ProductStockUpdatedEvent,
)
from domain.products.value_objects.Attribute import Attribute
from domain.products.value_objects.ImageUrl import ImageUrl


class Product(AggregateRoot):
    id: EntityId
    name: str
    description: str | None = None
    sku: str
    active: bool
    stock_quantity: int
    price: Money
    category_id: EntityId
    attributes: list[Attribute]
    image_url: ImageUrl | None
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        _id: EntityId,
        name: str,
        sku: str,
        category_id: EntityId,
        price: Money,
        description: str | None = None,
        active: bool = True,
        stock_quantity: int = 0,
        attributes: list[Attribute] | None = None,
        image_url: ImageUrl | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__()
        self.id = _id
        self.name = name
        self.description = description
        self.sku = sku
        self.active = active
        self.stock_quantity = stock_quantity
        self.price = price
        self.category_id = category_id
        self.attributes = attributes if attributes is not None else []
        self.image_url = image_url
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()

    @classmethod
    def create(
        cls,
        name: str,
        sku: str,
        category_id: EntityId,
        price: Money,
        active: bool = True,
        stock_quantity: int = 0,
        image_url: ImageUrl | None = None,
        attributes: list[Attribute] | None = None,
        description: str | None = None,
    ) -> 'Product':
        _id = EntityId.generate()
        product = cls(
            _id=_id,
            name=name,
            description=description,
            sku=sku,
            category_id=category_id,
            price=price,
            active=active,
            stock_quantity=stock_quantity,
            attributes=attributes,
            image_url=image_url,
        )
        product.add_domain_event(ProductCreatedEvent(
            aggregate_id=product.id,
            name=product.name,
            description=product.description,
            sku=product.sku,
            active=product.active,
            stock_quantity=product.stock_quantity,
            price_amount=product.price.amount,
            price_currency=product.price.currency,
            category_id=product.category_id,
            image_url=product.image_url.url if product.image_url else None,
            image_alt_text=product.image_url.alt_text if product.image_url else None,
            attributes=[attribute.model_dump() for attribute in product.attributes],
        ))
        return product

    def add_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount to add to stock must be positive.")
        self.stock_quantity += amount
        self.updated_at = datetime.now()
        self.add_domain_event(ProductStockUpdatedEvent(
            aggregate_id=self.id,
            stock_quantity=self.stock_quantity,
        ))

    def remove_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount to remove from stock must be positive.")
        if self.stock_quantity < amount:
            raise ValueError("Insufficient stock to remove.")
        self.stock_quantity -= amount
        self.updated_at = datetime.now()
        self.add_domain_event(ProductStockUpdatedEvent(
            aggregate_id=self.id,
            stock_quantity=self.stock_quantity,
        ))

    def update_price(self, new_price: Money) -> None:
        if new_price.amount < 0:
            raise ValueError("Price cannot be negative.")
        self.price = new_price
        self.updated_at = datetime.now()
        self.add_domain_event(ProductPriceUpdatedEvent(
            aggregate_id=self.id,
            price=self.price,
        ))

    def activate(self) -> None:
        if not self.active:
            self.active = True
            self.updated_at = datetime.now()
            self.add_domain_event(ProductActivatedEvent(
                aggregate_id=self.id,
            ))

    def deactivate(self) -> None:
        if self.active:
            self.active = False
            self.updated_at = datetime.now()
            self.add_domain_event(ProductDeactivatedEvent(
                aggregate_id=self.id,
            ))
