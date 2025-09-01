import random
import string
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from domain.core.AggregateRoot import AggregateRoot
from domain.core.value_objects.EntityId import EntityId
from domain.core.value_objects.Money import Money  # Core Money VO
from domain.orders.events.OrderCancelledEvent import OrderCancelledEvent
from domain.orders.events.OrderCompletedEvent import OrderCompletedEvent
from domain.orders.events.OrderPlacedEvent import OrderPlacedEvent
from domain.orders.events.OrderProcessingEvent import OrderProcessingEvent
from domain.orders.exceptions import OrderValidationException
from domain.orders.models.OrderItem import OrderItem
from domain.orders.models.OrderStatus import OrderStatus
from domain.orders.value_objects.ShippingDetails import ShippingDetails


class Order(AggregateRoot):
    id: EntityId
    customer_id: EntityId
    order_number: str
    items: List[OrderItem]
    shipping_details: ShippingDetails
    currency: str # e.g., "USD", "EUR"
    shipping_cost: Money
    tax_amount: Money
    notes: Optional[str]
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]
    tracking_number: Optional[str] = None

    @staticmethod
    def _generate_order_number(length: int = 10) -> str:
        """Generates a unique, human-readable order number, e.g., ORD-A1B2C3D4."""
        prefix = "ORD-"
        # Generate random alphanumeric characters (uppercase and digits)
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choice(chars) for _ in range(length - len(prefix)))
        return f"{prefix}{random_part}"

    def __init__(
        self,
        _id: EntityId,
        customer_id: EntityId,
        items: List[OrderItem], # List of Pydantic OrderItem models
        shipping_details: ShippingDetails,
        currency: str = "USD",
        order_number: Optional[str] = None,
        shipping_cost_raw: Optional[Decimal] = None,
        tax_amount_raw: Optional[Decimal] = None,
        notes: Optional[str] = None,
        status: OrderStatus = OrderStatus.DRAFT,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        tracking_number: Optional[str] = None,
    ):
        super().__init__()
        self.id = _id
        self.customer_id = customer_id
        
        if not currency or len(currency) != 3:
            raise OrderValidationException("Order currency must be a 3-letter code.")
        self.currency = currency.upper()

        self.order_number = order_number if order_number else Order._generate_order_number()
        self.shipping_details = shipping_details
        self.notes = notes
        self.status = status # Initial status
        self.created_at = created_at if created_at else datetime.now(timezone.utc)
        self.updated_at = updated_at
        self.tracking_number = tracking_number

        # Initialize Money fields with the order's currency
        self.shipping_cost = Money(shipping_cost_raw if shipping_cost_raw is not None else Decimal(0), self.currency)
        self.tax_amount = Money(tax_amount_raw if tax_amount_raw is not None else Decimal(0), self.currency)
        
        self.items = [] # Initialize before validating and adding
        if not items: # Check after self.currency is set, as add_item might need it for Money.zero()
            raise OrderValidationException("Order must have at least one item upon creation.")
        for item_to_add in items:
            self.add_item(item_to_add, dispatch_event=False) # Use add_item to ensure consistency

        self._validate_order_state() # General validation for the order state after all setup

    def _validate_item_currency(self, item: OrderItem):
        if item.unit_price.currency != self.currency:
            raise OrderValidationException(
                f"Item '{item.product_name}' (ID: {item.id}) unit price currency ({item.unit_price.currency}) "
                f"does not match order currency ({self.currency})."
            )
        # No discount_amount to validate in item anymore

    def _validate_order_state(self):
        """Validates overall order consistency. Called after init or major modifications."""
        if self.shipping_cost.currency != self.currency:
            raise OrderValidationException(f"Shipping cost currency ({self.shipping_cost.currency}) must match order currency ({self.currency}).")
        if self.tax_amount.currency != self.currency:
            raise OrderValidationException(f"Tax amount currency ({self.tax_amount.currency}) must match order currency ({self.currency}).")
        if not self.items: # This check might be redundant if __init__ enforces it.
            raise OrderValidationException("Order must contain at least one item.")
        for item_in_order in self.items:
            self._validate_item_currency(item_in_order)

    def add_item(self, item_to_add: OrderItem, dispatch_event: bool = True):
        """Adds an item to the order. Validates currency against order currency."""
        if self.status != OrderStatus.DRAFT:
            raise OrderValidationException("Cannot add items to an order that is not in DRAFT status.")
        
        self._validate_item_currency(item_to_add) # Ensure item currency is consistent with order currency
        
        # Check if item with same product_id already exists, if so, consider updating quantity (optional rule)
        # For now, allowing duplicate product_ids as separate line items if their UUIDs are different.
        self.items.append(item_to_add)
        self.updated_at = datetime.now(timezone.utc)
        
        # Placeholder for event dispatching
        # if dispatch_event:
        #     self.add_domain_event(OrderItemAddedEvent(aggregate_id=self.id, item_id=item_to_add.id, ...))

    @property
    def subtotal_amount(self) -> Money:
        """Calculates the total amount for all items before shipping and taxes."""
        current_subtotal = Money(Decimal(0), self.currency)
        for item_in_list in self.items:
            current_subtotal += item_in_list.subtotal
        return current_subtotal

    @property
    def total_amount(self) -> Money:
        """Calculates the final total amount for the order."""
        return self.subtotal_amount + self.shipping_cost + self.tax_amount

    @classmethod
    def create(
        cls,
        customer_id: EntityId,
        items_data: List[dict], # Expect list of dicts for OrderItems
        shipping_details_data: dict, # Expect dict for ShippingDetails
        currency: str = "USD",
        order_id: Optional[EntityId] = None,
        order_number_override: Optional[str] = None, # Allow overriding generated number if needed
        shipping_cost_raw: Optional[Decimal] = None, # Renamed
        tax_amount_raw: Optional[Decimal] = None,    # Renamed
        notes: Optional[str] = None,
    ) -> "Order":
        """Factory method to create a new Order from raw data and raise OrderPlacedEvent."""
        instance_id = order_id if order_id else EntityId.generate()
        order_currency = currency.upper()

        shipping_details_obj = ShippingDetails(**shipping_details_data)
        
        processed_order_items = []
        if not items_data:
            raise OrderValidationException("Cannot create an order with no items data.")

        for item_dict in items_data:
            # Ensure unit_price data is present and has amount/currency
            unit_price_data = item_dict.get('unit_price')
            if not isinstance(unit_price_data, dict) or 'amount' not in unit_price_data or 'currency' not in unit_price_data:
                raise OrderValidationException(f"Missing or invalid unit_price data for item: {item_dict.get('product_name', 'N/A')}")

            item_unit_price = Money(unit_price_data['amount'], unit_price_data['currency'])
            
            if item_unit_price.currency != order_currency:
                 raise OrderValidationException(
                    f"Item '{item_dict.get('product_name', 'N/A')}' unit price currency ({item_unit_price.currency}) "
                    f"does not match order currency ({order_currency})."
                )
            
            processed_order_items.append(OrderItem(
                product_id=EntityId.from_string(item_dict['product_id']),
                product_name=item_dict['product_name'],
                quantity=item_dict['quantity'],
                unit_price=item_unit_price,
                # id will be auto-generated by OrderItem Pydantic model
            ))

        order = cls(
            _id=instance_id,
            customer_id=customer_id,
            items=processed_order_items,
            shipping_details=shipping_details_obj,
            currency=order_currency,
            order_number=order_number_override, # Allows passing specific order_number, else __init__ generates
            shipping_cost_raw=shipping_cost_raw,
            tax_amount_raw=tax_amount_raw,
            notes=notes,
        )

        # Prepare items_data for the event, ensuring Money objects are dicts
        event_items_data = []
        for oi in order.items:
            item_dump = oi.model_dump() # OrderItem is Pydantic
            if 'unit_price' in item_dump and hasattr(oi.unit_price, 'to_dict'):
                item_dump['unit_price'] = oi.unit_price.to_dict()
            event_items_data.append(item_dump)

        order.add_domain_event(
            OrderPlacedEvent(
                aggregate_id=order.id,
                customer_id=order.customer_id,
                order_number=order.order_number,
                items_data=event_items_data, # Use the processed list
                amount=order.total_amount,
                shipping_details_data=order.shipping_details.model_dump(), # ShippingDetails is Pydantic
                status=order.status.value
            )
        )
        return order

    def remove_item(self, item_id: EntityId, dispatch_event: bool = True):
        if self.status != OrderStatus.DRAFT:
            raise OrderValidationException("Cannot remove items from an order that is not in DRAFT status.")
        original_item_count = len(self.items)
        self.items = [it for it in self.items if it.id != item_id]
        if len(self.items) == original_item_count:
            raise OrderValidationException(f"Item with ID {item_id} not found in order.")
        if not self.items:
             raise OrderValidationException("Order must have at least one item after removal.")
        self.updated_at = datetime.now(timezone.utc)
        # if dispatch_event: self.add_domain_event(OrderItemRemovedEvent(aggregate_id=self.id, item_id=item_id))

    def update_item_quantity(self, item_id: EntityId, new_quantity: int, dispatch_event: bool = True):
        if self.status != OrderStatus.DRAFT:
            raise OrderValidationException("Cannot update item quantity for an order not in DRAFT status.")
        if new_quantity <= 0:
            raise OrderValidationException("Item quantity must be positive.")
        
        item_to_update = next((it for it in self.items if it.id == item_id), None)
        if not item_to_update:
            raise OrderValidationException(f"Item with ID {item_id} not found to update quantity.")
        
        item_to_update.quantity = new_quantity # OrderItem is Pydantic, quantity is assignable
        self.updated_at = datetime.now(timezone.utc)
        # if dispatch_event: self.add_domain_event(OrderItemQuantityUpdatedEvent(...))

    def update_shipping_details(self, shipping_details: ShippingDetails, dispatch_event: bool = True):
        if self.status != OrderStatus.DRAFT:
            raise OrderValidationException("Cannot update shipping details for an order not in DRAFT status.")
        self.shipping_details = shipping_details
        self.updated_at = datetime.now(timezone.utc)
        # if dispatch_event: self.add_domain_event(OrderShippingDetailsUpdatedEvent(...))

    def update_shipping_cost(self, new_shipping_cost: Money, dispatch_event: bool = True):
        if self.status != OrderStatus.DRAFT:
            raise OrderValidationException("Cannot update shipping cost for an order not in DRAFT status.")
        if new_shipping_cost.currency != self.currency:
            raise OrderValidationException(f"Shipping cost currency ({new_shipping_cost.currency}) must match order currency ({self.currency}).")
        self.shipping_cost = new_shipping_cost
        self.updated_at = datetime.now(timezone.utc)
        # if dispatch_event: self.add_domain_event(OrderShippingCostUpdatedEvent(...))

    def update_tax_amount(self, new_tax_amount: Money, dispatch_event: bool = True):
        if self.status != OrderStatus.DRAFT:
            raise OrderValidationException("Cannot update tax amount for an order not in DRAFT status.")
        if new_tax_amount.currency != self.currency:
            raise OrderValidationException(f"Tax amount currency ({new_tax_amount.currency}) must match order currency ({self.currency}).")
        self.tax_amount = new_tax_amount
        self.updated_at = datetime.now(timezone.utc)
        # if dispatch_event: self.add_domain_event(OrderTaxAmountUpdatedEvent(...))

    def process_order(self): # Renamed from original 'processing'
        if self.status != OrderStatus.DRAFT:
            raise OrderValidationException(f"Can only process DRAFT orders. Current status: {self.status.value}")
        self.status = OrderStatus.PROCESSING
        self.updated_at = datetime.now(timezone.utc)
        self.add_domain_event(OrderProcessingEvent(
            aggregate_id=self.id,
            order_number=self.order_number,
            customer_id=self.customer_id,
            status=self.status.value,
            amount=self.total_amount,
        ))

    def cancel_order(self, cancellation_reason: Optional[str] = None): # Added reason parameter
        # More complex cancellation rules will apply when OrderStatus is fully updated
        if self.status not in [OrderStatus.DRAFT, OrderStatus.PROCESSING]:
            raise OrderValidationException(f"Cannot cancel order in status {self.status.value}.")
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now(timezone.utc)
        self.add_domain_event(OrderCancelledEvent(
            aggregate_id=self.id,
            order_number=self.order_number,
            customer_id=self.customer_id,
            status=self.status.value,
            amount=self.total_amount,
            cancellation_reason=cancellation_reason
        ))

    def complete_order(self, tracking_number: Optional[str] = None): # Added tracking_number parameter
        if self.status != OrderStatus.PROCESSING:
            raise OrderValidationException(f"Cannot complete order in status {self.status.value}. Must be PROCESSING.")
        self.status = OrderStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)
        # Update tracking number if provided
        if tracking_number:
            self.tracking_number = tracking_number
        self.add_domain_event(OrderCompletedEvent(
            aggregate_id=self.id,
            order_number=self.order_number,
            customer_id=self.customer_id,
            status=self.status.value,
            amount=self.total_amount,
            tracking_number=self.tracking_number
        ))
