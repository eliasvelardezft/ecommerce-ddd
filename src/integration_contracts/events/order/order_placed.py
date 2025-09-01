import uuid
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


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
