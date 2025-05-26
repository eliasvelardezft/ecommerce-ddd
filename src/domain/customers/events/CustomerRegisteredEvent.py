from domain.core.events.DomainEvent import DomainEvent
from typing import Dict, Any

class CustomerRegisteredEvent(DomainEvent):
    def __init__(self, aggregate_id: str, name: str, email: str):
        super().__init__(aggregate_id)
        self.name = name
        self.email = email

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "name": self.name,
            "email": self.email
        })
        return base_dict
