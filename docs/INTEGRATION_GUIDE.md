# Frontend-Backend Integration Guide

## Overview
This guide explains how to run the full Hidden Messages application stack with both frontend and backend integrated.

## Prerequisites
- Docker Desktop installed and running
- Git
- Your LLM API keys (OpenAI, Anthropic, and/or Google)

## Quick Start

### 1. Add Your API Keys
Copy `.env.example` to `.env` in the root directory and add your API keys:
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key-here
```

### 2. Start All Services
From the project root directory:
```bash
docker compose up --build
```

This will start:
- **PostgreSQL Database** on port 5432
- **Backend API** on port 8000
- **Frontend Web** on port 5173

### 3. Access the Application
Once all services are running:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Architecture

### Services Overview
```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Browser   │ ──────> │   Frontend  │ ──────> │   Backend   │
│             │         │   (React)   │         │  (FastAPI)  │
│ localhost:  │ <────── │             │ <────── │             │
│    5173     │         │  Port 5173  │         │  Port 8000  │
└─────────────┘         └─────────────┘         └──────┬──────┘
                                                       │
                                                       ▼
                                                ┌─────────────┐
                                                │  PostgreSQL │
                                                │   Database  │
                                                │  Port 5432  │
                                                └─────────────┘
```

### Configuration Files

#### Root Level
- **`.env`** - Shared environment variables loaded by Docker Compose
- **`docker-compose.yml`** - Orchestrates all three services

#### Frontend (`./frontend/`)
- **`.env.local`** - Local development environment variables
- **`Dockerfile`** - Multi-stage build (development & production)
- **`vite.config.ts`** - Vite development server configuration

#### Backend (`./backend/`)
- **`.env.development`** - Local development environment variables
- **`Dockerfile`** - Backend container build
- **`pyproject.toml`** - Python dependencies via uv

## Development Workflow

### Running Individual Services

#### Backend Only (Local)
```bash
cd backend
uv run uvicorn app.main:app --reload
```

#### Frontend Only (Local)
```bash
cd frontend
npm install
npm run dev
```
Make sure to create `frontend/.env.local` with:
```
VITE_API_BASE_URL=http://localhost:8000
```

#### Database Only
```bash
docker compose up db
```

### Hot Reloading
Both frontend and backend support hot reloading in development mode:
- **Frontend**: Vite watches for file changes in `./frontend/src`
- **Backend**: Uvicorn watches for changes in `./backend/app`

### Stopping Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes (clears database)
docker compose down -v
```

## Network Configuration

### CORS
The backend is configured to accept requests from:
- `http://localhost:5173` (Frontend dev server)
- `http://localhost:3000` (Alternative frontend port)

To add more origins, edit `ALLOWED_ORIGINS` in `.env`.

### Docker Network
All services communicate within a Docker bridge network named `app`:
- Frontend → Backend: `http://api:8000` (internal) or `http://localhost:8000` (external)
- Backend → Database: `postgresql+psycopg://app:app@db:5432/hidden_messages`

## Troubleshooting

### Port Conflicts
If ports are already in use:
1. Check running processes: `docker ps`
2. Stop conflicting services
3. Or modify ports in `docker-compose.yml`

### Database Connection Issues
```bash
# Check if database is healthy
docker compose ps

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

### Frontend Not Loading
1. Check browser console for API errors
2. Verify `VITE_API_BASE_URL` is correct in `.env.local`
3. Ensure backend is running: `curl http://localhost:8000`

### Backend API Errors
```bash
# View backend logs
docker compose logs api

# Check if migrations ran
docker compose exec api uv run alembic current
```

### Clean Restart
```bash
# Remove all containers, volumes, and rebuild
docker compose down -v
docker compose up --build
```

## Testing

### Backend Tests
```bash
cd backend
uv run pytest
```

### Frontend Tests
```bash
cd frontend
npm run lint
npm run build
```

## API Integration

### Frontend API Client
The frontend uses environment variables to configure the API base URL:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

### Key Endpoints
- `POST /api/start-session` - Initialize a new game session
- `POST /api/next-turn` - Progress conversation and evaluate guesses
- `GET /api/sessions/{id}` - Retrieve session details

Full API documentation available at: http://localhost:8000/docs

## Production Deployment

### Building for Production
```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Frontend production build
cd frontend
npm run build
```

The frontend Dockerfile includes a production stage that:
1. Builds optimized assets
2. Serves via Nginx
3. Reduces image size significantly

## Next Steps

1. **Configure API Keys**: Add your LLM provider API keys to `.env.docker`
2. **Start the Stack**: Run `docker compose up --build`
3. **Access Frontend**: Navigate to http://localhost:5173
4. **Test the Flow**: Start a session and watch the agents communicate
5. **Monitor Logs**: Use `docker compose logs -f` to watch all services

## Additional Resources
- Backend README: `./backend/README.md`
- Frontend README: `./frontend/README.md`
- API Documentation: http://localhost:8000/docs
- Project Overview: `./README.md`
