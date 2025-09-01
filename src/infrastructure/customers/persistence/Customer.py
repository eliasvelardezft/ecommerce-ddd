from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from infrastructure.core.persistence.base import BaseModel

class CustomerSQL(BaseModel):
    __tablename__ = "customers"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
