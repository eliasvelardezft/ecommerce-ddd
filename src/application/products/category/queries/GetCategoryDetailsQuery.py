from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class GetCategoryDetailsQuery(BaseModel):
    """Query to retrieve details of a specific category, potentially including its children."""
    category_id: UUID = Field(..., description="ID of the category to retrieve.")
    recursive_children: Optional[bool] = Field(description="Whether to recursively fetch all children.", default=False)
