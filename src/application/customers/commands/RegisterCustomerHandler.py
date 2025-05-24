from src.domain.customers.Customer import Customer
from src.domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from .RegisterCustomerCommand import RegisterCustomerCommand
from src.infrastructure.customers.persistence.CustomerWriteRepository import CustomerWriteRepository
import logging
from uuid import uuid4

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
            id=uuid4(),
            name=command.name,
            email=command.email
        )
        
        # Save customer
        await self._repository.save(customer)
        logger.info(f"Customer saved to write repository: {customer.id}")

        # Dispatch all domain events
        for event in customer.domain_events:
            logger.info("[Command] Dispatching event %s", event.__class__.__name__)
            await self._event_dispatcher.dispatch(event)
        
        # Clear events after dispatching
        customer.clear_domain_events()
        
        return customer
