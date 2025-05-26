import logging
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.orders.models.Order import Order
from domain.orders.models.Order import OrderItem
from domain.orders.repositories.IOrderWriteRepository import IOrderWriteRepository
from .Order import OrderSQL, OrderItemSQL


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
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
        # Convert domain items to SQL models
        db_order.items = [
            OrderItemSQL(
                id=uuid4(),  # Generate new ID for each item
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            for item in order.items
        ]
        
        # Merge or add the order
        db_order = await self._session.merge(db_order)
        await self._session.commit()
        
        return order

    async def get_by_id(self, id: UUID) -> Optional[Order]:
        """Retrieve an order by ID"""
        result = await self._session.execute(
            select(OrderSQL).where(OrderSQL.id == id)
        )
        db_order = result.scalar_one_or_none()
        
        if not db_order:
            return None
            
        # Convert SQL model back to domain entity
        order_items = [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            for item in db_order.items
        ]
        
        return Order(
            id=db_order.id,
            customer_id=db_order.customer_id,
            items=order_items,
            status=db_order.status,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at
        )
