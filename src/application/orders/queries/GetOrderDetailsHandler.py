from .GetOrderDetailsQuery import GetOrderDetailsQuery
from infrastructure.orders.persistence.OrderReadRepository import OrderReadRepository
from domain.orders.dtos.OrderDetailsDTO import OrderDetailsDTO


class GetOrderDetailsHandler:
    def __init__(
        self,
        read_repository: OrderReadRepository,
    ):
        self._repository = read_repository

    async def handle(self, query: GetOrderDetailsQuery) -> OrderDetailsDTO:
        order = await self._repository.get_order_details(id=query.id)
        return order
