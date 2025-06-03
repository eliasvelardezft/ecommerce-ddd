from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

class CategoryDetailsDTO(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    parent_category_id: Optional[UUID]
    children_ids: List[UUID] = [] 
    children: List["CategoryDetailsDTO"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {
        "arbitrary_types_allowed": True 
    }
