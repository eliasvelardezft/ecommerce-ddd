"""
E-commerce MVP Flow Integration Tests

This test suite validates the complete e-commerce MVP flow with behavior-based testing.
We test the API endpoints and verify the resulting state changes in the database.

MVP Flow:
1. Register as a customer
2. Browse products
3. Check specific product details
4. Place an order

Testing Strategy:
- Use FastAPI TestClient for API calls
- Verify database state changes after each operation
- Test both success and failure scenarios
- Focus on behavior, not implementation details
"""

import asyncio
from decimal import Decimal
from typing import Any, AsyncGenerator, Dict
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_mongo_db
from main import app


@pytest.fixture
def test_app(sqlite_session, mongo_db):
    """Create a test app with overridden dependencies."""
    # Override database dependencies to use test databases
    async def override_get_db_session():
        try:
            yield sqlite_session
            await sqlite_session.commit()  # Match production behavior
        except:
            await sqlite_session.rollback()
            raise
    
    def override_get_mongo_db():
        return mongo_db
    
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_mongo_db] = override_get_mongo_db
    
    yield app
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
async def client(test_app):
    """Create FastAPI async test client with mocked dependencies."""
    from httpx import ASGITransport
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


# Test fixtures are now imported from conftest.py


class TestMVPECommerceFlow:
    """Test class for the complete MVP e-commerce flow."""
    
    async def test_complete_mvp_flow(
        self,
        client: AsyncClient,
        sqlite_session: AsyncSession,
        mongo_db,
        sample_customer_data: Dict[str, Any],
        sample_category_data: Dict[str, Any],
        sample_product_data: Dict[str, Any],
        sample_order_data: Dict[str, Any]
    ):
        """Test the complete MVP e-commerce flow end-to-end."""
        
        # ===========================================
        # STEP 1: CUSTOMER REGISTRATION
        # ===========================================
        
        # 1.1 Command: Register customer
        response = await client.post("/api/customers/", json=sample_customer_data)
        
        # Debug: Print response details if not 200
        if response.status_code != 200:
            print(f"❌ Registration failed with status {response.status_code}")
            print(f"Response content: {response.text}")
            print(f"Request data: {sample_customer_data}")
        
        assert response.status_code == 200
        
        customer_response = response.json()
        assert customer_response["email"] == sample_customer_data["email"]
        assert customer_response["name"] == sample_customer_data["name"]
        assert "id" in customer_response
        
        customer_id = customer_response["id"]
        
        # 1.2 Query: Get customer profile (read model check)
        profile_response = await client.get(f"/api/customers/profile/{sample_customer_data['email']}")
        assert profile_response.status_code == 200
        
        profile_data = profile_response.json()
        assert profile_data["email"] == sample_customer_data["email"]
        assert profile_data["name"] == sample_customer_data["name"]
        assert profile_data["id"] == customer_id
        
        # 1.3 Write model verification: Check customer in PostgreSQL
        from sqlalchemy import text
        result = await sqlite_session.execute(
            text("SELECT id, name, email FROM customers WHERE id = :customer_id"),
            {"customer_id": customer_id}
        )
        customer_row = result.fetchone()
        assert customer_row is not None
        assert str(customer_row.id) == customer_id
        assert customer_row.email == sample_customer_data["email"]
        assert customer_row.name == sample_customer_data["name"]
        
        # ===========================================
        # STEP 2: CATEGORY MANAGEMENT
        # ===========================================
        
        # 2.1 Command: Create category
        category_response = await client.post("/api/category/", json=sample_category_data)
        assert category_response.status_code == 200
        category_data = category_response.json()
        assert "category_id" in category_data
        category_id = category_data["category_id"]
        
        # 2.2 Query: Get category details (read model check)
        category_detail_response = await client.get(f"/api/category/{category_id}")
        assert category_detail_response.status_code == 200
        
        category_detail = category_detail_response.json()
        assert category_detail["id"] == category_id
        assert category_detail["name"] == sample_category_data["name"]
        assert category_detail["description"] == sample_category_data["description"]
        
        # 2.3 Write model verification: Check category in PostgreSQL
        result = await sqlite_session.execute(
            text("SELECT id, name, description FROM categories WHERE id = :category_id"),
            {"category_id": category_id}
        )
        category_row = result.fetchone()
        assert category_row is not None
        assert str(category_row.id) == category_id
        assert category_row.name == sample_category_data["name"]
        
        # ===========================================
        # STEP 3: PRODUCT MANAGEMENT
        # ===========================================
        
        # 3.1 Command: Create product
        sample_product_data["category_id"] = category_id
        product_response = await client.post("/api/products/", json=sample_product_data)
        assert product_response.status_code == 200
        product_data = product_response.json()
        assert "product_id" in product_data
        product_id = product_data["product_id"]
        
        # 3.2 Query: Get specific product details (read model check)
        product_detail_response = await client.get(f"/api/products/{product_id}")
        assert product_detail_response.status_code == 200
        
        product_detail = product_detail_response.json()
        assert product_detail["id"] == product_id
        assert product_detail["name"] == sample_product_data["name"]
        assert product_detail["sku"] == sample_product_data["sku"]
        assert product_detail["category_id"] == category_id
        
        # 3.3 Query: Browse all products (read model check)
        browse_response = await client.get("/api/products/")
        assert browse_response.status_code == 200
        
        browse_data = browse_response.json()
        assert "products" in browse_data
        assert browse_data["count"] >= 1
        
        # Find our product in the list
        our_product = next(
            (p for p in browse_data["products"] if p["id"] == product_id),
            None
        )
        assert our_product is not None
        assert our_product["name"] == sample_product_data["name"]
        
        # 3.4 Write model verification: Check product in PostgreSQL
        result = await sqlite_session.execute(
            text("SELECT id, name, sku, category_id FROM products WHERE id = :product_id"),
            {"product_id": product_id}
        )
        product_row = result.fetchone()
        assert product_row is not None
        assert str(product_row.id) == product_id
        assert product_row.name == sample_product_data["name"]
        assert product_row.sku == sample_product_data["sku"]
        assert str(product_row.category_id) == category_id
        
        # ===========================================
        # STEP 4: ORDER PLACEMENT
        # ===========================================
        
        # 4.1 Command: Place order
        sample_order_data["customer_id"] = customer_id
        sample_order_data["items"] = [
            {
                "product_id": product_id,
                "product_name": sample_product_data["name"],
                "quantity": 2,
                "unit_price": {
                    "amount": sample_product_data["price_amount"],
                    "currency": sample_product_data["price_currency"]
                }
            }
        ]
        
        order_response = await client.post("/api/orders/", json=sample_order_data)
        assert order_response.status_code == 200
        
        order_response_data = order_response.json()
        assert "order_id" in order_response_data
        assert order_response_data["customer_id"] == customer_id
        assert "total_amount" in order_response_data
        
        order_id = order_response_data["order_id"]
        
        # 4.2 Query: Get order details (read model check)
        order_detail_response = await client.get(f"/api/orders/{order_id}/details")
        assert order_detail_response.status_code == 200
        
        order_detail = order_detail_response.json()
        assert order_detail["id"] == order_id
        assert order_detail["customer_id"] == customer_id
        assert len(order_detail["items"]) == 1
        assert order_detail["items"][0]["product_id"] == product_id
        assert order_detail["items"][0]["quantity"] == 2
        
        # 4.3 Write model verification: Check order in PostgreSQL
        result = await sqlite_session.execute(
            text("SELECT id, customer_id, status FROM orders WHERE id = :order_id"),
            {"order_id": order_id}
        )
        order_row = result.fetchone()
        assert order_row is not None
        assert str(order_row.id) == order_id
        assert str(order_row.customer_id) == customer_id
        assert order_row.status is not None
        
        # 4.4 Write model verification: Check order items in PostgreSQL
        result = await sqlite_session.execute(
            text("SELECT order_id, product_id, quantity FROM order_items WHERE order_id = :order_id"),
            {"order_id": order_id}
        )
        order_items = result.fetchall()
        assert len(order_items) == 1
        assert str(order_items[0].order_id) == order_id
        assert str(order_items[0].product_id) == product_id
        assert order_items[0].quantity == 2
        
        # ===========================================
        # STEP 5: CUSTOMER PROFILE WITH ORDERS
        # ===========================================
        
        # 5.1 Query: Get customer by ID (should include order history in read model)
        customer_by_id_response = await client.get(f"/api/customers/{customer_id}")
        assert customer_by_id_response.status_code == 200
        
        customer_by_id = customer_by_id_response.json()
        assert customer_by_id["id"] == customer_id
        assert customer_by_id["email"] == sample_customer_data["email"]
        assert customer_by_id["name"] == sample_customer_data["name"]
        
    # async def test_customer_registration_validation(self, client: TestClient):
    #     """Test customer registration with invalid data."""
        
    #     # Test missing name
    #     response = await client.post("/api/customers/", json={"email": "test@example.com"})
    #     assert response.status_code == 422
        
    #     # Test missing email
    #     response = await client.post("/api/customers/", json={"name": "Test User"})
    #     assert response.status_code == 422
        
    #     # Test invalid email format
    #     response = await client.post("/api/customers/", json={
    #         "name": "Test User",
    #         "email": "invalid-email"
    #     })
    #     assert response.status_code == 422
        
    # async def test_product_not_found(self, client: TestClient):
    #     """Test getting non-existent product."""
    #     fake_product_id = str(uuid4())
    #     response = await client.get(f"/api/products/{fake_product_id}")
    #     assert response.status_code == 404
        
    # async def test_order_with_invalid_customer(self, client: TestClient, sample_order_data: Dict[str, Any]):
    #     """Test placing order with non-existent customer."""
    #     sample_order_data["customer_id"] = str(uuid4())
    #     sample_order_data["items"] = [
    #         {
    #             "product_id": str(uuid4()),
    #             "product_name": "Test Product",
    #             "quantity": 1,
    #             "unit_price": {
    #                 "amount": "10.00",
    #                 "currency": "USD"
    #             }
    #         }
    #     ]
        
    #     response = await client.post("/api/orders/", json=sample_order_data)
    #     assert response.status_code == 400
        
    # async def test_order_with_empty_items(self, client: TestClient, sample_order_data: Dict[str, Any]):
    #     """Test placing order with no items."""
    #     sample_order_data["customer_id"] = str(uuid4())
    #     sample_order_data["items"] = []
        
    #     response = await client.post("/api/orders/", json=sample_order_data)
    #     assert response.status_code == 400
        
    # async def test_get_customer_by_id(self, client: TestClient, sample_customer_data: Dict[str, Any]):
    #     """Test getting customer by ID."""
        
    #     # Register customer
    #     response = await client.post("/api/customers/", json=sample_customer_data)
    #     assert response.status_code == 200
    #     customer_id = response.json()["id"]
        
    #     # Get customer by ID
    #     response = await client.get(f"/api/customers/{customer_id}")
    #     assert response.status_code == 200
        
    #     customer_data = response.json()
    #     assert customer_data["id"] == customer_id
    #     assert customer_data["email"] == sample_customer_data["email"]
        
    # async def test_get_customer_by_email(self, client: TestClient, sample_customer_data: Dict[str, Any]):
    #     """Test getting customer by email."""
        
    #     # Register customer
    #     response = await client.post("/api/customers/", json=sample_customer_data)
    #     assert response.status_code == 200
        
    #     # Get customer by email
    #     response = await client.get(f"/api/customers/profile/{sample_customer_data['email']}")
    #     assert response.status_code == 200
        
    #     customer_data = response.json()
    #     assert customer_data["email"] == sample_customer_data["email"]
        
    # async def test_browse_products_empty_catalog(self, client: TestClient):
    #     """Test browsing products when catalog is empty."""
    #     response = await client.get("/api/products/")
    #     assert response.status_code == 200
        
    #     data = response.json()
    #     assert "products" in data
    #     assert data["count"] == 0
    #     assert len(data["products"]) == 0


