from dataclasses import dataclass
from uuid import UUID

from src.domain.core.ValueObject import ValueObject


@dataclass
class OrderItem(ValueObject):
    product_id: UUID
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.unit_price * self.quantity
