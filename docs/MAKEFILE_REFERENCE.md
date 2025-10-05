# Makefile Quick Reference

## 🚀 Quick Start Commands

### Run the Full Application
```bash
make run         # Start frontend + backend + database (Docker)
make dev         # Same as 'make run' (alias)
```

After running, access:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

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
make run         # Build and start all services (recommended)
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
# 1. Add your API keys to .env.docker
# 2. Start everything
make run

# Wait for services to start, then access:
# http://localhost:5173
```

### Daily Development
```bash
# Start your day
make run

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

## Environment Files

- **`.env.docker`** - Backend environment for Docker (add your API keys here)
- **`frontend/.env.local`** - Frontend environment for local development
- **`backend/.env.development`** - Backend environment for local development

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
make run
```

### Frontend Not Connecting to Backend
1. Check backend is running: `curl http://localhost:8000`
2. Verify `VITE_API_BASE_URL` in `frontend/.env.local`
3. Check CORS settings in backend

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
