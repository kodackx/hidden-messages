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
- API keys for OpenAI, Anthropic, and/or Google AI
- For Docker: Docker and Docker Compose

### Local Development (SQLite)

By default, the backend uses SQLite for local development. This is the quickest way to get started.

1. **Install dependencies with uv:**
   ```bash
   cd backend
   pip install uv
   uv venv
   uv pip install -e .
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.development.example .env.development
   # Edit .env.development with your API keys (SQLite is already configured)
   ```

3. **Start the development server:**
   
   **Option A - Using uvicorn directly:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   
   **Option B - Using Python module:**
   ```bash
   uv run python -m app.main
   ```
   
   Both methods will auto-reload on code changes. The database tables will be created automatically on first run.

### Docker Development (PostgreSQL)

For a production-like environment with PostgreSQL, use Docker Compose:

1. **Set up environment:**
   ```bash
   cd ..  # Go to project root
   cp .env.docker.example .env.docker
   # Edit .env.docker with your API keys (PostgreSQL is pre-configured)
   ```

2. **Start all services:**
   ```bash
   docker compose up --build
   ```

   This will start:
   - PostgreSQL database on port 5432
   - FastAPI backend on port 8000

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

## Database Configuration

The backend supports both SQLite and PostgreSQL:

- **SQLite (Local Development)**: Configured in `.env.development` file with `DATABASE_URL=sqlite+aiosqlite:///./hidden_messages_dev.db`
- **PostgreSQL (Docker)**: Configured in root `.env.docker` file with `DATABASE_URL=postgresql+psycopg://app:app@db:5432/hidden_messages`

The application automatically detects the database type from the `DATABASE_URL` environment variable and uses the appropriate async driver (aiosqlite or asyncpg).

### Environment Files

- `backend/.env.development` - Local development configuration (uses SQLite, gitignored)
- `.env.docker` (root) - Docker configuration (uses PostgreSQL, gitignored)
- `backend/.env.development.example` - Template file for local development (tracked in git)
- `.env.docker.example` (root) - Template file for Docker setup (tracked in git)

## Development Notes

- The system uses in-memory session state for active games
- Agent responses are validated using Pydantic models
- Automatic retry on JSON validation failures
- CORS configured for frontend at http://localhost:5173
- Database tables are created automatically on application startup