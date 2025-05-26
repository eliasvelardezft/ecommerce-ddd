from datetime import datetime
from uuid import UUID, uuid4
import json
from fastapi.encoders import jsonable_encoder

from domain.core.events.DomainEvent import DomainEvent


class StoredEvent:
    def __init__(
        self,
        event_type: str,
        data: str,
        aggregate_id: str,
        timestamp: datetime = None,
        event_id: UUID = None
    ):
        self.event_id = event_id or uuid4()
        self.timestamp = timestamp or datetime.now()
        self.event_type = event_type
        self.data = data
        self.aggregate_id = aggregate_id

    @classmethod
    def from_domain_event(cls, event: 'DomainEvent') -> 'StoredEvent':
        return cls(
            event_type=event.__class__.__name__,
            data=json.dumps(jsonable_encoder(event.to_dict())),
            aggregate_id=event.aggregate_id
        )
