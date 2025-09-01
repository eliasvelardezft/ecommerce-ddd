from datetime import datetime
from typing import List, Optional

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
    items: List[OrderItemDTO]
    items_count: int
    total_amount: float
    created_at: datetime
    status: str
    shipping_details: Optional[ShippingDetails] = None
    tracking_number: Optional[str] = None
    cancellation_reason: Optional[str] = None
