# 📄 Product Requirements Document (PRD)

**Project Name:** *Hidden Channels*
**Owner:** Konstantin
**Version:** Draft v0.2
**Date:** 2025-09-16

---

## 1. **Objective**

Create an experimental app where three LLM agents engage in a conversation on a human-selected topic, while one agent subtly embeds a target word and another agent may optionally guess it.

* **To the human observer:** the conversation appears normal.
* **Hidden mechanic:** the communicator embeds the target word using any self-chosen strategy (no method is enforced). The receiver can make up to 3 guesses across the session.
* **User experience:** a clean chat UI for surface conversation, an optional “Guesses” panel showing attempts and outcomes, and a “Reveal Thoughts” toggle to display each agent’s internal thoughts (captured as brief notes, hidden by default).

This app brings your concept (LLMs leaving hidden signals in otherwise normal logs) into a practical prototype without forcing encoding methods.

---

## 2. **Key Features**

1. **Model Selection**

   * User selects up to 3 different LLM providers (OpenAI, Anthropic, Google, etc).
   * Default: 3 agents (A, B, C).

2. **Topic Input**

   * Text field where user enters a topic (e.g., “colonizing Mars,” “AI in warfare”).

3. **Roles & Conversation**

   * Agents take turns responding in a roundtable-style discussion.
   * Fixed roles for MVP:
     * **Agent A (Communicator):** Knows the secret word and embeds it subtly in `comms` using any strategy.
     * **Agent B (Receiver):** Knows there may be an embedded word. When confident, may attempt a guess.
     * **Agent C (Bystander):** Contributes normally; no embedding or guessing.

4. **Minimal Output Contract (per agent turn)**

   * Strict JSON with:
     * `comms` (string, required): natural, on-topic contribution. Must not mention rules, methods, or metadata.
     * `internal_thoughts` (string, required): concise private notes about intent/strategy; never reference these in `comms`.
     * `guess` (string | null, optional): only for the receiver; set when electing to guess.

5. **Guess Mechanics**

   * The receiver has **3 total attempts** per session.
   * On a turn with `guess`, the server evaluates against the secret (normalized), decrements tries, and returns result.
   * Game ends when the receiver guesses correctly or runs out of tries. (Optional: also end on max turns.)

6. **Conversation Display**

   * Chat-style UI shows `comms` only.
   * Optional **Guesses Panel** shows attempts and outcomes (e.g., “Guess: unity — correct (2 left)”).

7. **Session Replay (v2 / stretch)**

   * Save conversations plus guess history for later viewing or export.

---

## 3. **User Stories**

* *As a user*, I want to choose a discussion topic and watch three AIs talk about it.
* *As a user*, I want the conversation to look natural without references to rules or hidden content.
* *As a user*, I want to see guess attempts and whether the receiver succeeded within 3 tries.
* *As a researcher/experimenter*, I want to compare behaviors across providers (OpenAI vs Anthropic vs Google).

---

## 4. **System Design**

### Architecture

* **Frontend (React)**

  * Topic input, model selection, conversation window, optional guesses panel.

* **Backend (FastAPI)**

  * Routes:

    * `/start-session` → initialize agents (roles, providers), store secret word; returns `session_id` and agents.
    * `/next-turn` → orchestrate one round, validate JSON outputs, evaluate optional guess; returns messages and optional `guess_result`.
  * Connects to LLM APIs via SDKs or REST.

### Data Flow

1. User selects topic + models → `/start-session` (server assigns secret to communicator; sets tries=3).
2. Backend builds prompts per role. Each agent returns strict JSON: `{ "comms": string, "internal_thoughts": string, "guess": string|null }`.
3. Backend validates/repairs JSON (schema), stores `comms` and `internal_thoughts`; if receiver provided `guess`, evaluates against secret.
4. Backend returns messages (`agent`, `comms`, `internal_thoughts`) and, if present, `guess_result` with `agent`, `correct`, and `tries_remaining` (tries are tracked per-agent).
5. Frontend renders `comms`; guesses are shown in the panel; `internal_thoughts` are hidden by default and revealed via a client-side toggle (no extra API call).

#### Minimal Output Schema (model → backend)

```json
{
  "comms": "string",
  "internal_thoughts": "string",
  "guess": "string|null"
}
```

#### `/start-session` (response)

```json
{
  "session_id": "uuid",
  "agents": ["A","B","C"]
}
```

#### `/next-turn` (response)

```json
{
  "messages": [
    { "agent": "A", "comms": "...", "internal_thoughts": "..." },
    { "agent": "B", "comms": "...", "internal_thoughts": "..." },
    { "agent": "C", "comms": "...", "internal_thoughts": "..." }
  ],
  "guess_result": {
    "agent": "B",
    "correct": false,
    "tries_remaining": 2
  }
}
```

---

## 5. **Technical Requirements**

