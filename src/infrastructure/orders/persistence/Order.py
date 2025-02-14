from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import UUID
from datetime import datetime
from src.infrastructure.core.persistence.base import BaseModel
from src.domain.orders.models.OrderStatus import OrderStatus


class OrderSQL(BaseModel):
    """SQL Model for Order aggregate"""
    id: Mapped[UUID] = mapped_column(primary_key=True)
    customer_id: Mapped[UUID] = mapped_column(index=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus))
    items: Mapped[list["OrderItemSQL"]] = relationship(
        "OrderItemSQL",
        cascade="all, delete-orphan",
        lazy="joined"
    )

class OrderItemSQL(BaseModel):
    """SQL Model for Order Items"""
    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey("order.id"))
    product_id: Mapped[UUID]
    quantity: Mapped[int]
    unit_price: Mapped[float]
