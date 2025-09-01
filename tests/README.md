# E-commerce DDD Testing Strategy

This directory contains comprehensive tests for the e-commerce DDD/CQRS application, focusing on behavior-driven testing to validate the MVP e-commerce flow.

## Testing Philosophy

Our testing approach follows these principles:

1. **Behavior-Driven Testing**: We test what the system does, not how it does it
2. **Database State Verification**: Tests verify actual state changes in the database
3. **MVP Flow Coverage**: Complete coverage of the basic e-commerce user journey
4. **Integration Focus**: Tests simulate real API calls and verify end-to-end behavior

## MVP E-commerce Flow

Our tests cover this complete user journey:

1. **Customer Registration** - `POST /api/customers/`
2. **Browse Products** - `GET /api/products/`
3. **View Product Details** - `GET /api/products/{id}`
4. **Place Order** - `POST /api/orders/`
5. **View Order Details** - `GET /api/orders/{id}/details`

## Test Structure

```
tests/
├── README.md                 # This file
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini              # Pytest configuration
├── test_api_endpoints.py    # API endpoint structure tests (fast)
├── test_mvp_ecommerce_flow.py # Full integration tests (comprehensive)
└── requirements.txt         # Test dependencies
```

## Test Categories

### 1. API Endpoint Tests (`test_api_endpoints.py`)
- **Fast execution** - No database setup required
- **Validation testing** - Ensures endpoints accept correct data structures
- **Error handling** - Tests validation and error responses
- **Endpoint accessibility** - Verifies all MVP endpoints exist

### 2. MVP Flow Integration Tests (`test_mvp_ecommerce_flow.py`)
- **Complete flow testing** - End-to-end MVP scenarios
- **Database state verification** - Checks actual data persistence
- **Business logic validation** - Ensures domain rules are enforced
- **Cross-domain integration** - Tests interaction between bounded contexts

## Required Dependencies

For testing, you'll need:

```bash
# Core testing
pytest>=7.0.0
pytest-asyncio>=0.20.0
pytest-cov>=4.0.0

# API testing
httpx>=0.24.0
fastapi[all]>=0.95.0

# Database testing
sqlalchemy[asyncio]>=1.4.0
motor>=3.0.0  # MongoDB async driver
asyncpg>=0.27.0  # PostgreSQL async driver

# Mocking (for unit tests)
pytest-mock>=3.10.0
```

## Database Setup for Integration Tests

### PostgreSQL (Write Model)
```sql
-- Create test database
CREATE DATABASE ecommerce_test;

-- Create test user (optional)
CREATE USER ecommerce_test_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_test TO ecommerce_test_user;
```

### MongoDB (Read Model)
```bash
# Start MongoDB with test database
mongod --dbpath /path/to/test/db

# Test database will be created automatically
# Collections: customers, products, categories, orders, events
```

## Running Tests

### Quick API Tests (Fast)
```bash
# Run only API endpoint tests
pytest tests/test_api_endpoints.py -v

# Run with coverage
pytest tests/test_api_endpoints.py --cov=src --cov-report=html
```

### Full Integration Tests (Comprehensive)
```bash
# Run full MVP flow tests (requires database setup)
pytest tests/test_mvp_ecommerce_flow.py -v

# Run all tests
pytest tests/ -v

# Run with coverage and HTML report
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

### Run Specific Test Categories
```bash
# Run only MVP flow tests
pytest -m mvp

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

## Test Configuration

### Environment Variables
```bash
# Test database URLs
export TEST_POSTGRES_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce_test"
export TEST_MONGO_URL="mongodb://localhost:27017"
export TEST_MONGO_DB="ecommerce_test"

# Test settings
export API_DEBUG=false
export LOG_LEVEL=WARNING
```

### Docker Setup (Optional)
```bash
# Start test databases with Docker
docker-compose -f docker-compose.test.yml up -d

# Run tests
pytest tests/ -v

# Cleanup
docker-compose -f docker-compose.test.yml down
```

## Test Data Management

### Fixtures
- **Automatic cleanup** - Each test gets a clean database state
- **Reusable test data** - Common fixtures for customers, products, orders
- **Consistent data** - Standardized test data across all tests

### Test Data Examples
```python
# Customer data
{
    "name": "John Doe",
    "email": "john.doe@example.com"
}

# Product data
{
    "name": "Smartphone",
    "sku": "PHONE-001",
    "price_amount": "599.99",
    "price_currency": "USD",
    "stock_quantity": 50
}

# Order data
{
    "customer_id": "uuid-here",
    "items": [...],
    "shipping_details": {...}
}
```

## Expected Test Results

### Success Criteria
- ✅ Customer can register successfully
- ✅ Products can be browsed and viewed
- ✅ Orders can be placed with valid data
- ✅ Database state matches expected values
- ✅ Domain events are properly dispatched
- ✅ Integration between bounded contexts works

### Failure Scenarios Tested
- ❌ Invalid customer data (missing email, invalid format)
- ❌ Non-existent product IDs
- ❌ Invalid order data (empty items, invalid shipping)
- ❌ Currency mismatches
- ❌ Business rule violations

## Debugging Tests

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database is running
   pg_isready -h localhost -p 5432
   mongo --eval "db.runCommand('ping')"
   ```

2. **Async Test Issues**
   ```bash
   # Ensure pytest-asyncio is installed
   pip install pytest-asyncio
   
   # Check pytest.ini has asyncio_mode = auto
   ```

3. **Import Errors**
   ```bash
   # Run from project root
   cd /path/to/ecommerce-ddd
   python -m pytest tests/
   ```

### Test Debugging Commands
```bash
# Run with verbose output
pytest tests/ -v -s

# Run single test with debugging
pytest tests/test_api_endpoints.py::TestCustomerEndpoints::test_register_customer_endpoint_structure -v -s

# Run with pdb debugger
pytest tests/ --pdb

# Run failed tests only
pytest tests/ --lf
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: ecommerce_test
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
      mongodb:
        image: mongo:5
        ports:
          - 27017:27017
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tests/requirements.txt
    
    - name: Run tests
      run: pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Contributing to Tests

### Adding New Tests
1. **API Tests**: Add to `test_api_endpoints.py` for quick validation
2. **Integration Tests**: Add to `test_mvp_ecommerce_flow.py` for behavior verification
3. **New Features**: Create dedicated test files for new bounded contexts

### Test Naming Convention
- `test_[feature]_[scenario]()` - For specific functionality
- `test_[feature]_validation()` - For input validation
- `test_[feature]_error_handling()` - For error scenarios

### Test Documentation
- Each test should have a clear docstring explaining what it validates
- Use descriptive test names that explain the behavior being tested
- Include comments for complex test setup or assertions

## Performance Considerations

### Test Execution Speed
- **API tests**: ~10-30 seconds (no database setup)
- **Integration tests**: ~2-5 minutes (with database setup)
- **Full suite**: ~5-10 minutes (depending on hardware)

### Optimization Tips
1. Run API tests first for quick feedback
2. Use `pytest-xdist` for parallel execution
3. Mock external dependencies when possible
4. Use database transactions for faster cleanup

## Next Steps

After the MVP tests are passing:

1. **Add Performance Tests** - Load testing for key endpoints
2. **Add Security Tests** - Authentication, authorization, input sanitization
3. **Add Contract Tests** - API contract validation
4. **Add E2E Tests** - Browser automation tests
5. **Add Chaos Tests** - Failure scenario testing

This testing strategy ensures your MVP e-commerce flow is solid and ready for frontend development! 