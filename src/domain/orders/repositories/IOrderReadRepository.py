from abc import ABC
from typing import List
from uuid import UUID

from src.domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO


class IOrderReadRepository(ABC):
    async def get_order_details(self, id: UUID) -> OrderDetailsDTO:
        raise NotImplementedError

    async def get_all_order_details(self) -> List[OrderDetailsDTO]:
        raise NotImplementedError

    async def update_read_model(self, order: OrderDetailsDTO) -> None:
        raise NotImplementedError
