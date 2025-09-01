from decimal import Decimal

from pydantic import BaseModel, Field

from domain.orders.value_objects.ShippingDetails import ShippingDetails


class OrderItemRequest(BaseModel):
    """DTO for order item requests from API"""
    product_id: str
    product_name: str
    quantity: int = Field(..., gt=0)
    unit_price: dict  # {"amount": Decimal, "currency": str}


class PlaceOrderCommand(BaseModel):
    customer_id: str
    items: list[OrderItemRequest]
    shipping_details: ShippingDetails
    currency: str = Field(default="USD", max_length=3)
    shipping_cost_raw: Decimal | None = Field(default=None, ge=0)
    tax_amount_raw: Decimal | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=1000)
