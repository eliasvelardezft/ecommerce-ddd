import logging

# --- Import and Setup Structured Logging --- 
from infrastructure.core.logging_config import setup_logging
setup_logging() # Call this early to configure logging for the entire application
# --- End Logging Setup ---

from fastapi import FastAPI

from infrastructure.core.settings import settings
from api.customers.router import router as customer_router
from api.orders.router import router as order_router
from api.products.router.category import router as category_router
from api.products.router.product import router as product_router
# Removed complex lifespan dependencies - these will become regular FastAPI dependencies

# Standard logger for this file, will now use the Rich setup configured by setup_logging()
logger = logging.getLogger(__name__) 

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.api_debug,
)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.api_title}",
        "version": settings.api_version
    }

app.include_router(customer_router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(category_router, prefix="/api")
app.include_router(product_router, prefix="/api")

logger.info(f"{settings.api_title} application startup complete.")
