from datetime import datetime
from uuid import uuid4
from typing import Dict, Any
from pydantic import BaseModel
from src.domain.core.events.Message import Message


class RegisterCustomerCommand(BaseModel):
    name: str
    email: str

    def to_customer_dict(self) -> Dict[str, Any]:
        return {
            "id": uuid4(),
            "name": self.name,
            "email": self.email,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
