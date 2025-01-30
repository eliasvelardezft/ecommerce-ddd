import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.infrastructure.core.settings import settings
from src.api.customers.router import router as customer_router
from src.api.dependencies import init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable SQLAlchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
