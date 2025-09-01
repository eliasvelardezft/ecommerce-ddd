from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from domain.products.value_objects.Attribute import Attribute
from domain.products.value_objects.ImageUrl import ImageUrl


class ProductDetailsDTO(BaseModel):
    id: str
    name: str
    description: str
    sku: str
    active: bool
    stock_quantity: int
    price_amount: Decimal
    price_currency: str
    category_id: str
    attributes: list[Attribute]
    image_url: Optional[ImageUrl]
    created_at: datetime
    updated_at: datetime
