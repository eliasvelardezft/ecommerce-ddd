from sqlalchemy import ForeignKey, Enum as SQLEnum, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.core.persistence.base import BaseModel
from domain.orders.models.OrderStatus import OrderStatus


class OrderSQL(BaseModel):
    """SQL Model for Order aggregate"""
    __tablename__ = "orders"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus))
    items: Mapped[list["OrderItemSQL"]] = relationship(
        "OrderItemSQL",
        cascade="all, delete-orphan",
        lazy="joined"
    )

class OrderItemSQL(BaseModel):
    """SQL Model for Order Items"""
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"))
    product_id: Mapped[str] = mapped_column(String(36))
    quantity: Mapped[int]
    unit_price: Mapped[float]
