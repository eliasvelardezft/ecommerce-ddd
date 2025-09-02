from abc import ABC, abstractmethod
from uuid import UUID

from domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO


class IOrderReadRepository(ABC):
    @abstractmethod
    async def get_order_details(self, id: UUID) -> OrderDetailsDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_all_order_details(self) -> list[OrderDetailsDTO]:
        raise NotImplementedError

    @abstractmethod
    async def update_read_model(self, order: OrderDetailsDTO) -> None:
        raise NotImplementedError
