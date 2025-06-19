from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

class UpdateProductPriceCommand(BaseModel):
    """Command to update the price of a product."""
    product_id: UUID = Field(..., description="ID of the product to update.")
    new_price_amount: Decimal = Field(..., gt=0, description="The new price amount for the product.")
    new_price_currency: str = Field(..., min_length=3, max_length=3, description="The currency code for the new price (e.g., USD).") 