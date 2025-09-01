import logging

from domain.customers.repositories.ICustomerReadRepository import (
    ICustomerReadRepository,
)
from integration_contracts.events.order.order_placed import (
    OrderPlacedEventContractV1,
)

logger = logging.getLogger(__name__)


class UpdateCustomerOnOrderPlaced:
    """
    Integration event handler.
    Reacts to the public OrderPlacedEventContractV1.
    Updates customer information based on an order placement.
    (Example: increment order count, update last order date)
    """
    def __init__(self, customer_read_repository: ICustomerReadRepository):
        self._customer_read_repository = customer_read_repository
        logger.info(f"[UpdateCustomerOnOrderPlaced] Initialized.")

    async def handle(self, event: OrderPlacedEventContractV1) -> None:
        # This handler now consumes a public Integration Event Contract (Pydantic model)
        logger.info(
            f"[UpdateCustomerOnOrderPlaced] Received OrderPlacedEventContractV1 for order ID: {event.order_id}, "
            f"customer ID: {event.customer_id}"
        )
        
        try:
            # Access data using Pydantic model attributes
            customer_id = event.customer_id
            
            # Fetch the customer - using read repo as this handler typically updates a read model
            # or performs actions that don't belong in the customer aggregate's transactional boundary.
            customer = await self._customer_read_repository.get_customer_profile_by_id(customer_id) # Assuming find_by_id
            
            if customer:
                logger.info(f"[UpdateCustomerOnOrderPlaced] Updating customer {customer_id} based on order {event.order_id}.")
                # Example: Increment order count or update last order date.
                # This is a placeholder for actual logic.
                # For a read model, you might directly update a document.
                customer.total_orders += 1
                customer.last_order_date = event.occurred_on
                await self._customer_read_repository.update_read_model(customer) # Or save, depending on repo

            else:
                logger.warning(f"[UpdateCustomerOnOrderPlaced] Customer with ID {customer_id} not found. Cannot update.")
        except Exception as e:
            logger.error(
                f"[UpdateCustomerOnOrderPlaced] Error processing OrderPlacedEventContractV1 for order ID {event.order_id}: {e}",
                exc_info=True
            )
