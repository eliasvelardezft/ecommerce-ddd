from datetime import datetime

from pydantic import BaseModel

from domain.orders.value_objects.ShippingDetails import ShippingDetails


class OrderItemDTO(BaseModel):
    product_name: str
    product_id: str
    quantity: int
    subtotal: float
    final_price: float


class OrderDetailsDTO(BaseModel):
    id: str
    customer_id: str
    items: list[OrderItemDTO]
    items_count: int
    total_amount: float
    created_at: datetime
    status: str
    shipping_details: ShippingDetails | None = None
    tracking_number: str | None = None
    cancellation_reason: str | None = None
