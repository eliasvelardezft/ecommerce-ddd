from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

from domain.core.value_objects.EntityId import EntityId
from domain.core.value_objects.Money import Money  # Using the core Money VO


class OrderItem(BaseModel):
    id: Annotated[EntityId, Field(default_factory=EntityId.generate)]
    product_id: EntityId
    product_name: Annotated[str, Field(min_length=1, max_length=255)]
    quantity: Annotated[int, Field(gt=0)]
    unit_price: Money # Instance of the Money class from core value_objects
    # discount_amount field removed for now

    model_config = {
        "extra": "forbid",
        "arbitrary_types_allowed": True # To allow Money type from domain.core
    }

    # model_validator for currency consistency removed as discount_amount is removed.
    # Currency of unit_price will be validated by the Order aggregate when an item is added.

    @property
    def subtotal(self) -> Money:
        """Calculates the item's subtotal (unit_price * quantity)."""
        # Multiplication is handled by the Money class.
        # It will return a new Money object with the same currency as unit_price.
        return self.unit_price * self.quantity
