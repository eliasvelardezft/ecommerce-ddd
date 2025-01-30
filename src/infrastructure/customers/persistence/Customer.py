from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from uuid import UUID
from src.infrastructure.core.persistence.base import BaseModel

class CustomerSQL(BaseModel):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