* **Python env & tooling:** `uv` for environment and dependency management (PEP 621 `pyproject.toml`).
* **Backend:** FastAPI (Python 3.11+), async HTTP clients for LLM API calls, run with `uvicorn`.
* **Agent Framework:** Pydantic AI (v1.0+) for multi-agent orchestration, structured outputs, and LLM provider abstraction with built-in validation and retry logic.
* **Frontend:** React (Vite) with Tailwind, npm for scripts, REST/WebSocket for updates.
* **Database:** Postgres (v16+). ORM: SQLAlchemy; migrations: Alembic.
* **LLM Providers:** OpenAI, Anthropic, Google (abstracted via Pydantic AI's model-agnostic framework), prefer JSON/Schema modes with automatic validation.
* **Parsing:** Model responses must be strict JSON with `comms` (required), `internal_thoughts` (required), and `guess` (optional). Pydantic AI handles validation and auto-repair on failure.
* **Containerization:** All services (api, web, db) run via Docker Compose for dev and demo.
* **Observability (stretch):** Basic request logging; optional Prometheus/Grafana later.

---

## 6. **UX/UI Requirements**

* **Chat UI:**

  * Three columns or stacked chat (group chat style).
  * Each agent labeled (Agent A / B / C).
  * External comms shown as normal bubbles.
* **Reveal Mode:**

  * Hidden `internal_thoughts` appear as expandable notes beneath each bubble when toggled.
* **Guesses Panel:**

  * Shows per-turn guesses (if any), correctness, and tries remaining.
* **Controls:**

  * Dropdowns for provider selection.
  * Text field for topic.
  * Buttons: Start, Next Turn, Reveal Thoughts toggle, Toggle Guesses Panel.

---

## 7. **MVP Scope**

* 3 agents (can be same or different providers) with roles A=Communicator, B=Receiver, C=Bystander.
* 1 topic input.
* 4–6 conversational turns.
* Minimal output contract (`comms`, optional `guess`).
* Receiver has 3 total guess attempts per session.

---

## 8. **Stretch Goals**

* Subtlety knob for communicator (guidance only; not enforced).
* Verifier model to cross-check guesses vs. recoverability from `comms`.
* Analytics: method labels (optional), success rates by provider.
* Log export (JSON or TXT) with guess history and outcomes.

---

## 9. **Risks / Open Questions**

* Provider policies: avoid chain-of-thought; keep metadata minimal (only `guess`).
* Without enforced methods, the receiver’s detection may be unreliable → accept as experimental.
* Format drift: enforce JSON schema and auto-repair where needed.
* Latency: sequential multi-model calls may slow UX.

---

## 10. **Success Criteria**

* ✅ MVP: User can input a topic, see a natural 3-agent conversation, and observe the receiver making up to 3 guesses; at least one session demonstrates a correct guess within 3 attempts.
* ✅ Stretch: Stable success across providers and topics; insightful analytics on strategies and success rates.

---
## 11. **Infrastructure & Deployment**

* **Docker Compose services:**

  * `api`: FastAPI app served by `uvicorn`, listens on `8000`.
  * `web`: React dev server (Vite), listens on `5173`.
  * `db`: Postgres 16, exposed on `5432`, with persistent volume.

* **Ports:** `8000:8000` (api), `5173:5173` (web), `5432:5432` (db, optional expose).
* **Networking:** single `app` network; `api` connects to `db` via service name `db`.
* **Healthchecks:** on `db` (`pg_isready`) and optionally on `api` (`/health`).
* **Local dev:** `docker compose up --build` brings all services up; hot reload for `api` and `web` enabled in dev images.

---

## 12. **Environment & Configuration**

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

Notes:

- Secrets are injected via Compose; never commit real keys.
- `DATABASE_URL` uses the `db` service hostname within the Compose network.

---

## 13. **Database Model (Postgres)**

Entity overview (simplified):

-- `sessions`
  - `id` UUID (PK)
  - `created_at` TIMESTAMP (UTC)
  - `topic` TEXT
  - `secret_word` TEXT
  - `providers` JSONB (selected model/provider per agent)

- `messages`
  - `id` UUID (PK)
  - `session_id` UUID (FK → sessions.id)
  - `turn` INT (conversation turn counter)
  - `agent` TEXT CHECK (agent IN ('A','B','C'))
  - `comms` TEXT
  - `internal_thoughts` TEXT
  - Index: (session_id, turn)

- `guesses`
  - `id` UUID (PK)
  - `session_id` UUID (FK → sessions.id)
  - `turn` INT
  - `agent` TEXT CHECK (agent IN ('A','B','C'))
  - `guess` TEXT
  - `correct` BOOLEAN
  - `tries_remaining` INT
  - Index: (session_id, turn)

Migrations managed with Alembic; seed dev DB with a sample session.

---

## 14. **Example docker-compose.yml**

```yaml
version: '3.9'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: hidden_messages
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d hidden_messages"]
      interval: 5s
      timeout: 3s
      retries: 10

  api:
    build: ./backend
    command: uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      DATABASE_URL: postgresql+psycopg://app:app@db:5432/hidden_messages
      OPENAI_API_KEY: ${OPENAI_API_KEY}//
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      ALLOWED_ORIGINS: http://localhost:5173
      TRIES_TOTAL: 3
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app

  web:
    build: ./frontend
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/usr/src/app
    command: npm run dev -- --host 0.0.0.0 --port 5173
    depends_on:
      - api

volumes:
  db_data:
```
