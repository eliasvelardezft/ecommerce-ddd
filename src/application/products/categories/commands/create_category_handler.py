import logging
from uuid import UUID

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.products.models.Category import Category
from domain.products.repositories.ICategoryWriteRepository import ICategoryWriteRepository
from domain.products.repositories.ICategoryReadRepository import ICategoryReadRepository
from .CreateCategoryCommand import CreateCategoryCommand

logger = logging.getLogger(__name__)

class CreateCategoryHandler:
    def __init__(
        self,
        category_write_repository: ICategoryWriteRepository,
        category_read_repository: ICategoryReadRepository,
        domain_event_dispatcher: DomainEventDispatcher
    ):
        self._category_write_repository = category_write_repository
        self._category_read_repository = category_read_repository
        self._domain_event_dispatcher = domain_event_dispatcher

    async def handle(self, command: CreateCategoryCommand) -> UUID:
        logger.info(f"Handling CreateCategoryCommand for category name: {command.name}")

        # 1. Validate parent_category_id if provided
        if command.parent_category_id:
            parent_category = await self._category_read_repository.get_category(command.parent_category_id)
            if not parent_category:
                logger.error(f"Parent category with ID {command.parent_category_id} not found.")
                raise ValueError(f"Parent category with ID {command.parent_category_id} not found.")

        # 2. Create Category aggregate
        # Category.create handles initial event creation (CategoryCreatedEvent)
        category = Category.create(
            name=command.name,
            description=command.description, # Domain model handles Optional description
            parent_category_id=command.parent_category_id
        )

        # 3. Persist the aggregate
        await self._category_write_repository.save(category)
        logger.info(f"Category {category.id} created successfully with name {category.name}.")

        # 4. Dispatch domain events
        await self._domain_event_dispatcher.dispatch_events(category.domain_events)
        logger.info(f"Dispatched {len(category.domain_events)} domain events for category {category.id}.")
        category.clear_domain_events()

        return category.id 