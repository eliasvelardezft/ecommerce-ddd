from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ListCategoriesQuery(BaseModel):
    """Query to list categories. 
    If parent_category_id is provided, lists its direct children.
    If parent_category_id is None, lists top-level categories.
    """
    parent_category_id: UUID | None = Field(None, description="ID of the parent category to list children for. If None, lists top-level categories.")
    recursive: bool = Field(False, description="If True and parent_category_id is None, attempts to build full trees for all top-level categories.")
