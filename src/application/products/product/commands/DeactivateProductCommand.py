from pydantic import BaseModel, Field


class DeactivateProductCommand(BaseModel):
    product_id: str = Field(..., description="ID of the product to deactivate.")
