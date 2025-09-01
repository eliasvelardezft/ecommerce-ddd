from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class CategoryDetailsDTO(BaseModel):
    id: str
    name: str
    description: Optional[str]
    parent_category_id: Optional[str]
    children_ids: List[str] = [] 
    children: List["CategoryDetailsDTO"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {
        "arbitrary_types_allowed": True 
    }
