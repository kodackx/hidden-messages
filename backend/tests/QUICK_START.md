# Test Suite Quick Start

## Setup (One Time)

```bash
cd backend
uv sync --extra dev
```

## Run Tests

```bash
# All tests
make test

# Or directly
cd backend
uv run pytest
```

## Common Commands

```bash
# Unit tests only (fast)
make test-unit

# Integration tests only
make test-integration

# With coverage report
make test-coverage

# Verbose output (see each test)
make test-verbose

# Stop at first failure
make test-fail-fast

# Run specific file
make test-file FILE=test_schemas.py

# Run specific test
cd backend
uv run pytest tests/test_schemas.py::TestAgentOutput::test_valid_agent_output
```

## What Gets Tested

✅ **Schemas** - Pydantic validation  
✅ **Agent Manager** - LLM response handling  
✅ **API Endpoints** - FastAPI routes  
✅ **Database** - SQLAlchemy models  
✅ **Edge Cases** - Error handling  

## Test Results

Expected: **180+ tests pass** in **< 10 seconds**

## Troubleshooting

### Import errors?
```bash
cd backend  # Make sure you're in backend directory
uv sync --extra dev  # Reinstall dependencies
```

### Async warnings?
Check that `pytest-asyncio` is installed and pytest.ini exists.

### Database errors?
Tests use in-memory SQLite (no setup needed). Check `aiosqlite` is installed.

## Writing Tests

```python
# Unit test template
@pytest.mark.unit
class TestMyFeature:
    @pytest.mark.asyncio
    async def test_something(self):
        # Arrange
        ...
        
        # Act
        result = await my_async_function()
        
        # Assert
        assert result == expected

# Integration test template
@pytest.mark.integration  
class TestMyAPI:
    @pytest.mark.asyncio
    async def test_endpoint(self, client):
        response = await client.post("/api/endpoint", json={...})
        assert response.status_code == 200
```

## More Info

See `backend/tests/README.md` for full documentation.
