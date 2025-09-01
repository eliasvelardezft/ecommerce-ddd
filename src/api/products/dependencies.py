"""Product-specific dependencies"""
from fastapi import Depends

from api.dependencies import get_db_session, get_mongo_db, get_domain_event_dispatcher
from domain.core.events.DomainEventDispatcher import DomainEventDispatcher
from infrastructure.products.persistence.ProductWriteRepository import ProductWriteRepository
from infrastructure.products.persistence.CategoryWriteRepository import CategoryWriteRepository
from infrastructure.products.persistence.ProductReadRepository import ProductReadRepository
from infrastructure.products.persistence.CategoryReadRepository import CategoryReadRepository


def get_product_write_repository(session = Depends(get_db_session)):
    return ProductWriteRepository(session)

def get_category_write_repository(session = Depends(get_db_session)):
    return CategoryWriteRepository(session)

def get_product_read_repository(db = Depends(get_mongo_db)):
    return ProductReadRepository(db)

def get_category_read_repository(db = Depends(get_mongo_db)):
    return CategoryReadRepository(db)

def get_products_event_dispatcher(
    dispatcher: DomainEventDispatcher = Depends(get_domain_event_dispatcher),
) -> DomainEventDispatcher:
    """Returns the configured event dispatcher from app state"""
    return dispatcher