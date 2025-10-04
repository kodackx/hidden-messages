# Hidden Channels Makefile
# Works with make (if installed) or can be run directly with commands

PYTHON_VERSION = 3.12

.PHONY: help install dev up down build clean test test-coverage test-unit \
        test-integration test-verbose test-file test-fail-fast test-e2e test-no-e2e \
        migrate migrate-create shell-api shell-db logs logs-api logs-db restart fresh \
        health format lint test-api test-session env run-backend run-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install Python $(PYTHON_VERSION) (if needed) and dependencies via uv"
	@echo "  make run-backend- Run the backend locally using uv"
	@echo "  make run-dev    - Run backend with Python directly (more verbose logs)"
	@echo "  make dev        - Start development servers (Docker)"
	@echo "  make up         - Start all services (Docker)"
	@echo "  make down       - Stop all services"
	@echo "  make build      - Build Docker images"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make test       - Run all backend tests (excluding e2e)"
	@echo "  make test-unit  - Run only unit tests"
	@echo "  make test-integration - Run only integration tests"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make test-e2e   - Run end-to-end tests with REAL LLM calls"
	@echo "  make migrate    - Run database migrations"
	@echo "  make shell-api  - Open shell in API container"
	@echo "  make shell-db   - Connect to PostgreSQL"
	@echo "  make logs       - View container logs"
	@echo "  make restart    - Restart all services"
	@echo "  make fresh      - Clean and rebuild everything"

# Install dependencies locally
install:
	@echo "Ensuring Python $(PYTHON_VERSION) is installed via uv..."
	uv python install $(PYTHON_VERSION)
	@echo "Creating virtual environment with Python $(PYTHON_VERSION) and syncing dependencies..."
	cd backend && uv venv --python $(PYTHON_VERSION) && uv sync --extra dev

# Run backend locally
run-backend:
	@test -d "backend/.venv" || (echo "Virtual environment not found. Please run 'make install' first." && exit 1)
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-config log_conf.yaml

# Run backend with Python directly (even more verbose)
run-dev:
	@test -d "backend/.venv" || (echo "Virtual environment not found. Please run 'make install' first." && exit 1)
	cd backend && uv run python -m app.main

# Start development environment
dev:
	docker compose up --build

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

# Connect to database
shell-db:
	docker compose exec db psql -U app -d hidden_messages

# View logs
logs:
	docker compose logs -f

# View specific service logs
logs-api:
	docker compose logs -f api

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