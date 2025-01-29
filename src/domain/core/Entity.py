from abc import ABC
from uuid import UUID

class Entity(ABC):
    id: UUID

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id 