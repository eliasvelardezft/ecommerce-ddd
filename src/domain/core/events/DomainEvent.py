from datetime import datetime
from typing import Dict, Any


class DomainEvent:
    def __init__(self, aggregate_id: str):
        super().__init__()
        self.aggregate_id = aggregate_id
        self.occurred_on = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat()
        })
        return base_dict
