# Demo Mode (Force Mock Mode)

## Overview

To publicly host Hidden Channels without incurring LLM API costs, you can enable **Force Mock Mode**. This hardlocks the application to demo mode, preventing real API calls while still showcasing the full conversation experience with pre-recorded responses.

## How It Works

When `VITE_FORCE_MOCK_MODE=true`:
- The mock/live toggle remains visible but is **disabled** with a tooltip explaining the lock
- "DEMO MODE" styling reinforces that the app is running on canned responses
- All API calls use mock responses (no real LLM API calls)
- Users can start sessions, run conversations, and see the mechanics
- **Zero API costs** – perfect for public demos

## Configuration

### Local Development (default)
```bash
make dev
```
This combines `docker-compose.yml` with `docker-compose.dev.yml`, exposing ports 5173/8000 and running the development commands (`npm run dev`, Uvicorn with `--reload`). All configuration still comes from `.env`, so ensure it contains development-friendly values such as:
```env
APP_ENV=development
VITE_FORCE_MOCK_MODE=false
ALLOWED_ORIGINS=http://localhost,http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
```

### Public VPS Hosting (recommended)
```bash
make prod
```
This runs the base compose file detached, serving through Caddy. On your server, configure `.env` with your production values (e.g. `APP_ENV=production`, `VITE_FORCE_MOCK_MODE=true`, `ALLOWED_ORIGINS=https://yourdomain.com`).

## Deployment Steps

1. **Copy the example environment**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` (used by both make targets) and set**:
   ```env
   APP_ENV=production
   VITE_FORCE_MOCK_MODE=true
   ALLOWED_ORIGINS=https://yourdomain.com
   ```
   Include any development origins you still rely on (e.g., `http://localhost`, `http://localhost:5173`) so the same file works for both environments.

3. **Deploy with Docker Compose**:
   ```bash
   docker compose up --build -d
   ```

4. **Verify**: Visit your site - you should see "DEMO MODE" instead of a toggle button

## Mock Mode Behavior

Mock mode provides realistic pre-scripted conversations that demonstrate:
- Agent initialization and role assignment
- Turn-based conversation flow
- Secret word embedding by the communicator
- Guess attempts by the receiver (with limited tries)
- Win/loss game states
- Internal thoughts vs public communications

## Removing the Lock

To allow real API mode (for private use or when users bring their own keys):

```env
VITE_FORCE_MOCK_MODE=false
```

Then add your API keys and redeploy.

## Future Enhancements

Consider these options if you want to offer limited live access:

- **IP Rate Limiting**: Allow 3-5 sessions per day per IP
- **BYOK (Bring Your Own Key)**: Let users provide their own API keys
- **GitHub OAuth**: Require authentication to track usage per user
- **Token System**: Generate limited-use access tokens

See the main README for more details on these approaches.
