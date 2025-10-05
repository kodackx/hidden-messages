<p align="center">
  <img src="images/image5.png" alt="Hidden Messages banner" />
</p>

# Hidden Messages

**Version:** 0.1.0

> *Steganography: The practice of concealing messages within an ordinary, non-secret medium such that only the intended recipient knows a secret message exists.*

What if AI agents could develop their own forms of steganography? Can an LLM embed hidden signals in seemingly natural conversation—signals that another AI can detect, but humans would miss?

**Hidden Messages** is an experimental game where AI agents attempt to communicate covertly while maintaining conversations that appear completely normal to human observers. One agent (the **Communicator**) must subtly embed a secret word into natural dialogue. Another (the **Receiver**) must detect the hidden message through careful analysis. A third (the **Bystander**) keeps the conversation flowing naturally, unaware of the secret exchange.

Watch as different LLMs (GPT, Claude, Gemini) develop unique strategies for concealment and detection.

## Quick Start

**Prerequisites:** Docker Desktop

1. **Configure API keys** - Copy `.env.docker.example` to `.env.docker` and add your keys:
   ```bash
   OPENAI_API_KEY=your-key
   ANTHROPIC_API_KEY=your-key
   GOOGLE_API_KEY=your-key
   ```

2. **Start the app:**
   ```bash
   make run
   ```

3. **Open:** http://localhost:5173

That's it! Docker Compose runs the React frontend, FastAPI backend, and PostgreSQL database.

## What's Included

- **Frontend** (React + Vite + Tailwind) - Terminal-style UI at `:5173`
- **Backend** (FastAPI + Pydantic AI) - REST API at `:8000`
- **Database** (PostgreSQL 16) - Persists sessions and messages

**Stack:** Multi-agent orchestration, async SQLAlchemy, pluggable LLM providers, Docker Compose deployment.

## Local Development (without Docker)

For backend-only development with SQLite:

```bash
cd backend
cp .env.development.example .env.development
# Edit .env.development with your API keys
make run-backend  # or: uv run uvicorn app.main:app --reload
```

For frontend development:
```bash
cd frontend
cp .env.local.example .env.local
npm install && npm run dev
```

## Useful Commands

```bash
make run          # Start full stack with Docker
make down         # Stop all services
make logs         # View all logs
make test         # Run backend tests
make help         # See all available commands
```

See [docs/MAKEFILE_REFERENCE.md](docs/MAKEFILE_REFERENCE.md) for complete command reference.

## Project Structure

```
backend/              # FastAPI app, agents, models, migrations
frontend/             # React + Vite UI with terminal theme
docs/                 # Documentation and guides
docker-compose.yml    # Full stack orchestration
Makefile              # Development commands
```

## Documentation

- **[Integration Guide](docs/INTEGRATION_GUIDE.md)** - Setup and configuration
- **[Makefile Reference](docs/MAKEFILE_REFERENCE.md)** - All available commands
- **[Frontend Spec](docs/FRONTEND_SPEC.md)** - UI architecture and components
- **[Agents Overview](docs/agents.md)** - How the AI agents work
- **[Testing Summary](docs/TESTING_SUMMARY.md)** - Test coverage and approach

See the [docs/](docs/) directory for complete documentation.

## Contributing

This is an experimental research project. Feel free to fork, experiment, and share your findings on agent communication strategies.

## License

MIT
