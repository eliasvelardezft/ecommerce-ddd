import logging

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher

# Import internal domain events
from domain.customers.events.CustomerRegisteredEvent import (
    CustomerRegisteredEvent as InternalCustomerRegisteredEvent,
)
from domain.customers.events.handlers.customer_registered_handlers import (
    AuditNewCustomerOnCustomerRegisteredEvent,
)
from domain.customers.events.handlers.customer_registered_handlers import (
    SendWelcomeEmailOnCustomerRegisteredEvent as CustomerSendWelcomeEmailHandler,
)

# from integration_contracts.events.customer_events import CustomerRegisteredEventContractV1 # Example for future use
# Import internal handlers (same-BC)
from domain.customers.events.handlers.customer_registered_handlers import (
    UpdateReadModelOnCustomerRegisteredEvent as CustomerUpdateReadModelHandler,
)

# Import integration handlers (cross-BC, listen to public contracts)
from domain.customers.events.handlers.integration.order_placed_handlers import (
    UpdateCustomerOnOrderPlaced,  # Renamed for clarity and to expect a contract
)
from domain.orders.events.handlers.order_cancelled_handlers import (
    UpdateOrderOnOrderCancelled,
)
from domain.orders.events.handlers.order_completed_handlers import (
    UpdateOrderOnOrderCompleted,
)
from domain.orders.events.handlers.order_placed_handlers import (
    UpdateOrderOnOrderPlaced as OrderUpdateReadModelHandler,
)

# Added imports for new handlers
from domain.orders.events.handlers.order_processing_handlers import (
    UpdateOrderOnOrderProcessing,
)
from domain.orders.events.OrderCancelledEvent import (
    OrderCancelledEvent as InternalOrderCancelledEvent,
)
from domain.orders.events.OrderCompletedEvent import (
    OrderCompletedEvent as InternalOrderCompletedEvent,
)
from domain.orders.events.OrderPlacedEvent import (
    OrderPlacedEvent as InternalOrderPlacedEvent,
)
from domain.orders.events.OrderProcessingEvent import (
    OrderProcessingEvent as InternalOrderProcessingEvent,
)

# Import internal Category domain events
from domain.products.events.CategoryCreatedEvent import (
    CategoryCreatedEvent as InternalCategoryCreatedEvent,
)
from domain.products.events.CategoryDetailsUpdatedEvent import (
    CategoryDetailsUpdatedEvent as InternalCategoryDetailsUpdatedEvent,
)
from domain.products.events.CategoryParentChangedEvent import (
    CategoryParentChangedEvent as InternalCategoryParentChangedEvent,
)

# Import internal Category handlers
from domain.products.events.handlers.category_created_handlers import (
    UpdateCategoryOnCategoryCreated,
)
from domain.products.events.handlers.category_details_updated_handlers import (
    UpdateCategoryOnCategoryDetailsUpdated,
)
from domain.products.events.handlers.category_parent_changed_handlers import (
    UpdateCategoryOnCategoryParentChanged,
)
from domain.products.events.handlers.product_activated_handlers import (
    UpdateProductOnProductActivated,
)

# Import internal Product handlers
from domain.products.events.handlers.product_created_handlers import (
    UpdateProductOnProductCreated,
)
from domain.products.events.handlers.product_deactivated_handlers import (
    UpdateProductOnProductDeactivated,
)
from domain.products.events.handlers.product_price_updated_handlers import (
    UpdateProductOnProductPriceUpdated,
)
from domain.products.events.handlers.product_stock_updated_handlers import (
    UpdateProductOnProductStockUpdated,
)
from domain.products.events.ProductActivatedEvent import (
    ProductActivatedEvent as InternalProductActivatedEvent,
)

# Import internal Product domain events
from domain.products.events.ProductCreatedEvent import (
    ProductCreatedEvent as InternalProductCreatedEvent,
)
from domain.products.events.ProductDeactivatedEvent import (
    ProductDeactivatedEvent as InternalProductDeactivatedEvent,
)
from domain.products.events.ProductPriceUpdatedEvent import (
    ProductPriceUpdatedEvent as InternalProductPriceUpdatedEvent,
)
from domain.products.events.ProductStockUpdatedEvent import (
    ProductStockUpdatedEvent as InternalProductStockUpdatedEvent,
)
from infrastructure.core.events.integration_event_dispatcher import (
    IntegrationEventDispatcher,
)

# Import public event contracts
from integration_contracts.events.order.order_placed import (
    OrderPlacedEventContractV1,
)

logger = logging.getLogger(__name__)


