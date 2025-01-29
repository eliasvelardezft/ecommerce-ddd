from typing import List, Optional
from src.domain.customers.dtos.CustomerProfileDTO import CustomerProfileDTO
from src.domain.customers.repositories.ICustomerReadRepository import ICustomerReadRepository
import logging

logger = logging.getLogger(__name__)

class CustomerReadRepository(ICustomerReadRepository):
    """Repository for read operations (queries) on Customer data"""

    def __init__(self):
        self._customer_views = []  # In-memory storage of read models
        logger.info("Initialized CustomerReadRepository")

    async def get_customer_profile(self, email: str) -> Optional[CustomerProfileDTO]:
        """Get customer profile by email"""
        logger.info("[Read] Fetching profile for: %s", email)
        customer = next(
            (c for c in self._customer_views if c.email == email),
            None
        )

        if not customer:
            logger.info("[Read] Profile not found for: %s", email)
            return None
            
        logger.info(f"Customer profile found for email: {email}")
        return CustomerProfileDTO(
            id=str(customer.id),
            name=customer.name,
            email=customer.email,
            created_at=customer.created_at,
            total_orders=0,  # In a real app, would be calculated
            last_order_date=None,
            favorite_products=[],  # In a real app, would be calculated
            loyalty_tier="NEW"  # In a real app, would be calculated
        )

    async def get_all_profiles(self) -> List[CustomerProfileDTO]:
        """Get all customer profiles"""
        return [
            CustomerProfileDTO(
                id=str(c.id),
                name=c.name,
                email=c.email,
                created_at=c.created_at,
                total_orders=0,
                last_order_date=None,
                favorite_products=[],
                loyalty_tier="NEW"
            )
            for c in self._customer_views
        ]

    async def update_read_model(self, customer: CustomerProfileDTO) -> None:
        """
        Update the read model when changes occur
        This would be called by event handlers
        """
        logger.info("[Read] Current views before update: %s", 
                   [c.email for c in self._customer_views])
        
        existing = next(
            (c for c in self._customer_views if c.id == customer.id),
            None
        )
        
        if existing:
            self._customer_views.remove(existing)
        self._customer_views.append(customer)
        
        logger.info("[Read] Current views after update: %s", 
                   [c.email for c in self._customer_views])
