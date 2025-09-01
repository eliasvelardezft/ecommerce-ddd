from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from domain.products.value_objects.Attribute import Attribute
from domain.products.value_objects.ImageUrl import ImageUrl


class CreateProductCommand(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the product.")
    description: Optional[str] = Field(None, description="Detailed description of the product.")
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit.")
    price_amount: Decimal = Field(..., gt=0, description="Price of the product.")
    price_currency: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., USD).")
    stock_quantity: int = Field(..., ge=0, description="Available stock quantity.")
    category_id: str = Field(..., description="ID of the category this product belongs to.")
    image_url: Optional[ImageUrl] = Field(None, description="Image URL for the product.")
    attributes: Optional[List[Attribute]] = Field(None, description="List of product attributes.")
    active: bool = Field(True, description="Whether the product is initially active.")
