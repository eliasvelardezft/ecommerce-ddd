from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CategoryDetailsDTO(BaseModel):
    id: str
    name: str
    description: str | None
    parent_category_id: str | None
    children_ids: list[str] = []
    children: list["CategoryDetailsDTO"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {
        "arbitrary_types_allowed": True
    }
