from datetime import datetime
from typing import Optional, Dict, Any

from domain.core.AggregateRoot import AggregateRoot
from domain.core.value_objects.EntityId import EntityId
from domain.products.events.CategoryCreatedEvent import CategoryCreatedEvent
from domain.products.events.CategoryDetailsUpdatedEvent import CategoryDetailsUpdatedEvent
from domain.products.events.CategoryParentChangedEvent import CategoryParentChangedEvent
# from domain.products.exceptions import CategoryDomainException # Placeholder for future custom exceptions

class Category(AggregateRoot):
    id: EntityId
    name: str
    description: Optional[str]
    parent_category_id: Optional[EntityId]
    created_at: datetime
    updated_at: datetime

    def __init__(
        self,
        _id: EntityId,
        name: str,
        description: Optional[str] = None,
        parent_category_id: Optional[EntityId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__()
        self.id = _id
        self.name = name
        self.description = description
        self.parent_category_id = parent_category_id
        
        current_time = datetime.now()
        self.created_at = created_at if created_at is not None else current_time
        self.updated_at = updated_at if updated_at is not None else self.created_at

        if not name:
            raise ValueError("Category name cannot be empty.")
        if parent_category_id == self.id:
            raise ValueError("A category cannot be its own parent.")

    @classmethod
    def create(
        cls,
        name: str,
        description: Optional[str] = None,
        parent_category_id: Optional[EntityId] = None,
    ) -> 'Category':
        _id = EntityId.generate()
        if parent_category_id == _id: # Should not happen with uuid4 but as a safeguard
            raise ValueError("A category cannot be its own parent during creation.")

        category = cls(
            _id=_id,
            name=name,
            description=description,
            parent_category_id=parent_category_id
        )
        category.add_domain_event(CategoryCreatedEvent(
            aggregate_id=category.id,
            name=category.name,
            description=category.description,
            parent_category_id=category.parent_category_id,
            created_at=category.created_at
        ))
        return category

    def update_details(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        changes: Dict[str, Any] = {}
        if name is not None and self.name != name:
            if not name.strip():
                raise ValueError("Category name cannot be empty when updating.") # Replace with CategoryDomainException
            self.name = name
            changes["name"] = name
        
        if description is not None:
            if self.description != description:
                 self.description = description
                 changes["description"] = description
        elif description is None and self.description is not None: # If None is passed to clear existing description
            self.description = None
            changes["description"] = None
            
        if changes:
            self.updated_at = datetime.now()
            self.add_domain_event(CategoryDetailsUpdatedEvent(
                aggregate_id=self.id,
                updated_details=changes,
                updated_at=self.updated_at
            ))

    def change_parent(
        self, 
        new_parent_category_id: Optional[EntityId]
    ) -> None:
        if self.parent_category_id == new_parent_category_id:
            return

        if new_parent_category_id == self.id:
            raise ValueError("A category cannot be its own parent.") # Replace with CategoryDomainException

        prev_parent_id = self.parent_category_id
        self.parent_category_id = new_parent_category_id
        self.updated_at = datetime.now()
        self.add_domain_event(CategoryParentChangedEvent(
            aggregate_id=self.id,
            new_parent_category_id=self.parent_category_id,
            prev_parent_category_id=prev_parent_id,
            updated_at=self.updated_at
        ))
