from typing import List, Optional

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.core.persistence.base import BaseModel


class CategorySQL(BaseModel):
    __tablename__ = "categories"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_category_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("categories.id"), nullable=True, index=True)

    parent = relationship("CategorySQL", remote_side=[id], back_populates="children", lazy="joined")
    children = relationship("CategorySQL", back_populates="parent", cascade="all, delete-orphan", lazy="joined")

    products: Mapped[list["ProductSQL"]] = relationship(back_populates="category")
