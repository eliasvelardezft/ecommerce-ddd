from abc import ABC, abstractmethod
from typing import List, Optional

from domain.products.dtos.CategoryDetailsDTO import CategoryDetailsDTO

class ICategoryReadRepository(ABC):
    @abstractmethod
    async def get_category(self, category_id: str, recursive: bool = False) -> Optional[CategoryDetailsDTO]:
        """Retrieves category details by its ID.
        If recursive is True, attempts to load all descendant children.
        Otherwise, may load direct children or none, depending on implementation.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_categories(self) -> List[CategoryDetailsDTO]:
        """Lists all categories."""
        raise NotImplementedError

    @abstractmethod
    async def list_children(self, parent_category_id: str) -> List[CategoryDetailsDTO]:
        """Lists direct children of a given parent category."""
        raise NotImplementedError

    @abstractmethod
    async def list_top_level(self) -> List[CategoryDetailsDTO]:
        """Lists all top-level categories (those without a parent)."""
        raise NotImplementedError
    
    @abstractmethod
    async def update_read_model(self, category_dto: CategoryDetailsDTO) -> None:
        """Updates the category read model, typically used by event handlers."""
        raise NotImplementedError
