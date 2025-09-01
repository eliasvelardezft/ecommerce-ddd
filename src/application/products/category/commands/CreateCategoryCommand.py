from typing import Optional

from pydantic import BaseModel, Field


class CreateCategoryCommand(BaseModel):
    """Command to create a new category."""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the category.")
    description: Optional[str] = Field(None, description="Description for the category.")
    parent_category_id: Optional[str] = Field(None, description="ID of the parent category, if any.")
