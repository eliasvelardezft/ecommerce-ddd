# Testing Strategy for E-Commerce DDD+CQRS Project

This document outlines the testing strategy for our DDD+CQRS+Event Sourcing e-commerce application. The goal is to ensure the system works correctly while respecting the architectural boundaries.

## Table of Contents

- [Testing Strategy for E-Commerce DDD+CQRS Project](#testing-strategy-for-e-commerce-dddcqrs-project)
  - [Table of Contents](#table-of-contents)
  - [Testing Principles](#testing-principles)
  - [Test Types](#test-types)
    - [Unit Tests](#unit-tests)
    - [Integration Tests](#integration-tests)
    - [End-to-End Tests](#end-to-end-tests)
  - [Domain Layer Testing](#domain-layer-testing)
    - [Entity and Aggregate Testing](#entity-and-aggregate-testing)
    - [Domain Event Testing](#domain-event-testing)
  - [Application Layer Testing](#application-layer-testing)
    - [Command Handler Testing](#command-handler-testing)
    - [Query Handler Testing](#query-handler-testing)
  - [Infrastructure Layer Testing](#infrastructure-layer-testing)
    - [Repository Testing](#repository-testing)
    - [Event Dispatcher Testing](#event-dispatcher-testing)
    - [Event Handler Testing](#event-handler-testing)
  - [API Layer Testing](#api-layer-testing)
  - [Cross-Domain Testing](#cross-domain-testing)
  - [End-to-End Testing](#end-to-end-testing)
  - [Test Environment Setup](#test-environment-setup)
    - [Test Database Setup](#test-database-setup)
    - [Event Dispatcher Setup](#event-dispatcher-setup)
    - [Application Setup](#application-setup)
  - [CI/CD Integration](#cicd-integration)
    - [Test Automation](#test-automation)
    - [Required Packages](#required-packages)
    - [Directory Structure for Tests](#directory-structure-for-tests)
    - [Test Best Practices](#test-best-practices)

## Testing Principles

1. **Respect Domain Boundaries**: Tests should respect the boundaries between domains
2. **Test in Isolation**: Components should be tested in isolation with mocks/stubs for dependencies
3. **Behavior over Implementation**: Test expected behaviors rather than implementation details
4. **Complete Test Pyramid**: Include unit, integration, and E2E tests in appropriate ratios
5. **Fast Feedback Loop**: Tests should be fast to encourage running them often

## Test Types

### Unit Tests
- Fast execution, no external dependencies
- Test individual classes and methods in isolation
- Use mocks/stubs for external dependencies

### Integration Tests
- Test interaction between components
- May involve test databases or in-memory alternatives
- Focus on boundaries between components

### End-to-End Tests
- Test complete user flows
- Exercise the entire system including external dependencies
- Slower but provide confidence in system-wide functionality

## Domain Layer Testing

### Entity and Aggregate Testing

Test the behavior of entities and aggregates in isolation:

```python
# test_order.py
def test_order_calculates_total_amount():
    # Arrange
    items = [
        OrderItem(product_id=uuid4(), quantity=2, price=10.0),
        OrderItem(product_id=uuid4(), quantity=1, price=5.0)
    ]
    
    # Act
    order = Order.create(id=uuid4(), customer_id=uuid4(), items=items)
    
    # Assert
    assert order.total_amount == 25.0
```

### Domain Event Testing

Test that domain events are correctly generated:

```python
def test_order_placed_event_generated():
    # Arrange
    customer_id = uuid4()
    items = [OrderItem(product_id=uuid4(), quantity=2, price=10.0)]
    
    # Act
    order = Order.create(id=uuid4(), customer_id=customer_id, items=items)
    
    # Assert
    assert len(order.domain_events) == 1
    event = order.domain_events[0]
    assert isinstance(event, OrderPlacedEvent)
    assert event.customer_id == customer_id
    assert event.total_amount == 20.0
    assert event.items_count == 1
```

## Application Layer Testing

### Command Handler Testing

Test command handlers with mocked repositories and event dispatchers:

```python
# test_place_order_handler.py
@pytest.mark.asyncio
async def test_place_order_handler():
    # Arrange
    command = PlaceOrderCommand(
        customer_id=uuid4(),
        items=[OrderItem(product_id=uuid4(), quantity=1, price=10.0)]
    )
    
    mock_repository = AsyncMock(spec=OrderWriteRepository)
    mock_dispatcher = AsyncMock(spec=DomainEventDispatcher)
    
    handler = PlaceOrderHandler(
        write_repository=mock_repository,
        event_dispatcher=mock_dispatcher
    )
    
    # Act
    await handler.handle(command)
    
    # Assert
    mock_repository.save.assert_called_once()
    mock_dispatcher.dispatch.assert_called()
```

### Query Handler Testing

Test query handlers with mocked read repositories:

```python
# test_get_order_details_handler.py
@pytest.mark.asyncio
async def test_get_order_details_handler():
    # Arrange
    query = GetOrderDetailsQuery(id=uuid4())
    expected_result = OrderDetailsDTO(id=str(query.id), customer_id="123", total_amount=30.0)
    
    mock_repository = AsyncMock(spec=OrderReadRepository)
    mock_repository.get_order_details.return_value = expected_result
    
    handler = GetOrderDetailsHandler(read_repository=mock_repository)
    
    # Act
    result = await handler.handle(query)
    
    # Assert
    assert result == expected_result
    mock_repository.get_order_details.assert_called_once_with(id=query.id)
```

## Infrastructure Layer Testing

### Repository Testing

Test repositories with a test database:

```python
# test_order_write_repository.py
@pytest.mark.asyncio
async def test_order_write_repository():
    # Arrange
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        repository = OrderWriteRepository(session=session)
        
        order = Order.create(
            id=uuid4(),
            customer_id=uuid4(),
            items=[OrderItem(product_id=uuid4(), quantity=1, price=10.0)]
        )
        
        # Act
        await repository.save(order)
        
        # Assert
        saved_order = await repository.get_by_id(order.id)
        assert saved_order is not None
        assert saved_order.id == order.id
```

### Event Dispatcher Testing

Test the event dispatcher with mock handlers:

```python
# test_event_dispatcher.py
@pytest.mark.asyncio
async def test_event_dispatcher():
    # Arrange
    dispatcher = DomainEventDispatcher()
    
    mock_handler = AsyncMock(spec=DomainEventHandler)
    event = OrderPlacedEvent(
        aggregate_id=uuid4(),
        customer_id=uuid4(),
        total_amount=20.0,
        items_count=2
    )
    
    dispatcher.register_handler(OrderPlacedEvent, mock_handler)
    
    # Act
    await dispatcher.dispatch(event)
    
    # Assert
    mock_handler.handle.assert_called_once_with(event)
```

### Event Handler Testing

Test event handlers individually:

```python
# test_order_placed_handlers.py
@pytest.mark.asyncio
async def test_update_read_model_handler():
    # Arrange
    mock_read_repo = AsyncMock(spec=OrderReadRepository)
    handler = UpdateReadModelHandler(read_repository=mock_read_repo)
    
    event = OrderPlacedEvent(
        aggregate_id=uuid4(),
        customer_id=uuid4(),
        total_amount=20.0,
        items_count=2
    )
    
    # Act
    await handler.handle(event)
    
    # Assert
    mock_read_repo.update_read_model.assert_called_once()
    # Verify the DTO passed to update_read_model has the correct values
    called_dto = mock_read_repo.update_read_model.call_args[0][0]
    assert called_dto.id == str(event.aggregate_id)
    assert called_dto.total_amount == event.total_amount
```

## API Layer Testing

Test API endpoints using FastAPI's TestClient:

```python
# test_order_api.py
def test_place_order_endpoint():
    # Arrange
    client = TestClient(app)
    order_data = {
        "customer_id": str(uuid4()),
        "items": [
            {
                "product_id": str(uuid4()),
                "quantity": 2,
                "price": 10.0
            }
        ]
    }
    
    # Act
    response = client.post("/orders/", json=order_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
```

## Cross-Domain Testing

Test handlers that process events from other domains:

```python
# test_cross_domain_handlers.py
@pytest.mark.asyncio
async def test_update_customer_for_order_placed():
    # Arrange
    mock_customer_repo = AsyncMock(spec=CustomerReadRepository)
    handler = UpdateCustomerHandler(read_repository=mock_customer_repo)
    
    # Create event data manually to avoid importing OrderPlacedEvent in Customer domain
    event_data = {
        "aggregate_id": str(uuid4()),
        "customer_id": str(uuid4()),
        "total_amount": 30.0,
        "items_count": 3
    }
    
    # Mock customer profile
    profile = CustomerProfileDTO(
        id=event_data["customer_id"],
        name="Test Customer",
        email="test@example.com",
        created_at=datetime.now(),
        total_orders=1
    )
    mock_customer_repo.get_customer_profile_by_id.return_value = profile
    
    # Act
    # We use a custom event-like object that supports get()
    event = type("EventDict", (), {"get": lambda self, key: event_data.get(key)})()
    await handler.handle(event)
    
    # Assert
    mock_customer_repo.get_customer_profile_by_id.assert_called_once_with(
        id=event_data["customer_id"]
    )
    assert profile.total_orders == 2  # Should increment by 1
    mock_customer_repo.update_read_model.assert_called_once_with(profile)
```

## End-to-End Testing

Test complete user flows, using temporary databases:

```python
# test_place_order_flow.py
@pytest.mark.asyncio
async def test_complete_order_flow():
    # Setup test database connections
    # This would be handled by fixtures in practice
    
    # Register a customer
    customer_data = {
        "name": "Test Customer",
        "email": "test@example.com"
    }
    customer_response = client.post("/customers/", json=customer_data)
    customer_id = customer_response.json()["id"]
    
    # Place an order
    order_data = {
        "customer_id": customer_id,
        "items": [
            {
                "product_id": str(uuid4()),
                "quantity": 2,
                "price": 10.0
            }
        ]
    }
    order_response = client.post("/orders/", json=order_data)
    order_id = order_response.json()["id"]
    
    # Give event handlers time to process events
    await asyncio.sleep(0.1)
    
    # Check order read model
    order_details_response = client.get(f"/orders/{order_id}/details")
    assert order_details_response.status_code == 200
    order_details = order_details_response.json()
    assert order_details["customer_id"] == customer_id
    
    # Check customer read model was updated
    customer_profile_response = client.get(f"/customers/profile/{customer_data['email']}")
    assert customer_profile_response.status_code == 200
    customer_profile = customer_profile_response.json()
    assert customer_profile["total_orders"] == 1
```

## Test Environment Setup

### Test Database Setup

For integration tests, use in-memory databases:

```python
@pytest.fixture
async def test_write_db():
    """Create an in-memory SQLite database for testing"""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

@pytest.fixture
def test_read_db():
    """Create an in-memory MongoDB for testing"""
    mongomock_client = mongomock.MongoClient()
    db = mongomock_client["test_db"]
    return db
```

### Event Dispatcher Setup

Create a test event dispatcher:

```python
@pytest.fixture
def test_event_dispatcher():
    """Create a clean event dispatcher for testing"""
    return DomainEventDispatcher()
```

### Application Setup

Create test container with dependencies:

```python
@pytest.fixture
async def test_container(test_read_db, test_write_db):
    """Create a container with test dependencies"""
    customer_repo = CustomerReadRepository(test_read_db)
    order_repo = OrderReadRepository(test_read_db)
    email_service = MockEmailService()
    audit_service = MockAuditService()
    
    container = {
        "customer_read_repository": customer_repo,
        "order_read_repository": order_repo,
        "email_service": email_service,
        "audit_service": audit_service,
        "event_store": EventStore()
    }
    
    return container
```

## CI/CD Integration

### Test Automation

Run tests in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          pytest --cov=src tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### Required Packages

```
# requirements-test.txt
pytest==7.3.1
pytest-asyncio==0.21.0
pytest-cov==4.1.0
httpx==0.24.1
pytest-mock==3.10.0
mongomock==4.1.2
aiosqlite==0.19.0
```

### Directory Structure for Tests

Match the structure of the source code:

```
tests/
├── unit/                   # Unit tests
│   ├── domain/
│   │   ├── customers/
│   │   └── orders/
│   ├── application/
│   │   ├── customers/
│   │   └── orders/
│   └── infrastructure/
├── integration/           # Integration tests
│   ├── repositories/
│   ├── event_handlers/
│   └── api/
└── e2e/                   # End-to-end tests
    ├── customer_flows.py
    └── order_flows.py
```

### Test Best Practices

1. **Arrange-Act-Assert**: Structure tests in this clear pattern
2. **Clear Test Names**: Use descriptive test names (e.g., `test_order_placed_event_updates_customer_order_count`)
3. **Mock External Services**: Always mock external services like email
4. **Parameterized Tests**: Use pytest's parameterization for testing multiple cases
5. **Fixtures Over Setup**: Use pytest fixtures instead of setup/teardown methods
6. **Test Isolation**: Each test should be independent
7. **Test Coverage**: Aim for high test coverage, especially in domain logic 