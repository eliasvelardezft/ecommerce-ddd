from typing import Optional
from pydantic import BaseModel, Field

class ChangeCategoryParentCommand(BaseModel):
    """Command to change a category's parent."""
    category_id: str = Field(..., description="ID of the category to reparent.")
    new_parent_category_id: Optional[str] = Field(None, description="ID of the new parent category. Pass None to make it a top-level category.")
