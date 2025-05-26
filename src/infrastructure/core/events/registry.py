import logging
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from infrastructure.core.events.integration_event_dispatcher import IntegrationEventDispatcher

# Import internal domain events
from domain.customers.events.CustomerRegisteredEvent import CustomerRegisteredEvent as InternalCustomerRegisteredEvent
from domain.orders.events.OrderPlacedEvent import OrderPlacedEvent as InternalOrderPlacedEvent

# Import public event contracts
from integration_contracts.events.order.order_placed import OrderPlacedEventContractV1
# from integration_contracts.events.customer_events import CustomerRegisteredEventContractV1 # Example for future use

# Import internal handlers (same-BC)
from domain.customers.events.handlers.customer_registered_handlers import (
    UpdateReadModelOnCustomerRegisteredEvent as CustomerUpdateReadModelHandler,
    SendWelcomeEmailOnCustomerRegisteredEvent as CustomerSendWelcomeEmailHandler,
    AuditNewCustomerOnCustomerRegisteredEvent
)
from domain.orders.events.handlers.OrderPlacedHandlers import (
    UpdateReadModelHandler as OrderUpdateReadModelHandler
)

# Import integration handlers (cross-BC, listen to public contracts)
from domain.customers.events.handlers.integration.OrderPlacedHandlers import (
    UpdateCustomerOnOrderPlacedHandler # Renamed for clarity and to expect a contract
)


logger = logging.getLogger(__name__)

def register_customer_event_handlers(
    domain_event_dispatcher: DomainEventDispatcher,
    integration_event_dispatcher: IntegrationEventDispatcher, # Added
    container: dict # Assuming container is a dict for simplicity
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
        InternalCustomerRegisteredEvent,
        CustomerUpdateReadModelHandler(customer_read_repo)
    )
    domain_event_dispatcher.register_handler(
        InternalCustomerRegisteredEvent,
        CustomerSendWelcomeEmailHandler(email_service)
    )
    domain_event_dispatcher.register_handler(
        InternalCustomerRegisteredEvent,
        AuditNewCustomerOnCustomerRegisteredEvent(audit_service)
    )
    logger.info("[Registry] Internal Customer event handlers registered with DomainEventDispatcher.")

    # 2. Register handlers for PUBLIC INTEGRATION event contracts consumed by Customer domain
    # These handlers are within the Customer BC but react to public events from OTHER BCs (e.g., Orders).
    # The handler 'UpdateCustomerOnOrderPlacedHandler' now expects 'OrderPlacedEventContractV1'.
    integration_event_dispatcher.register_handler(
        OrderPlacedEventContractV1, # Subscribes to the public contract
        UpdateCustomerOnOrderPlacedHandler(customer_read_repo) # This handler must be updated to expect the contract
    )
    logger.info("[Registry] Integration event handlers for Customer domain registered with IntegrationEventDispatcher.")


def register_order_event_handlers(
    domain_event_dispatcher: DomainEventDispatcher,
    integration_event_dispatcher: IntegrationEventDispatcher, # Added for consistency and future use
    container: dict
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
        InternalOrderPlacedEvent,
        OrderUpdateReadModelHandler(order_read_repo)
    )
    logger.info("[Registry] Internal Order event handlers registered with DomainEventDispatcher.")

    # 2. (Example) Register handlers for PUBLIC INTEGRATION event contracts consumed by Order domain
    # If Order domain needed to react to an external event (e.g., CustomerVerificationCompletedContractV1),
    # it would be registered here with the integration_event_dispatcher.
    # Example:
    # from integration_contracts.events.customer_events import CustomerVerificationCompletedContractV1
    # from domain.orders.events.handlers.integration.CustomerVerificationHandlers import UpdateOrderOnCustomerVerifiedHandler
    #
    # if integration_event_dispatcher: # Ensure it's provided
    #     integration_event_dispatcher.register_handler(
    #         CustomerVerificationCompletedContractV1,
    #         UpdateOrderOnCustomerVerifiedHandler(container.get("some_order_dependency"))
    #     )
    #     logger.info("[Registry] Integration event handlers for Order domain registered with IntegrationEventDispatcher (if any).")
