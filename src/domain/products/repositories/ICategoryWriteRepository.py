from abc import ABC, abstractmethod

from domain.core.value_objects.EntityId import EntityId
from domain.products.models.Category import Category


class ICategoryWriteRepository(ABC):
    @abstractmethod
    async def save(self, category: Category) -> None:
        """Persists a category, creating it if new or updating if existing."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, category_id: EntityId) -> Category | None:
        """Retrieves a category by its ID, potentially for updates or checks."""
        raise NotImplementedError
