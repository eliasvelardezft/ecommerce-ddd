import logging
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.core.value_objects.EntityId import EntityId
from domain.orders.models.Order import Order, OrderItem
from domain.orders.repositories.IOrderWriteRepository import (
    IOrderWriteRepository,
)

from .Order import OrderItemSQL, OrderSQL

logger = logging.getLogger(__name__)


class OrderWriteRepository(IOrderWriteRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        logger.info("Initialized OrderWriteRepository")

    async def save(self, order: Order) -> Order:
        """Save or update an order"""
        logger.info("[Write] Saving order: %s", order.id)

        # Convert domain order to SQL model
        db_order = OrderSQL(
            id=str(order.id),  # Convert EntityId to string
            customer_id=str(order.customer_id),  # Convert EntityId to string
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

        # Convert domain items to SQL models
        db_order.items = [
            OrderItemSQL(
                id=str(uuid4()),  # Generate new ID for each item, convert to string
                order_id=str(order.id),  # Convert EntityId to string
                product_id=str(item.product_id),  # Convert EntityId to string
                quantity=item.quantity,
                unit_price=float(item.unit_price.amount),  # Convert Money to float for database
            )
            for item in order.items
        ]

        # Merge or add the order
        db_order = await self._session.merge(db_order)
        await self._session.commit()

        return order

    async def get_by_id(self, id: EntityId) -> Order | None:
        """Retrieve an order by ID"""
        result = await self._session.execute(select(OrderSQL).where(OrderSQL.id == str(id)))
        db_order = result.scalar_one_or_none()

        if not db_order:
            return None

        # Convert SQL model back to domain entity
        order_items = [
            OrderItem(
                product_id=EntityId.from_string(item.product_id),  # Convert string back to EntityId
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in db_order.items
        ]

        return Order(
            _id=EntityId.from_string(db_order.id),  # Convert string back to EntityId
            customer_id=EntityId.from_string(
                db_order.customer_id
            ),  # Convert string back to EntityId
            items=order_items,
            status=db_order.status,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at,
        )

    async def delete(self, order: Order) -> None:
        """Delete an order"""
        logger.info("[Write] Deleting order: %s", order.id)
        await self._session.delete(order)
        await self._session.commit()
