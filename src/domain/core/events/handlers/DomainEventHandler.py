from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from ..DomainEvent import DomainEvent

TEvent = TypeVar('TEvent', bound=DomainEvent)

class DomainEventHandler(Generic[TEvent], ABC):
    """
    Abstract base class for domain event handlers.
    TEvent specifies which specific DomainEvent type this handler can process.
    """
    
    @abstractmethod
    async def handle(self, event: TEvent) -> None:
        """Handle the domain event"""
        pass 