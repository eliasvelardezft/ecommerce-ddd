import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_domain_event_dispatcher
from application.customers.commands.RegisterCustomerCommand import (
    RegisterCustomerCommand,
)
from application.customers.commands.RegisterCustomerHandler import (
    RegisterCustomerHandler,
)
from application.customers.queries.GetCustomerProfileHandler import (
    GetCustomerProfileHandler,
)
from application.customers.queries.GetCustomerProfileQuery import (
    GetCustomerProfileQuery,
)
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.core.value_objects.EntityId import EntityId
from domain.customers.repositories.ICustomerReadRepository import (
    ICustomerReadRepository,
)
from domain.customers.repositories.ICustomerWriteRepository import (
    ICustomerWriteRepository,
)

from .dependencies import (
    get_customer_read_repository,
    get_customer_write_repository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post(
    "/",
    summary="Register a new customer",
    description="""
    Register a new customer in the system.
    
    This endpoint creates a new customer with the provided information and triggers
    domain events for customer lifecycle management.
    
    **Business Rules:**
    - Email must be unique across the system
    - Name must be at least 2 characters long
    - Customer will be assigned a unique ID automatically
    
    **Events Triggered:**
    - `CustomerRegisteredEvent`: Internal domain event for customer creation
    """,
    response_description="Customer created successfully with generated ID",
    tags=["customers"],
)
async def register_customer(
    command: RegisterCustomerCommand,
    repository: Annotated[ICustomerWriteRepository, Depends(get_customer_write_repository)],
    event_dispatcher: Annotated[DomainEventDispatcher, Depends(get_domain_event_dispatcher)],
):
    handler = RegisterCustomerHandler(repository, event_dispatcher)
    try:
        customer = await handler.handle(command)
        # Return a clean JSON response with string ID
        return {
            "id": str(customer.id),  # Convert EntityId to string
            "name": customer.name,
            "email": customer.email,
            "created_at": customer.created_at,
            "updated_at": customer.updated_at,
        }
    except Exception as e:
        import traceback

        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/profile/{email}",
    summary="Get customer profile by email",
    description="""
    Retrieve customer profile information using email address.
    
    This endpoint queries the read model (MongoDB) for optimized performance.
    
    **Use Cases:**
    - Login/authentication flows
    - Profile lookup by email
    - Customer service operations
    """,
    response_description="Customer profile data or 404 if not found",
    tags=["customers"],
)
async def get_customer_profile(
    email: str,
    repository: Annotated[ICustomerReadRepository, Depends(get_customer_read_repository)],
):
    query = GetCustomerProfileQuery(email)
    handler = GetCustomerProfileHandler(repository)
    customer = await handler.handle(query)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


@router.get(
    "/{customer_id}",
    summary="Get customer profile by ID",
    description="""
    Retrieve customer profile information using customer ID.
    
    This endpoint queries the read model (MongoDB) for optimized performance.
    
    **Path Parameters:**
    - `customer_id`: UUID string format (e.g., "123e4567-e89b-12d3-a456-426614174000")
    
    **Use Cases:**
    - Direct customer lookup by ID
    - Order processing customer validation
    - Customer profile management
    """,
    response_description="Customer profile data or 404 if not found",
    tags=["customers"],
)
async def get_customer_by_id(
    customer_id: str,
    repository: Annotated[ICustomerReadRepository, Depends(get_customer_read_repository)],
):
    try:
        entity_id = EntityId.from_string(customer_id)
        customer = await repository.get_customer_profile_by_id(entity_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except Exception as e:
        logger.error(f"Error fetching customer {customer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e
