
from pydantic import BaseModel, Field


class UpdateCategoryDetailsCommand(BaseModel):
    """Command to update a category's details (name, description)."""
    category_id: str = Field(..., description="ID of the category to update.")
    name: str | None = Field(None, min_length=1, max_length=255, description="New name for the category.")
    description: str | None = Field(None, description="New description for the category. Can be set to null explicitly by passing None.")
