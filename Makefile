# Hidden Channels Makefile
# Works with make (if installed) or can be run directly with commands

PYTHON_VERSION = 3.12
DOCKER_COMPOSE = docker compose

.PHONY: help install dev prod run up down build clean test test-coverage test-unit \
        test-integration test-verbose test-file test-fail-fast test-e2e test-no-e2e \
        migrate migrate-create shell-api shell-db shell-web logs logs-api logs-db logs-web \
        restart fresh health format lint test-api test-session env run-backend run-frontend \
        install-backend install-frontend

# Default target
help:
	@echo "=== Hidden Messages - Full Stack Commands ==="
	@echo ""
	@echo "Quick Start:"
	@echo "  make dev        - Start full stack for development (exposes 5173/8000)"
	@echo "  make prod       - Start full stack in detached mode for production"
	@echo "  make run        - Alias for 'make prod'"
	@echo "  make down       - Stop all services"
	@echo ""
	@echo "Installation:"
	@echo "  make install    - Install both backend and frontend dependencies"
	@echo "  make install-backend - Install Python $(PYTHON_VERSION) and backend dependencies"
	@echo "  make install-frontend - Install Node.js frontend dependencies"
	@echo ""
	@echo "Local Development (without Docker):"
	@echo "  make run-backend   - Run backend locally with uv"
	@echo "  make run-frontend  - Run frontend locally with npm"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make up         - Start all services (without rebuild)"
	@echo "  make build      - Build Docker images"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make restart    - Restart all services"
	@echo "  make fresh      - Clean and rebuild everything"
	@echo ""
	@echo "Testing:"
	@echo "  make test       - Run all backend tests (excluding e2e)"
	@echo "  make test-unit  - Run only unit tests"
	@echo "  make test-integration - Run only integration tests"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make test-e2e   - Run end-to-end tests with REAL LLM calls"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    - Run database migrations"
	@echo "  make migrate-create msg='description' - Create new migration"
	@echo ""
	@echo "Shells & Logs:"
	@echo "  make shell-api  - Open shell in API container"
	@echo "  make shell-web  - Open shell in frontend container"
	@echo "  make shell-db   - Connect to PostgreSQL"
	@echo "  make logs       - View all container logs"
	@echo "  make logs-api   - View backend API logs"
	@echo "  make logs-web   - View frontend logs"
	@echo "  make logs-db    - View database logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make health     - Check service health"
	@echo "  make format     - Format Python code"
	@echo "  make lint       - Lint Python code"

# Install all dependencies (backend + frontend)
install: install-backend install-frontend
	@echo "All dependencies installed!"

# Install backend dependencies locally
install-backend:
	@echo "Ensuring Python $(PYTHON_VERSION) is installed via uv..."
	uv python install $(PYTHON_VERSION)
	@echo "Creating virtual environment with Python $(PYTHON_VERSION) and syncing dependencies..."
	cd backend && uv venv --python $(PYTHON_VERSION) && uv sync --extra dev

# Install frontend dependencies locally
install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run full stack (frontend + backend + database)
run: prod

