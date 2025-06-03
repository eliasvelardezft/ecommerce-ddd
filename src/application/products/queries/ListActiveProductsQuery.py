from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class ListActiveProductsQuery(BaseModel):
    """Query to retrieve a list of active products."""
    category_id: Optional[UUID] = Field(None, description="Optional category ID to filter by.")
