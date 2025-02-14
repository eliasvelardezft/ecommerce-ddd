from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetOrderDetailsQuery:
    id: UUID
