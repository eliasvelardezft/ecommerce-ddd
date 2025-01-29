from abc import ABC
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Any

class Message(ABC):
    """Base class for all messages (Commands and Events)"""
    def __init__(self):
        self.id: UUID = uuid4()
        self.timestamp: datetime = datetime.now()
        self.message_type: str = self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": str(self.id),
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type
        } 