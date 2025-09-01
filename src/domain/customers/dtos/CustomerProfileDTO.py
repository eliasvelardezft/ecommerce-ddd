from datetime import datetime

from pydantic import BaseModel


class CustomerProfileDTO(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    total_orders: int
    last_order_date: datetime | None = None
    favorite_products: list[str] = []
    loyalty_tier: str = "Bronze"
