from pydantic import BaseModel, Field
from typing import Optional


class ListActiveProductsQuery(BaseModel):
    """Query to retrieve a list of active products."""
    category_id: Optional[str] = Field(None, description="Optional category ID to filter by.")
