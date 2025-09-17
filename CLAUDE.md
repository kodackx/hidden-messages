# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Hidden Channels" - an experimental application where three LLM agents engage in conversations while one agent subtly embeds a target word and another agent attempts to guess it. The conversation should appear natural to human observers while containing hidden communication channels between the agents.

## Architecture

The project follows a modern full-stack architecture:

- **Backend**: FastAPI (Python 3.11+) with async HTTP clients for LLM API calls
- **Frontend**: React with Vite and Tailwind CSS
- **Database**: PostgreSQL 16 with SQLAlchemy ORM and Alembic migrations
- **Containerization**: Docker Compose for all services (api, web, db)
- **Python Environment**: `uv` for dependency management (PEP 621 `pyproject.toml`)

## Agent Roles & Communication Protocol

### Agent Roles
- **Agent A (Communicator)**: Embeds a secret word subtly in communications
- **Agent B (Receiver)**: Attempts to detect and guess the hidden word (3 attempts max)
- **Agent C (Bystander)**: Participates normally without embedding/guessing

### Output Contract
Each agent must return strict JSON:
```json
{
  "comms": "string",           // Natural conversation contribution
  "internal_thoughts": "string", // Private strategy notes (hidden by default)
  "guess": "string|null"       // Optional guess (receiver only)
}
```

## Key API Endpoints

- `/start-session`: Initialize agents, assign roles, store secret word
- `/next-turn`: Orchestrate conversation rounds, evaluate guesses

## Database Schema

- **sessions**: `id`, `topic`, `secret_word`, `providers` (JSONB)
- **messages**: `session_id`, `turn`, `agent`, `comms`, `internal_thoughts`
- **guesses**: `session_id`, `turn`, `agent`, `guess`, `correct`, `tries_remaining`

## Development Commands

### Environment Setup
```bash
# Start all services
docker compose up --build

# Backend development (when implemented)
cd backend
uv run uvicorn app.main:app --reload

# Frontend development (when implemented)
cd frontend
npm run dev
```

### Service Ports
- API: http://localhost:8000
- Web: http://localhost:5173
- Database: localhost:5432

## Environment Variables

Backend (.env):
```
DATABASE_URL=postgresql+psycopg://app:app@db:5432/hidden_messages
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
ALLOWED_ORIGINS=http://localhost:5173
TRIES_TOTAL=3
```

Frontend (.env.local):
```
VITE_API_BASE_URL=http://localhost:8000
```

## LLM Provider Integration

The system supports multiple LLM providers (OpenAI, Anthropic, Google) abstracted via `ModelAdapter`. Users can select different providers for each agent to experiment with cross-model communication strategies.

## Prompt Structure

Agents use a dual-output structure with `<THOUGHTS>` for internal reasoning and `<COMMS>` for external communication. The frontend has a "Reveal Thoughts" toggle to show/hide internal thoughts.

## Security & Best Practices

- Never commit API keys to the repository
- Use the `db` service hostname for database connections within Docker Compose
- Validate and auto-repair JSON responses from LLM APIs
- Keep conversations natural - agents must not reference rules or hidden mechanics in public communications