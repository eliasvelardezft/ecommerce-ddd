from uuid import UUID

from pydantic import BaseModel

from src.domain.orders.models.OrderItem import OrderItem


class PlaceOrderCommand(BaseModel):
    customer_id: UUID
    items: list[OrderItem]
