# Hidden Channels Backend

FastAPI backend for the Hidden Channels experimental multi-agent AI communication system.

## Features

- Multi-agent orchestration using Pydantic AI
- Support for OpenAI, Anthropic, and Google AI models
- PostgreSQL database with async SQLAlchemy
- Structured JSON validation for agent outputs
- Real-time conversation tracking and guess evaluation

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+ (or use Docker)
- API keys for OpenAI, Anthropic, and/or Google AI

### Local Development

1. **Install dependencies with uv:**
   ```bash
   cd backend
   pip install uv
   uv venv
   uv pip install -e .
   ```

2. **Set up environment variables:**
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your API keys
   ```

3. **Run database migrations:**
   ```bash
   uv run alembic upgrade head
   ```

4. **Start the development server:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

### Docker Development

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start all services:**
   ```bash
   docker compose up --build
   ```

The API will be available at http://localhost:8000

## API Endpoints

### Start a Session
```http
POST /api/start-session
Content-Type: application/json

{
  "topic": "colonizing Mars",
  "providers": {
    "agent_a": "openai",
    "agent_b": "anthropic",
    "agent_c": "google"
  }
}
```

### Execute Next Turn
```http
POST /api/next-turn
Content-Type: application/json

{
  "session_id": "uuid-here"
}
```

### Get Session Status
```http
GET /api/session/{session_id}/status
```

### Health Check
```http
GET /api/health
```

## Project Structure

```
backend/
├── app/
│   ├── agents/        # Pydantic AI agent logic
│   ├── api/           # FastAPI routes
│   ├── models/        # SQLAlchemy models
│   └── main.py        # Application entry point
├── alembic/           # Database migrations
├── pyproject.toml     # Project dependencies
└── Dockerfile         # Container configuration
```

## Testing

```bash
uv run pytest
```

## Development Notes

- The system uses in-memory session state for active games
- Agent responses are validated using Pydantic models
- Automatic retry on JSON validation failures
- CORS configured for frontend at http://localhost:5173