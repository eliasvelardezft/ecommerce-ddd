from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from typing import List, Optional

from infrastructure.core.persistence.base import BaseModel

class CategorySQL(BaseModel):
    id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_category_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("category.id"), nullable=True, index=True) # Table name is singular due to auto-generation

    parent = relationship("CategorySQL", remote_side=[id], back_populates="children", lazy="joined")
    children = relationship("CategorySQL", back_populates="parent", cascade="all, delete-orphan", lazy="joined")

    products: Mapped[List["ProductSQL"]] = relationship(back_populates="category")
