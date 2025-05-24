def register_customer_event_handlers(dispatcher, container):
    """Register all handlers that modify the CUSTOMER domain"""
    from src.domain.customers.events.CustomerRegisteredEvent import CustomerRegisteredEvent
    from src.domain.orders.events.OrderPlacedEvent import OrderPlacedEvent
    from src.domain.customers.events.handlers.CustomerRegisteredHandlers import (
        UpdateReadModelHandler, 
        SendWelcomeEmailHandler,
        AuditNewCustomerHandler
    )
    from src.domain.customers.events.handlers.integration.OrderPlacedHandlers import UpdateCustomerHandler
    
    # Get dependencies
    customer_repo = container.get("customer_read_repository")
    email_service = container.get("email_service")
    audit_service = container.get("audit_service")
    
    # Register handlers for internal events
    dispatcher.register_handler(
        CustomerRegisteredEvent,
        UpdateReadModelHandler(customer_repo)
    )
    dispatcher.register_handler(
        CustomerRegisteredEvent,
        SendWelcomeEmailHandler(email_service)
    )
    dispatcher.register_handler(
        CustomerRegisteredEvent,
        AuditNewCustomerHandler(audit_service)
    )
    
    # Register handlers for external events that affect customers
    dispatcher.register_handler(
        OrderPlacedEvent,
        UpdateCustomerHandler(customer_repo)
    )

def register_order_event_handlers(dispatcher, container):
    """Register all handlers that modify the ORDER domain"""
    from src.domain.orders.events.OrderPlacedEvent import OrderPlacedEvent
    from src.domain.orders.events.handlers.OrderPlacedHandlers import UpdateReadModelHandler as OrderUpdateHandler
    
    # Get dependencies
    order_repo = container.get("order_read_repository")
    
    # Register handlers
    dispatcher.register_handler(
        OrderPlacedEvent,
        OrderUpdateHandler(order_repo)
    )
