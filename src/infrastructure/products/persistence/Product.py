from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.core.persistence.base import BaseModel


class ProductSQL(BaseModel):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)

    price_amount: Mapped[float] = mapped_column(Numeric(10, 2)) # Stored as Numeric, handled as Decimal in domain
    price_currency: Mapped[str] = mapped_column(String(3))

    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id"), index=True)
    category: Mapped["CategorySQL"] = relationship(back_populates="products", lazy="joined")

    image_url_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    image_alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    attributes: Mapped[list["AttributeSQL"]] = relationship(
        "AttributeSQL",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="joined"
    )

class AttributeSQL(BaseModel):
    __tablename__ = "product_attributes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    product: Mapped[ProductSQL] = relationship(back_populates="attributes")

    __table_args__ = (UniqueConstraint('product_id', 'name', name='_product_attribute_uc'),)
