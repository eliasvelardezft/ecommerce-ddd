from pydantic import BaseModel, Field


class GetProductByIdQuery(BaseModel):
    product_id: str = Field(..., description="ID of the product to retrieve.")
