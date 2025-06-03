from uuid import UUID
from pydantic import BaseModel, Field

class GetProductByIdQuery(BaseModel):
    product_id: UUID = Field(..., description="ID of the product to retrieve.")