def register_customer_event_handlers(
    domain_event_dispatcher: DomainEventDispatcher,
    integration_event_dispatcher: IntegrationEventDispatcher,  # Added
    container: dict,  # Assuming container is a dict for simplicity
) -> None:
    """
    Register all event handlers related to the CUSTOMER domain.
    - Internal handlers subscribe to DomainEvents via DomainEventDispatcher.
    - Integration handlers subscribe to public EventContracts via IntegrationEventDispatcher.
    """
    logger.info("[Registry] Registering Customer event handlers...")

    # Get dependencies from container
    customer_read_repo = container.get("customer_read_repository")
    email_service = container.get("email_service")
    audit_service = container.get("audit_service")

    # 1. Register handlers for INTERNAL events originating from Customer domain
    # These handlers are within the Customer BC and react to internal Customer events.
    domain_event_dispatcher.register_handler(
        InternalCustomerRegisteredEvent, CustomerUpdateReadModelHandler(customer_read_repo)
    )
    domain_event_dispatcher.register_handler(
        InternalCustomerRegisteredEvent, CustomerSendWelcomeEmailHandler(email_service)
    )
    domain_event_dispatcher.register_handler(
        InternalCustomerRegisteredEvent, AuditNewCustomerOnCustomerRegisteredEvent(audit_service)
    )
    logger.info(
        "[Registry] Internal Customer event handlers registered with DomainEventDispatcher."
    )

    # 2. Register handlers for PUBLIC INTEGRATION event contracts consumed by Customer domain
    # These handlers are within the Customer BC but react to public events from OTHER BCs (e.g., Orders).
    # The handler 'UpdateCustomerOnOrderPlaced' now expects 'OrderPlacedEventContractV1'.
    integration_event_dispatcher.register_handler(
        OrderPlacedEventContractV1,  # Subscribes to the public contract
        UpdateCustomerOnOrderPlaced(
            customer_read_repo
        ),  # This handler must be updated to expect the contract
    )
    logger.info(
        "[Registry] Integration event handlers for Customer domain registered with IntegrationEventDispatcher."
    )


def register_order_event_handlers(
    domain_event_dispatcher: DomainEventDispatcher,
    integration_event_dispatcher: IntegrationEventDispatcher,  # Added for consistency and future use
    container: dict,
) -> None:
    """
    Register all event handlers related to the ORDER domain.
    - Internal handlers subscribe to DomainEvents via DomainEventDispatcher.
    - Integration handlers (if any) subscribe to public EventContracts via IntegrationEventDispatcher.
    """
    logger.info("[Registry] Registering Order event handlers...")

    # Get dependencies from container
    order_read_repo = container.get("order_read_repository")

    # 1. Register handlers for INTERNAL events originating from Order domain
    domain_event_dispatcher.register_handler(
        InternalOrderPlacedEvent, OrderUpdateReadModelHandler(order_read_repo)
    )

    # Register lifecycle event handlers
    domain_event_dispatcher.register_handler(
        InternalOrderProcessingEvent, UpdateOrderOnOrderProcessing(order_read_repo)
    )

    domain_event_dispatcher.register_handler(
        InternalOrderCompletedEvent, UpdateOrderOnOrderCompleted(order_read_repo)
    )

    domain_event_dispatcher.register_handler(
        InternalOrderCancelledEvent, UpdateOrderOnOrderCancelled(order_read_repo)
    )

    logger.info("[Registry] Internal Order event handlers registered with DomainEventDispatcher.")


def register_product_event_handlers(
    domain_event_dispatcher: DomainEventDispatcher,
    # integration_event_dispatcher: IntegrationEventDispatcher, # If/when products have integration events
    container: dict,
) -> None:
    logger.info("[Registry] Registering Product event handlers...")
    product_read_repo = container.get("product_read_repository")  # Assuming this key

    domain_event_dispatcher.register_handler(
        InternalProductCreatedEvent, UpdateProductOnProductCreated(product_read_repo)
    )
    domain_event_dispatcher.register_handler(
        InternalProductStockUpdatedEvent, UpdateProductOnProductStockUpdated(product_read_repo)
    )
    domain_event_dispatcher.register_handler(
        InternalProductPriceUpdatedEvent, UpdateProductOnProductPriceUpdated(product_read_repo)
    )
    domain_event_dispatcher.register_handler(
        InternalProductActivatedEvent, UpdateProductOnProductActivated(product_read_repo)
    )
    domain_event_dispatcher.register_handler(
        InternalProductDeactivatedEvent, UpdateProductOnProductDeactivated(product_read_repo)
    )
    logger.info("[Registry] Internal Product event handlers registered with DomainEventDispatcher.")


def register_category_event_handlers(
    domain_event_dispatcher: DomainEventDispatcher, container: dict
) -> None:
    logger.info("[Registry] Registering Category event handlers...")
    category_read_repo = container.get("category_read_repository")  # Assuming this key

    domain_event_dispatcher.register_handler(
        InternalCategoryCreatedEvent, UpdateCategoryOnCategoryCreated(category_read_repo)
    )
    domain_event_dispatcher.register_handler(
        InternalCategoryDetailsUpdatedEvent,
        UpdateCategoryOnCategoryDetailsUpdated(category_read_repo),
    )
    domain_event_dispatcher.register_handler(
        InternalCategoryParentChangedEvent,
        UpdateCategoryOnCategoryParentChanged(category_read_repo),
    )
    logger.info(
        "[Registry] Internal Category event handlers registered with DomainEventDispatcher."
    )


def register_all_event_handlers(
    domain_event_dispatcher: DomainEventDispatcher,
    integration_event_dispatcher: IntegrationEventDispatcher,
    container: dict,
) -> None:
    """
    Registers all domain-specific and integration event handlers with their respective dispatchers
    using the functions from the registry.
    """
    logger.info("[Bootstrap] Registering all application event handlers from registry...")

    register_customer_event_handlers(
        domain_event_dispatcher=domain_event_dispatcher,
        integration_event_dispatcher=integration_event_dispatcher,
        container=container,
    )

    register_order_event_handlers(
        domain_event_dispatcher=domain_event_dispatcher,
        integration_event_dispatcher=integration_event_dispatcher,  # Now passed here
        container=container,
    )

    register_product_event_handlers(
        domain_event_dispatcher=domain_event_dispatcher, container=container
    )

    register_category_event_handlers(
        domain_event_dispatcher=domain_event_dispatcher, container=container
    )

    logger.info("[Bootstrap] All application event handlers registered.")
