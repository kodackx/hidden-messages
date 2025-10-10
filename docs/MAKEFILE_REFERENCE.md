# Makefile Quick Reference

## 🚀 Quick Start Commands

### Run the Full Application
```bash
make dev         # Development stack with hot reload + direct ports (5173/8000)
make prod        # Production-style stack served via Caddy (port 80)
make run         # Alias for 'make prod'
```

After `make dev`:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

After `make prod`:
- **Public site**: http://localhost (proxied by Caddy)
- **Backend API**: proxied via `/api` on the same origin

### Stop the Application
```bash
make down        # Stop all services
```

---

## 📦 Installation

### Install Everything
```bash
make install     # Install both backend and frontend dependencies
```

### Install Individual Components
```bash
make install-backend   # Install Python 3.12 + backend dependencies
make install-frontend  # Install Node.js + frontend dependencies
```

---

## 🛠️ Local Development (Without Docker)

Run components individually on your local machine:

### Backend Only
```bash
make run-backend   # Start backend on http://localhost:8000
```
*Requires: `make install-backend` first*

### Frontend Only
```bash
make run-frontend  # Start frontend on http://localhost:5173
```
*Requires: `make install-frontend` first*

**Note**: When running locally, you'll need to start the database separately or use Docker just for the database:
```bash
docker compose up db -d
```

---

## 🐳 Docker Commands

```bash
make prod        # Build and start the production stack (recommended)
make run         # Alias for 'make prod'
make up          # Start services without rebuilding
make down        # Stop all services
make build       # Build/rebuild Docker images
make restart     # Restart all services
make clean       # Stop services and remove volumes (clears database)
make fresh       # Clean + rebuild + start + run migrations
```

---

## 🧪 Testing

```bash
make test                # Run all tests (excluding e2e)
make test-unit           # Run unit tests only
make test-integration    # Run integration tests only
make test-coverage       # Run tests with coverage report
make test-e2e            # Run end-to-end tests (real LLM calls)
make test-verbose        # Run tests with verbose output
make test-fail-fast      # Stop at first test failure
make test-file FILE=path/to/test.py  # Run specific test file
```

---

## 🗄️ Database

```bash
make migrate                         # Run pending migrations
make migrate-create msg='add users' # Create new migration
make shell-db                        # Open PostgreSQL shell
```

---

## 📊 Logs & Monitoring

```bash
make logs         # View all service logs (follow mode)
make logs-api     # View backend API logs only
make logs-web     # View frontend logs only
make logs-db      # View database logs only
make health       # Check service health status
```

---

## 🖥️ Shell Access

Access running containers:

```bash
make shell-api    # Open bash in backend container
make shell-web    # Open shell in frontend container
make shell-db     # Connect to PostgreSQL database
```

---

## 🔧 Code Quality

```bash
make format       # Format Python code (black + ruff)
make lint         # Lint Python code (ruff + mypy)
```

---

## 📝 Quick Testing

```bash
make test-api     # Quick API health check (curl)
make test-session # Start a test session via API
```

---

## Common Workflows

### First Time Setup
```bash
# 1. Add your API keys and production secrets to .env
# 2. Start the development stack
make dev

# Wait for services to start, then access:
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

### Daily Development
```bash
# Start your day
make dev

# Make code changes (hot reload is enabled)
# ...

# View logs if something goes wrong
make logs

# End your day
make down
```

### Working on Backend Only
```bash
# Start database
docker compose up db -d

# Install dependencies (first time)
make install-backend

# Run backend locally
make run-backend

# Run tests
make test
```

### Working on Frontend Only
```bash
# Start backend + database
docker compose up api db -d

# Install dependencies (first time)
make install-frontend

# Run frontend locally
make run-frontend
```

### Clean Restart (Database Reset)
```bash
make fresh    # Stops everything, removes volumes, rebuilds, and starts
```

### Debugging
```bash
# Check what's running
docker compose ps

# View specific service logs
make logs-api    # or logs-web, logs-db

# Check service health
make health

# Get into a container
make shell-api   # or shell-web, shell-db
```

---

## Environment Configuration

- **`.env`** – Single source of truth for runtime configuration (e.g., `APP_ENV`, `LOG_LEVEL`, `ALLOWED_ORIGINS`, `VITE_FORCE_MOCK_MODE`, `VITE_API_BASE_URL`, database URL, and API keys). `make dev` and `make prod` both load this file.
- **`docker-compose.dev.yml`** – Overlay used by `make dev`; it adds local port mappings (5173/8000) and swaps in development commands (`npm run dev`, Uvicorn `--reload`) while configuration still comes from `.env`.
- **Per-service overrides** – Only needed if you have advanced requirements; by default everything should live in `.env`.

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the ports
docker ps
netstat -ano | findstr :5173  # Windows
lsof -i :5173                 # Mac/Linux

# Stop conflicting services or change ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Check database health
docker compose ps

# Restart database
docker compose restart db

# Fresh database
make clean
make dev
```

### Frontend Not Connecting to Backend
1. Check backend is running: `curl http://localhost:8000`
2. If you are not using `make dev`, ensure the frontend points to the correct API base URL
3. Check backend CORS settings (`ALLOWED_ORIGINS`)

### Tests Failing
```bash
# Run with verbose output
make test-verbose

# Run specific test
make test-file FILE=tests/test_api.py

# Check test environment
cd backend && uv run pytest --version
```

---

## Help

Run `make help` or just `make` to see all available commands with descriptions.
