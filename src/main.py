import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.infrastructure.core.settings import settings
from src.api.customers.router import router as customer_router
from src.api.orders.router import router as order_router
from src.api.dependencies import init_db, get_mongo_db, EventStore
from src.infrastructure.customers.services.EmailService import EmailService
from src.infrastructure.customers.services.AuditService import AuditService
from src.infrastructure.customers.persistence.CustomerReadRepository import CustomerReadRepository
from src.infrastructure.orders.persistence.OrderReadRepository import OrderReadRepository

# Import the event bootstrap
from src.infrastructure.core.events.bootstrap import configure_dispatcher

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable SQLAlchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await init_db()
    
    # Create service instances
    email_service = EmailService()
    audit_service = AuditService()
    mongo_database = get_mongo_db()
    
    # Create repositories
    customer_read_repo = CustomerReadRepository(mongo_database)
    order_read_repo = OrderReadRepository(mongo_database)
    
    # Create a container for dependencies
    container = {
        "customer_read_repository": customer_read_repo,
        "order_read_repository": order_read_repo,
        "email_service": email_service,
        "audit_service": audit_service,
        "event_store": EventStore()
    }
    
    # Configure event dispatcher
    event_dispatcher = configure_dispatcher(container)
    
    # Make it available through app state
    app.state.event_dispatcher = event_dispatcher
    
    yield

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.api_debug,
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the DDD E-Commerce API",
        "version": "1.0.0"
    }

# Register routers
app.include_router(customer_router)
app.include_router(order_router)