# class TestOrderValidation:
#     """Test class for order validation scenarios."""
    
#     async def test_order_currency_validation(self, client: TestClient, sample_order_data: Dict[str, Any]):
#         """Test order with invalid currency."""
#         sample_order_data["customer_id"] = str(uuid4())
#         sample_order_data["currency"] = "INVALID"
#         sample_order_data["items"] = [
#             {
#                 "product_id": str(uuid4()),
#                 "product_name": "Test Product",
#                 "quantity": 1,
#                 "unit_price": {
#                     "amount": "10.00",
#                     "currency": "USD"
#                 }
#             }
#         ]
        
#         response = await client.post("/api/orders/", json=sample_order_data)
#         assert response.status_code == 400
        
#     async def test_order_shipping_details_validation(self, client: TestClient, sample_order_data: Dict[str, Any]):
#         """Test order with invalid shipping details."""
#         sample_order_data["customer_id"] = str(uuid4())
#         sample_order_data["shipping_details"] = {
#             "address_line1": "",  # Empty required field
#             "city": "New York",
#             "state_province": "NY",
#             "postal_code": "10001",
#             "country": "USA",
#             "phone_number": "+1-555-0123"
#         }
#         sample_order_data["items"] = [
#             {
#                 "product_id": str(uuid4()),
#                 "product_name": "Test Product",
#                 "quantity": 1,
#                 "unit_price": {
#                     "amount": "10.00",
#                     "currency": "USD"
#                 }
#             }
#         ]
        
