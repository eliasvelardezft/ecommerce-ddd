import logging
from domain.core.value_objects.EntityId import EntityId
from fastapi import APIRouter, HTTPException, Depends

from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from domain.customers.repositories.ICustomerWriteRepository import ICustomerWriteRepository
from domain.customers.repositories.ICustomerReadRepository import ICustomerReadRepository
from application.customers.commands.RegisterCustomerCommand import RegisterCustomerCommand
from application.customers.commands.RegisterCustomerHandler import RegisterCustomerHandler
from .dependencies import (
    get_customer_write_repository,
    get_customer_read_repository,
)
from api.dependencies import get_domain_event_dispatcher
from application.customers.queries.GetCustomerProfileQuery import GetCustomerProfileQuery
from application.customers.queries.GetCustomerProfileHandler import GetCustomerProfileHandler


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

@router.post("/")
async def register_customer(
    command: RegisterCustomerCommand,
    repository: ICustomerWriteRepository = Depends(get_customer_write_repository),
    event_dispatcher: DomainEventDispatcher = Depends(get_domain_event_dispatcher)
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
            "updated_at": customer.updated_at
        }
    except Exception as e:
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile/{email}")
async def get_customer_profile(
    email: str,
    repository: ICustomerReadRepository = Depends(get_customer_read_repository)
):
    query = GetCustomerProfileQuery(email)
    handler = GetCustomerProfileHandler(repository)
    customer = await handler.handle(query)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer

@router.get("/{customer_id}")
async def get_customer_by_id(
    customer_id: str,
    repository: ICustomerReadRepository = Depends(get_customer_read_repository)
):
    try:
        entity_id = EntityId.from_string(customer_id)
        customer = await repository.get_customer_profile_by_id(entity_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except Exception as e:
        logger.error(f"Error fetching customer {customer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
