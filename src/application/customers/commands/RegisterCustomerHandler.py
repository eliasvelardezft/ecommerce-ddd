import logging

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.customers.Customer import Customer
from infrastructure.customers.persistence.CustomerWriteRepository import (
    CustomerWriteRepository,
)

from .RegisterCustomerCommand import RegisterCustomerCommand

logger = logging.getLogger(__name__)


class RegisterCustomerHandler:
    def __init__(
        self,
        write_repository: CustomerWriteRepository,
        event_dispatcher: DomainEventDispatcher
    ):
        self._repository = write_repository
        self._event_dispatcher = event_dispatcher

    async def handle(self, command: RegisterCustomerCommand) -> Customer:
        logger.info("[Command] Processing RegisterCustomerCommand for %s", command.email)

        # Create customer using factory method
        customer = Customer.create(
            name=command.name,
            email=command.email
        )

        # Save customer
        await self._repository.save(customer)
        logger.info(f"Customer saved to write repository: {customer.id}")

        # Dispatch all domain events using the new method
        await self._event_dispatcher.dispatch_events(customer.domain_events)
        logger.info(f"[Command] Dispatched {len(customer.domain_events)} domain events for customer {customer.id}")

        # Clear events after dispatching
        customer.clear_domain_events()

        return customer
