from datetime import datetime

from domain.core.AggregateRoot import AggregateRoot
from domain.core.value_objects.EntityId import EntityId

from .events.CustomerRegisteredEvent import CustomerRegisteredEvent


class Customer(AggregateRoot):
    def __init__(
        self,
        _id: EntityId,
        name: str,
        email: str,
    ):
        super().__init__()
        self.id = _id
        self.name = name
        self.email = email
        self.created_at = datetime.now()
        self.updated_at = None

    @staticmethod
    def create(name: str, email: str) -> "Customer":
        """Factory method for creating a new customer"""
        _id = EntityId.generate()
        customer = Customer(
            _id=_id,
            name=name,
            email=email,
        )

        # Add domain event when customer is created
        customer.add_domain_event(
            CustomerRegisteredEvent(aggregate_id=str(_id), name=name, email=email)
        )

        return customer
