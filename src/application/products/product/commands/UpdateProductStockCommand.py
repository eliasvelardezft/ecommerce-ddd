from uuid import UUID

from pydantic import BaseModel, Field


class UpdateProductStockCommand(BaseModel):
    """Command to update the stock quantity of a product."""
    product_id: UUID = Field(..., description="ID of the product to update.")
    change_in_quantity: int = Field(..., description="The amount to change the stock by (positive to add, negative to remove).")
