import logging
from fastapi import FastAPI
from src.api.customers.router import router as customer_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="CQRS Example",
    description="A simple CQRS implementation with FastAPI",
    version="1.0.0"
)

# Register routers
app.include_router(customer_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the DDD E-Commerce API",
        "version": "1.0.0"
    }