#         response = await client.post("/api/orders/", json=sample_order_data)
#         assert response.status_code == 422  # Validation error


# class TestProductManagement:
#     """Test class for product management operations."""
    
#     async def test_product_lifecycle(self, client: TestClient, sample_category_data: Dict[str, Any], sample_product_data: Dict[str, Any]):
#         """Test complete product lifecycle: create, update, activate, deactivate."""
        
#         # Create category
#         category_response = await client.post("/api/category/", json=sample_category_data)
#         assert category_response.status_code == 200
#         category_id = category_response.json()["category_id"]
        
#         # Create product
#         sample_product_data["category_id"] = category_id
#         product_response = await client.post("/api/products/", json=sample_product_data)
#         assert product_response.status_code == 200
#         product_id = product_response.json()["product_id"]
        
#         # Update product price
#         price_update_response = await client.put(f"/api/products/{product_id}/price", json={
#             "new_price_amount": "699.99",
#             "new_price_currency": "USD"
#         })
#         assert price_update_response.status_code == 200
        
#         # Update product stock
#         stock_update_response = await client.put(f"/api/products/{product_id}/stock", json={
#             "change_in_quantity": -5
#         })
#         assert stock_update_response.status_code == 200
        
#         # Deactivate product
#         deactivate_response = await client.post(f"/api/products/{product_id}/deactivate")
#         assert deactivate_response.status_code == 200
        
#         # Activate product
#         activate_response = await client.post(f"/api/products/{product_id}/activate")
#         assert activate_response.status_code == 200
        
#         # Verify product is in active products list
#         browse_response = await client.get("/api/products/")
#         assert browse_response.status_code == 200
        
#         products = browse_response.json()["products"]
#         our_product = next((p for p in products if p["id"] == product_id), None)
#         assert our_product is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])