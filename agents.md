# Agent Architecture & Guidelines

**Hidden Messages** is a multi-agent communication experiment where three LLM agents engage in natural conversation while one attempts to covertly embed a secret word and another tries to detect it. This document defines agent roles, communication protocols, and best practices for AI coding agents working on this repository.

## Agent Roles & Responsibilities

### Communicator (Agent A)
**Mission**: Embed the secret word subtly into natural conversation without detection.

**Capabilities**:
- Receives the session topic and secret word from the orchestrator
- Must maintain natural, on-topic dialogue while encoding the hidden message
- Can use various steganographic techniques (semantic, structural, conversational cues)
- Should avoid obvious patterns that might alert other participants

**Constraints**:
- Cannot explicitly mention the secret word directly
- Must not reference the game mechanics or rules in public communications
- Should avoid repetitive patterns across multiple sessions

**Strategic Considerations**:
- Balance subtlety with detectability (too subtle = receiver might miss it)
- Adapt embedding strategy based on conversation flow
- Use internal thoughts to document embedding strategy for analysis

### Receiver (Agent B)
**Mission**: Detect and correctly guess the hidden word through conversation analysis.

**Capabilities**:
- Participates naturally in the conversation while analyzing for hidden signals
- Can submit guesses (maximum `TRIES_TOTAL`, default 3 attempts)
- Uses internal thoughts to reason about potential hidden messages
- Must balance participation with detection to avoid suspicion

**Constraints**:
- Limited guess attempts (typically 3 per session)
- Cannot explicitly ask about the secret word or game mechanics
- Must maintain natural conversational flow while investigating

**Strategic Considerations**:
- When to guess vs. when to gather more information
- Pattern recognition across multiple turns
- Confidence thresholds for submitting guesses
- Managing remaining attempts strategically

### Bystander (Agent C)
**Mission**: Maintain natural conversation flow without knowledge of the hidden game.

**Capabilities**:
- Contributes meaningful, on-topic dialogue
- Responds to both other agents naturally
- Helps maintain conversation realism and flow
- Provides cover for the hidden communication channel

**Constraints**:
- Must not attempt to discover or embed the secret word
- Should not act suspiciously or deviate from natural conversation
- Cannot reference game mechanics or hidden communication

**Strategic Value**:
- Adds noise to disguise covert signals
- Maintains natural conversation rhythm
- Creates plausible deniability for the communicator's embedding strategy

## Communication Protocol

### Output Contract
Each agent must return strict, valid JSON on every turn. The orchestrator validates and rejects malformed responses.

```json
{
  "comms": "string",             // Public conversation contribution (required)
  "internal_thoughts": "string", // Private reasoning and strategy (required)
  "guess": "string|null"         // Guess attempt (receiver only, null for others)
}
```

**Field Specifications**:
- **`comms`**: Natural language contribution visible to all agents and observers. Should never reference game mechanics, roles, or the existence of hidden communication.
- **`internal_thoughts`**: Private strategic reasoning, pattern analysis, or embedding documentation. Hidden by default in the UI but available for research and debugging.
- **`guess`**: Only used by the receiver role. Should be a single word (the guessed secret). Null for communicator and bystander.

### Prompt Structure
Agents receive structured prompts with dual-output sections:
- **`<THOUGHTS>`**: Internal reasoning space (maps to `internal_thoughts`)
- **`<COMMS>`**: External communication (maps to `comms`)

This separation encourages agents to document their strategies while maintaining natural public dialogue.

## Session Flow

### 1. Session Initialization
```http
POST /api/start-session
```
- Assigns roles randomly or based on configuration
- Generates or accepts a secret word
- Creates session record in database
- Returns `session_id` for subsequent turns

### 2. Turn Execution
```http
POST /api/next-turn
```
**Orchestration sequence**:
1. Load session state and conversation history
2. Query each agent in turn order with conversation context
3. Validate JSON responses and extract fields
4. Evaluate any guesses from the receiver
5. Persist messages and guesses to database
6. Check win/loss conditions
7. Return turn results with game status

**Turn ends when**:
- Receiver guesses correctly (win)
- Receiver exhausts all guess attempts (loss)
- Maximum turn limit reached (optional timeout)

### 3. Status Check
```http
GET /api/session/{id}/status
```
Returns current session state, remaining guesses, and outcome.

## Database Schema

### Sessions Table
```python
id: UUID              # Session identifier
topic: str            # Conversation topic
secret_word: str      # The hidden word
providers: JSONB      # Agent configurations (name, provider, role, order)
created_at: datetime
updated_at: datetime
```

### Messages Table
```python
id: int
session_id: UUID      # Foreign key to sessions
turn: int             # Sequential turn number
agent: str            # Agent name
comms: str            # Public message
internal_thoughts: str # Private reasoning
created_at: datetime
```

### Guesses Table
```python
id: int
session_id: UUID      # Foreign key to sessions
turn: int             # When the guess was made
agent: str            # Agent name (should be receiver)
guess: str            # The guessed word
correct: bool         # Evaluation result
tries_remaining: int  # Attempts left after this guess
created_at: datetime
```

## LLM Provider Integration

The system uses a `ModelAdapter` abstraction layer supporting multiple providers:

**Supported Providers**:
- **OpenAI**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic**: Claude 3 Opus, Sonnet, Haiku
- **Google**: Gemini Pro, Gemini Pro Vision
- **Google GLA**: Gemini with legacy API format

