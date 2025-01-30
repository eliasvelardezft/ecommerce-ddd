import re
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import Column, DateTime, event, inspect
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, sessionmaker

from src.infrastructure.core.settings import settings

def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        # Remove the 'SQL' suffix from the class name
        class_name = cls.__name__[:-3]
        return camel_to_snake(class_name)

    def as_dict(self):
        return {
            column.key: getattr(self, column.key)
            for column in inspect(self).mapper.column_attrs
        }

class BaseModel(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True), 
        default=datetime.now()
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=datetime.now(),
        onupdate=datetime.now(),
    )
    deleted_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        index=True,
        nullable=True,
    )

@event.listens_for(BaseModel, "before_update", propagate=True)
def updated_at(mapper, connection, target):
    target.updated_at = datetime.now()
