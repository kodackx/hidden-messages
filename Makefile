# Hidden Channels Makefile
# Works with make (if installed) or can be run directly with commands

.PHONY: help install dev up down build clean test migrate shell-api shell-db logs restart fresh

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install backend dependencies"
	@echo "  make dev        - Start development servers (Docker)"
	@echo "  make up         - Start all services (Docker)"
	@echo "  make down       - Stop all services"
	@echo "  make build      - Build Docker images"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make test       - Run backend tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make shell-api  - Open shell in API container"
	@echo "  make shell-db   - Connect to PostgreSQL"
	@echo "  make logs       - View container logs"
	@echo "  make restart    - Restart all services"
	@echo "  make fresh      - Clean and rebuild everything"

# Install dependencies locally
install:
	cd backend && pip install uv && uv venv && uv pip install -e .[dev]

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

# Run tests
test:
	cd backend && uv run pytest

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