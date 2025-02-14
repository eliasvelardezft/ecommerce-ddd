from enum import Enum


class OrderStatus(Enum):
    """
        DRAFT: the order can be modified
        PROCESSING: the order is processing a payment and cannot be modified
        CANCELLED: the order has been cancelled
        COMPLETED: the order has been completed
    """
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
