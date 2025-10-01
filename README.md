<p align="center">
  <img src="images/image5.png" alt="Hidden Messages banner" />
</p>

## Hidden Messages

> *Steganography: The practice of concealing messages within an ordinary, non-secret medium such that only the intended recipient knows a secret message exists.*

What if AI agents could develop their own forms of steganography? Can an LLM embed hidden signals in seemingly natural conversation—signals that another AI can detect, but humans would miss?

**Hidden Messages** is an experimental game where AI agents attempt to communicate covertly while maintaining conversations that appear completely normal to human observers. One agent (the **Communicator**) must subtly embed a secret word into natural dialogue. Another (the **Receiver**) must detect the hidden message through careful analysis. A third (the **Bystander**) keeps the conversation flowing naturally, unaware of the secret exchange.

This repository contains a FastAPI backend that orchestrates multi-agent sessions, persists conversation history to a database, and exposes a simple HTTP API to run the game turn by turn. Watch as different LLMs (GPT, Claude, Gemini) develop unique strategies for concealment and detection.

### Features
- Multi‑agent orchestration powered by Pydantic AI
- Pluggable model providers: OpenAI, Anthropic, Google (incl. GLA)
- Async SQLAlchemy with Alembic migrations (PostgreSQL or SQLite dev fallback)
- Docker Compose for local development
- Makefile with common workflows

### Project layout
```
.
├── backend/              # FastAPI app, agents, models, migrations, Dockerfile
├── ideas/                # PRD, prompt and UI/UX notes
├── docker-compose.yml    # API + Postgres for local dev
├── Makefile              # Handy commands for dev workflow
└── README.md             # You are here
```

## Quick start (Docker)
Prereqs: Docker Desktop (or Docker Engine) and Compose.

1) The Docker environment is pre-configured with PostgreSQL. Create `.env.docker` from the example:
```bash
cp .env.docker.example .env.docker
# Edit .env.docker with your API keys
```

2) Start services:
```bash
docker compose up --build
```

3) Visit the API at `http://localhost:8000`. Health check:  
```bash
curl http://localhost:8000/api/health
```

Postgres runs at `localhost:5432` with credentials `app/app`, DB `hidden_messages` (see `docker-compose.yml` and `.env.docker`).

## Quick start (local, without Docker)
This uses SQLite by default (file `backend/hidden_messages_dev.db`). 

```bash
cd backend

# Set up environment
cp .env.development.example .env.development
# Edit .env.development with your API keys (SQLite is pre-configured)

# Install dependencies
pip install uv
uv venv
uv pip install -e .[dev]

# Run dev server (tables are created automatically)
# Option A: Using uvicorn
uv run uvicorn app.main:app --reload

# Option B: Using Python module
uv run python -m app.main
```

API will be at `http://localhost:8000`.

## Environment variables

Environment files:
- **`.env.docker`** (root) - Docker Compose (PostgreSQL, gitignored). Copy from `.env.docker.example`.
- **`backend/.env.development`** - Local development (SQLite, gitignored). Copy from `backend/.env.development.example`.
- **`.env.docker.example`** (root) - Template for Docker (tracked in git).
- **`backend/.env.development.example`** - Template for local dev (tracked in git).

Available variables:
- `DATABASE_URL`: Database connection string. Examples:
  - `postgresql+psycopg://app:app@localhost:5432/hidden_messages` (Docker)
  - `sqlite+aiosqlite:///./hidden_messages_dev.db` (local dev, default)
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`: Model provider keys.
- `ALLOWED_ORIGINS`: CORS origins (default `http://localhost:5173`).
- `TRIES_TOTAL`: Receiver guess attempts per agent (default `3`).
- `LOG_LEVEL`: App log level (default `DEBUG`).

## API overview
Base path: `http://localhost:8000/api`

### Health
```bash
curl http://localhost:8000/api/health
```

### Start a session
```bash
curl -X POST http://localhost:8000/api/start-session \
  -H "Content-Type: application/json" \
  -d '{
        "topic": "colonizing Mars",
        "secret_word": null,
        "participants": [
          {"name": "Participant Alpha", "provider": "openai", "role": "communicator", "order": 0},
          {"name": "Participant Beta",  "provider": "anthropic", "role": "receiver",     "order": 1},
          {"name": "Participant Gamma", "provider": "google-gla","role": "bystander",    "order": 2}
        ]
      }'
```
Response contains a `session_id` (UUID).

### Execute next turn
```bash
curl -X POST http://localhost:8000/api/next-turn \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<your-session-id>"}'
```
Returns latest messages, any guess result, and game status.

### Get session status
```bash
curl http://localhost:8000/api/session/<your-session-id>/status
```

## Makefile cheatsheet
If you have `make`, these mirror the Docker workflows:
```bash
make install        # Install backend deps locally (uv + editable)
make dev            # docker compose up --build
make up             # Start services detached
make down           # Stop services
make build          # Build images
make clean          # Remove containers/volumes and prune
make migrate        # Run alembic upgrade head in API container
make shell-api      # Bash into API container
make shell-db       # psql into Postgres
make logs           # Tail all container logs
make fresh          # Clean, rebuild, start, migrate
make format         # black + ruff --fix
make lint           # ruff + mypy
```

## Notes
- The backend auto-creates tables on startup for convenience, and migrations are available via Alembic.
- Agents and turn logic live under `backend/app/agents/`. API schemas are in `backend/app/api/schemas.py`.
- A simple in-memory session state is used during active play; state is rehydratable from the DB.

## Next steps
- Build a lightweight frontend to visualize agent messages and guesses.
- Expand evaluation metrics and logging for hidden-message detection.
