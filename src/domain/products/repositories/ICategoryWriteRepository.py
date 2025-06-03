from abc import ABC, abstractmethod
from uuid import UUID

from domain.products.models.Category import Category

class ICategoryWriteRepository(ABC):
    @abstractmethod
    async def save(self, category: Category) -> None:
        """Persists a new category or updates an existing one."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Category | None:
        """Retrieves a category by its ID, needed for updates."""
        raise NotImplementedError
