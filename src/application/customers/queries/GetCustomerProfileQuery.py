from dataclasses import dataclass

@dataclass
class GetCustomerProfileQuery:
    """Query to get a customer's complete profile"""
    email: str 