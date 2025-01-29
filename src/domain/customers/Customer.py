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
        created_at: datetime,
        updated_at: datetime
    ):
        super().__init__()
        self.id = id
        self.name = name
        self.email = email
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def create(id: UUID, name: str, email: str) -> 'Customer':
        """Factory method for creating a new customer"""
        now = datetime.now()
        customer = Customer(
            id=id,
            name=name,
            email=email,
            created_at=now,
            updated_at=now
        )
        
        # Add domain event when customer is created
        customer.add_domain_event(CustomerRegisteredEvent(
            aggregate_id=str(id),
            name=name,
            email=email
        ))
        
        return customer