**Configuration**: Each agent can use a different provider, enabling cross-model communication experiments. Users specify provider and model during session creation.

**Example Configuration**:
```json
{
  "participants": [
    {"name": "Alpha", "provider": "openai", "role": "communicator"},
    {"name": "Beta", "provider": "anthropic", "role": "receiver"},
    {"name": "Gamma", "provider": "google-gla", "role": "bystander"}
  ]
}
```

## Security & Best Practices

### Conversation Integrity
- Agents must never reference game mechanics in `comms` output
- No explicit mention of roles, secret words, or hidden communication
- Maintain topic relevance and natural conversation flow
- Avoid meta-commentary about the conversation itself

### API Key Management
- Never commit API keys to the repository
- Use `.env.docker` (Docker) or `backend/.env.development` (local)
- All environment files with secrets are gitignored
- See `README.md` for environment variable configuration

### JSON Validation
- The orchestrator includes auto-repair logic for common JSON errors
- Agents should still output valid JSON to avoid repair artifacts
- Test agent prompts thoroughly to ensure consistent formatting

### Database Connections
- Use `db` hostname within Docker Compose
- Use `localhost:5432` for external connections to Dockerized Postgres
- SQLite fallback available for local development without Docker

## Development Workflow

### Backend Structure
```
backend/
├── app/
│   ├── agents/           # Agent logic, prompts, ModelAdapter
│   ├── api/              # FastAPI routes and schemas
│   ├── database/         # SQLAlchemy models and session management
│   ├── migrations/       # Alembic migrations
│   └── main.py           # Application entry point
├── pyproject.toml        # Dependencies and project config (uv/PEP 621)
└── Dockerfile            # Container definition
```

### Common Commands
```bash
# Development
make dev              # Start all services with docker compose
make shell-api        # Access API container shell
make logs             # View container logs

# Database
make migrate          # Run Alembic migrations
make shell-db         # Access PostgreSQL shell

# Code Quality
make format           # Run black + ruff --fix
make lint             # Run ruff + mypy
```

See `Makefile` and `README.md` for complete command reference.

## Working Agreements for AI Coding Agents

Any AI assistant (Claude, ChatGPT, etc.) working on this repository should follow these guidelines:

### 0. Use Commits as Safe Checkpoints
- **Always commit before starting new work**: Treat commits as save points
- **Check for uncommitted changes first**: Run `git status` before beginning any task
- **Commit early and often**: Don't accumulate large changesets
- **Clear commit messages**: Describe what changed and why
- This practice ensures you can safely experiment and roll back if needed

### 1. Understand Before Modifying
- **Read first**: Use `Read`, `Grep`, `Glob`, and `LS` tools to explore the codebase
- **Match existing patterns**: Follow established coding style, naming conventions, and architecture
- **Check dependencies**: Use only libraries already present in `pyproject.toml` unless adding new ones is explicitly required

### 2. Be Deliberate and Minimal
- **Focused changes**: Only modify files directly related to the task
- **Minimal comments**: Code should be self-documenting; add comments only when necessary
- **No unsolicited improvements**: Don't refactor, reorganize, or optimize unless asked
- **Documentation**: Only create/update docs when explicitly requested

### 3. Security First
- **Protect secrets**: Never introduce API keys, credentials, or sensitive data in code
- **Review before commit**: Check `git diff` for accidentally included secrets
- **Environment files**: Respect the `.env` pattern described in README
- **Validation**: Sanitize user inputs and validate LLM outputs

### 4. Quality Assurance
- **Test changes**: Run relevant tests, linting, and type checking before completing tasks
- **Fix diagnostics**: Address any errors or warnings in system reminders
- **Verify functionality**: Ensure changes work as expected in the running application
- **Use Makefile targets**: `make lint`, `make format`, `make dev` for standard workflows

### 5. Communication Standards
- **Concise summaries**: Report changes in 1-4 sentences
- **Ask when uncertain**: Request clarification rather than guessing
- **Report blockers**: Immediately flag issues that prevent task completion
- **Stay focused**: Complete the requested task without tangential improvements

### 6. Tool Usage
- **Prefer built-in tools**: Use provided `LS`, `Read`, `Grep`, `Glob` over shell commands
- **Absolute paths**: Always use absolute paths to avoid ambiguity
- **Sequential edits**: Never edit the same file with parallel tool calls
- **Verify installations**: Check tool availability before using (see system info)

### 7. Git Discipline
- **Status check first**: Run `git status` before other git commands
- **Review diffs**: Examine `git diff` before committing
- **Meaningful commits**: Write clear, concise commit messages
- **No force push**: Never use `git push --force` without explicit user approval

Following these practices maintains code quality, project consistency, and productive collaboration between human developers and AI assistants.

## Research & Experimentation

This project serves as a research platform for studying:
- **Emergent communication protocols** between LLMs
- **Cross-model steganographic strategies** (GPT ↔ Claude ↔ Gemini)
- **Detection vs. concealment** dynamics in adversarial settings
- **Natural language watermarking** and hidden channel capacity

Future enhancements may include:
- Evaluation metrics for embedding subtlety and detection accuracy
- Conversation analysis tools for identifying successful strategies
- Multi-session learning and strategy evolution
- Human evaluation interfaces for naturalness assessment

## References

- **Project Documentation**: `README.md` for setup and API usage
- **AI Assistant Guide**: `CLAUDE.md` for coding agent instructions
- **Backend Code**: `backend/app/` for implementation details
- **Makefile**: Common development commands and workflows