dev:
	@set -e; \
	if command -v tput >/dev/null 2>&1; then \
		BOLD=$$(tput bold); \
		CYAN=$$(tput setaf 6); \
		GREEN=$$(tput setaf 2); \
		YELLOW=$$(tput setaf 3); \
		BLUE=$$(tput setaf 4); \
		RESET=$$(tput sgr0); \
	else \
		BOLD=""; CYAN=""; GREEN=""; YELLOW=""; BLUE=""; RESET=""; \
	fi; \
	printf '%b' "\n$${BOLD}$${CYAN}============================================$${RESET}\n"; \
	printf '%b' "$${BOLD}$${CYAN}  Hidden Messages :: Development Stack  $${RESET}\n"; \
	printf '%b' "$${BOLD}$${CYAN}============================================$${RESET}\n\n"; \
	if [ ! -f .env ]; then \
		printf '%b' "$${YELLOW}[WARNING] No .env file detected. Copying from .env.example...$${RESET}\n"; \
		cp .env.example .env; \
		printf '%b' "$${YELLOW}         Edit .env with your API keys before running live sessions.$${RESET}\n"; \
	fi; \
	missing_keys=""; \
	if [ -f .env ]; then \
		while IFS= read -r line; do \
			case $$line in \
				OPENAI_API_KEY=*|ANTHROPIC_API_KEY=*|GOOGLE_API_KEY=*) \
					key=$${line%%=*}; \
					value=$${line#*=}; \
					[ -z "$$value" ] && missing_keys="$$missing_keys $$key"; \
			;; \
			esac; \
		done < .env; \
	fi; \
	if [ -n "$$missing_keys" ]; then \
		printf '%b' "$${YELLOW}[WARNING] Missing API keys detected:$$missing_keys$${RESET}\n"; \
		printf '%b' "$${YELLOW}         Update .env so live LLM calls can succeed (mock mode still works).$${RESET}\n"; \
	else \
		printf '%b' "$${GREEN}[OK] API keys detected in .env -- live mode ready.$${RESET}\n"; \
	fi; \
	printf '%b' "\n$${BLUE}Frontend:$${RESET} http://localhost:5173\n"; \
	printf '%b' "$${BLUE}Backend:$${RESET}  http://localhost:8000\n"; \
	printf '%b' "$${BLUE}Docs:$${RESET}     http://localhost:8000/docs\n\n"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up --build

prod:
	@echo "Starting full stack for production (detached, served via Caddy)..."
	@echo "Public site: http://localhost"
	$(DOCKER_COMPOSE) -f docker-compose.yml up --build -d

# Run backend locally (without Docker)
run-backend:
	@test -d "backend/.venv" || (echo "Virtual environment not found. Please run 'make install-backend' first." && exit 1)
	@echo "Starting backend on http://localhost:8000..."
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-config log_conf.yaml

# Run frontend locally (without Docker)
run-frontend:
	@test -d "frontend/node_modules" || (echo "Node modules not found. Please run 'make install-frontend' first." && exit 1)
	@echo "Starting frontend on http://localhost:5173..."
	cd frontend && npm run dev

# Start services without rebuilding
up:
	docker compose up -d

# Stop services
down:
	docker compose down

# Build Docker images
build:
	docker compose build

# Clean everything (including volumes)
clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# Run tests (excluding e2e by default)
test:
	cd backend && uv run pytest -m "not e2e"

# Run tests with coverage
test-coverage:
	cd backend && uv run pytest --cov=app --cov-report=html --cov-report=term

# Run only unit tests
test-unit:
	cd backend && uv run pytest -m unit

# Run only integration tests
test-integration:
	cd backend && uv run pytest -m integration

# Run tests in verbose mode
test-verbose:
	cd backend && uv run pytest -vv

# Run specific test file
test-file:
	cd backend && uv run pytest tests/$(FILE)

# Run tests and stop at first failure
test-fail-fast:
	cd backend && uv run pytest -x

# Run end-to-end tests with real LLM calls (slow, expensive)
test-e2e:
	cd backend && uv run pytest -m e2e -v -s

# Run all tests EXCEPT e2e tests (default behavior)
test-no-e2e:
	cd backend && uv run pytest -m "not e2e"

# Run database migrations
migrate:
	docker compose exec api uv run alembic upgrade head

# Create new migration
migrate-create:
	docker compose exec api uv run alembic revision --autogenerate -m "$(msg)"

# Shell into API container
shell-api:
	docker compose exec api /bin/bash

# Shell into frontend container
shell-web:
	docker compose exec web /bin/sh

# Connect to database
shell-db:
	docker compose exec db psql -U app -d hidden_messages

# View all logs
logs:
	docker compose logs -f

# View specific service logs
logs-api:
	docker compose logs -f api

logs-web:
	docker compose logs -f web

logs-db:
	docker compose logs -f db

# Restart services
restart:
	docker compose restart

# Fresh start (clean + rebuild + start)
fresh: clean
	docker compose up --build -d
	@echo "Waiting for database..."
	sleep 5
	docker compose exec api uv run alembic upgrade head
	@echo "Fresh environment ready!"

# Check service health
health:
	@echo "Checking services..."
	@curl -s http://localhost:8000/api/health || echo "API not responding"
	@docker compose ps

# Format Python code
format:
	cd backend && uv run black . && uv run ruff check --fix .

# Lint Python code
lint:
	cd backend && uv run ruff check . && uv run mypy app

# Quick API test
test-api:
	@echo "Testing API endpoint..."
	curl -X GET http://localhost:8000/api/health

# Start a new session (example)
test-session:
	curl -X POST http://localhost:8000/api/start-session \
		-H "Content-Type: application/json" \
		-d '{"topic": "colonizing Mars", "providers": {"agent_a": "openai", "agent_b": "anthropic", "agent_c": "google"}}'

# Environment setup
env:
	@test -f .env || cp .env.example .env
	@echo "Edit .env file with your API keys"