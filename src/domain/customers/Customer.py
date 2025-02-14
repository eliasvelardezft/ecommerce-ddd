from uuid import UUID
from datetime import datetime
from src.domain.core.AggregateRoot import AggregateRoot
from .events.CustomerRegisteredEvent import CustomerRegisteredEvent

class Customer(AggregateRoot):
    def __init__(
        self,
        id: UUID,
        name: str,
        email: str,
    ):
        super().__init__()
        self.id = id
        self.name = name
        self.email = email
        self.created_at = datetime.now()
        self.updated_at = None

    @staticmethod
    def create(id: UUID, name: str, email: str) -> 'Customer':
        """Factory method for creating a new customer"""
        customer = Customer(
            id=id,
            name=name,
            email=email,
        )
        
        # Add domain event when customer is created
        customer.add_domain_event(CustomerRegisteredEvent(
            aggregate_id=str(id),
            name=name,
            email=email
        ))
        
        return customer
