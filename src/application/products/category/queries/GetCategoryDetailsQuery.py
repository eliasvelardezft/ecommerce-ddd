
from pydantic import BaseModel, Field


class GetCategoryDetailsQuery(BaseModel):
    """Query to retrieve details of a specific category, potentially including its children."""
    category_id: str = Field(..., description="ID of the category to retrieve.")
    recursive_children: bool | None = Field(description="Whether to recursively fetch all children.", default=False)
