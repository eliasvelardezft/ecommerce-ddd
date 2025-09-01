from pydantic import BaseModel, Field


class ActivateProductCommand(BaseModel):
    product_id: str = Field(..., description="ID of the product to activate.")
