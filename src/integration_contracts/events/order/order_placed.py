import uuid
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

class OrderPlacedEventContractV1(BaseModel):
    order_id: UUID
    customer_id: UUID
    total_amount: float
    currency: str
    item_count: int
    occurred_on: datetime
    event_id: UUID = Field(default_factory=uuid.uuid4)
    event_type: str = Literal["order.placed"]
    event_version: str = Literal["1.0"]
    source_service: str = Literal["orders"]
