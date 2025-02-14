from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class OrderItemDTO(BaseModel):
    product_name: str
    product_id: UUID
    quantity: int
    subtotal: float
    final_price: float


class OrderDetailsDTO(BaseModel):
    id: str
    customer_id: str
    items_count: int
    total_amount: float
    created_at: datetime
    status: str
