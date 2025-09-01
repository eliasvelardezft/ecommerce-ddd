"""
Pytest configuration and shared fixtures for e-commerce tests.

This file contains shared fixtures and configuration that can be used
across all test modules.
"""

import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import mongomock_motor

from infrastructure.core.persistence.base import BaseModel


# Test Configuration
TEST_SQLITE_URL = "sqlite+aiosqlite:///:memory:"
# MongoDB mock doesn't need URL - using in-memory mock
TEST_MONGO_DB = "ecommerce_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_sqlite_engine():
    """Create test SQLite engine and setup tables."""
    engine = create_async_engine(
        TEST_SQLITE_URL,
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest.fixture(scope="session")
async def test_mongo_client():
    """Create test MongoDB mock client."""
    client = mongomock_motor.AsyncMongoMockClient()
    yield client
    # Mock client doesn't need explicit closing


@pytest.fixture
async def sqlite_session(test_sqlite_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean SQLite session for each test."""
    async_session = sessionmaker(
        test_sqlite_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def mongo_db(test_mongo_client):
    """Create a clean MongoDB database for each test."""
    db = test_mongo_client[TEST_MONGO_DB]
    
    # Clean all collections before each test
    collections = ["customers", "products", "categories", "orders", "events"]
    for collection in collections:
        try:
            await db[collection].delete_many({})
        except Exception:
            # Collection might not exist yet, that's fine
            pass
    
    yield db


@pytest.fixture(autouse=True)
async def cleanup_databases(sqlite_session, mongo_db):
    """Automatically clean up databases after each test."""
    yield
    
    # Clean up MongoDB collections
    collections = ["customers", "products", "categories", "orders", "events"]
    for collection in collections:
        try:
            await mongo_db[collection].delete_many({})
        except Exception:
            # Collection might not exist or connection might be closed
            pass
    
    # SQLite cleanup is handled by session rollback in sqlite_session fixture


# Test data fixtures
@pytest.fixture
def sample_customer_data():
    """Sample customer registration data."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }


@pytest.fixture
def sample_category_data():
    """Sample category data."""
    return {
        "name": "Electronics",
        "description": "Electronic devices and accessories"
    }


@pytest.fixture
def sample_product_data():
    """Sample product data."""
    return {
        "name": "Smartphone",
        "description": "Latest model smartphone",
        "sku": "PHONE-001",
        "price_amount": "599.99",
        "price_currency": "USD",
        "stock_quantity": 50,
        "category_id": None,  # Will be set dynamically
        "attributes": [],
        "image_urls": []
    }


@pytest.fixture
def sample_shipping_details():
    """Sample shipping details."""
    return {
        "address_line1": "123 Main St",
        "address_line2": "Apt 4B",
        "city": "New York",
        "state_province": "NY",
        "postal_code": "10001",
        "country": "USA",
        "phone_number": "+1-555-0123"
    }


@pytest.fixture
def sample_order_item():
    """Sample order item data."""
    return {
        "product_id": None,  # Will be set dynamically
        "product_name": "Test Product",
        "quantity": 1,
        "unit_price": {
            "amount": "10.00",
            "currency": "USD"
        }
    }


@pytest.fixture
def sample_order_data(sample_shipping_details):
    """Sample order data."""
    return {
        "customer_id": None,  # Will be set dynamically
        "items": [],  # Will be set dynamically
        "shipping_details": sample_shipping_details,
        "currency": "USD",
        "shipping_cost_raw": "10.00",
        "tax_amount_raw": "5.99",
        "notes": "Test order"
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "mvp: marks tests as part of MVP flow"
    )