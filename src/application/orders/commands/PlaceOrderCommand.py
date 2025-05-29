from uuid import UUID

from pydantic import BaseModel

from domain.orders.models.OrderItem import OrderItem
from domain.orders.value_objects.ShippingDetails import ShippingDetails


class PlaceOrderCommand(BaseModel):
    customer_id: UUID
    items: list[OrderItem]
    shipping_details: ShippingDetails
