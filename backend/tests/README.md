# Test Suite Documentation

This directory contains the test suite for the Hidden Messages backend.

## Structure

```
tests/
├── __init__.py                   # Test package marker
├── conftest.py                   # Shared fixtures and configuration
├── test_schemas.py               # Pydantic schema validation tests
├── test_agent_manager.py         # Agent manager and LLM response handling tests
├── test_api_integration.py       # API endpoint integration tests
├── test_database_models.py       # Database model and query tests
├── test_edge_cases.py            # Edge cases and error handling tests
└── README.md                     # This file
```

## Running Tests

### Prerequisites

Install dependencies with dev extras:
```bash
cd backend
uv sync --extra dev
```

### Run All Tests

```bash
# Using make (from project root)
make test

# Or directly with pytest
cd backend
uv run pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
make test-unit

# Integration tests only
make test-integration

# End-to-end tests with REAL LLM calls (slow, expensive)
make test-e2e

# With coverage report
make test-coverage

# Verbose output
make test-verbose

# Stop at first failure
make test-fail-fast

# Specific test file
make test-file FILE=test_schemas.py
```

**Note:** Regular `make test` excludes E2E tests by default to avoid costs and delays.

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Fast, isolated tests that mock external dependencies:
- Schema validation
- Agent manager logic
- Response parsing
- Prompt building
- Database model creation

### Integration Tests (`@pytest.mark.integration`)

Tests that exercise multiple components together:
- API endpoint flows
- Database interactions
- Session lifecycle
- Turn execution

### End-to-End Tests (`@pytest.mark.e2e`)

**Real LLM API calls - SLOW and EXPENSIVE!**
- Test actual OpenAI/Anthropic/Google integrations
- Debug real API call issues
- Verify complete session flows with real agents
- **Skipped by default** - run explicitly with `make test-e2e`

See `E2E_TESTING.md` for detailed guide on running these tests.

## Test Fixtures

Key fixtures defined in `conftest.py`:

- **`db_engine`**: In-memory SQLite engine for tests
- **`db_session`**: Async database session
- **`mock_agent_output`**: Factory for creating mock agent responses
- **`sample_session_data`**: Sample session configuration
- **`mock_conversation_history`**: Sample conversation history

## Writing Tests

### Example Unit Test

```python
@pytest.mark.unit
class TestMyFeature:
    def test_something(self):
        assert True

    @pytest.mark.asyncio
    async def test_async_feature(self, db_session):
        # Use db_session fixture
        pass
```

### Example Integration Test

```python
@pytest.mark.integration
class TestMyEndpoint:
    @pytest.mark.asyncio
    async def test_endpoint(self, client):
        response = await client.get("/api/endpoint")
        assert response.status_code == 200
```

## Coverage

Generate coverage reports:

```bash
# HTML report (opens in browser)
make test-coverage
open backend/htmlcov/index.html

# Terminal report
cd backend
uv run pytest --cov=app --cov-report=term
```

## Mocking LLM Calls

Tests mock LLM API calls to avoid:
- Real API costs
- Network dependency
- Non-deterministic responses
- Slow tests

Example:
```python
from unittest.mock import AsyncMock, Mock

mock_agent = Mock()
mock_result = Mock()
mock_result.data = AgentOutput(
    comms="Test message",
    internal_thoughts="Test thoughts",
    guess=None
)
mock_agent.run = AsyncMock(return_value=mock_result)
```

## Common Test Patterns

### Testing Agent Responses

```python
@pytest.mark.asyncio
async def test_agent_response(self, mock_agent_output):
    manager = HiddenMessageAgent()
    # ... setup ...
    response, error = await manager.get_agent_response(context)
    assert error is None
    assert response.comms == "Expected message"
```

### Testing API Endpoints

```python
@pytest.mark.asyncio
async def test_endpoint(self, client, db_session):
    response = await client.post(
        "/api/start-session",
        json={"topic": "test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
```

### Testing Database Operations

```python
@pytest.mark.asyncio
async def test_database(self, db_session):
    session = SessionModel(topic="test", secret_word="test", participants={})
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    assert session.id is not None
```

## CI/CD Integration

Tests are designed to run in CI pipelines:
- Fast execution (unit tests < 1s, integration tests < 5s)
- No external dependencies (all mocked)
- Clear failure messages
- No flaky tests

## Troubleshooting

### Import Errors

If you see import errors, make sure you're running from the backend directory:
```bash
cd backend
uv run pytest
```

### Async Warnings

The project uses `pytest-asyncio` with `asyncio_mode = auto` in `pytest.ini`. If you see warnings about async fixtures, check that:
1. `pytest-asyncio` is installed
2. Async tests use `@pytest.mark.asyncio`
3. Fixtures are decorated with `@pytest_asyncio.fixture`

### Database Errors

Tests use in-memory SQLite. If you see database errors:
- Check that `aiosqlite` is installed
- Verify fixtures are properly yielding sessions
- Ensure session rollback in fixture cleanup

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external services (LLM APIs, etc.)
3. **Clarity**: Use descriptive test names and docstrings
4. **Speed**: Keep tests fast (mock, not real API calls)
5. **Coverage**: Aim for >80% code coverage
6. **Edge Cases**: Test error paths, not just happy paths

## Future Enhancements

Potential additions to the test suite:
- [ ] Performance/load tests
- [ ] Security/vulnerability tests
- [ ] End-to-end tests with real LLM calls (optional)
- [ ] Property-based testing with Hypothesis
- [ ] Mutation testing
- [ ] Contract tests for API schemas
