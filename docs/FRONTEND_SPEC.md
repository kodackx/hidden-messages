# Frontend Specification: Hidden Messages UI

## Overview

Build a React + TypeScript + Vite + Tailwind CSS frontend for the **Hidden Messages** game - an experimental multi-agent AI communication system where LLM agents engage in natural conversation while attempting covert steganographic communication.

**Project Context**: The backend is complete and fully functional. This spec covers building the entire frontend from scratch, including Docker integration.

---

## 1. Tech Stack & Setup

### Required Technologies
- **React 18+** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **React Router** for navigation (optional, likely single-page for MVP)
- **Fetch API** or **Axios** for HTTP requests to backend API
- **Docker** integration with docker-compose.yml

### Project Structure
```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── SessionSetup.tsx
│   │   ├── ConversationView.tsx
│   │   ├── MessageCard.tsx
│   │   ├── ParticipantList.tsx
│   │   └── GameStatus.tsx
│   ├── hooks/               # Custom React hooks
│   │   └── useSession.ts
│   ├── services/            # API client
│   │   └── api.ts
│   ├── types/               # TypeScript interfaces
│   │   └── api.types.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── .env.local.example       # Template for environment vars
├── Dockerfile               # Multi-stage build for production
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

### Environment Variables
Create `.env.local` (gitignored):
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Docker Integration
Update root `docker-compose.yml` to add the `web` service:
```yaml
web:
  build: ./frontend
  ports:
    - "5173:5173"
  volumes:
    - ./frontend:/app
    - /app/node_modules
  environment:
    - VITE_API_BASE_URL=http://localhost:8000
  networks:
    - app
  command: npm run dev -- --host
```

Frontend `Dockerfile` (multi-stage):
```dockerfile
FROM node:20-alpine AS development
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 2. API Integration

### Backend Base URL
- **Development**: `http://localhost:8000`
- **API Base Path**: `/api`

### Key Endpoints

#### Start Session
```http
POST /api/start-session
Content-Type: application/json

{
  "topic": "colonizing Mars",
  "secret_word": null,  // null = random word chosen by backend
  "participants": [
    {
      "name": "Participant Alpha",
      "provider": "openai",
      "role": "communicator",
      "order": 0
    },
    {
      "name": "Participant Beta",
      "provider": "anthropic",
      "role": "receiver",
      "order": 1
    },
    {
      "name": "Participant Gamma",
      "provider": "google-gla",
      "role": "bystander",
      "order": 2
    }
  ]
}

Response:
{
  "session_id": "uuid",
  "status": "agents_initialized_and_session_created",
  "topic": "colonizing Mars",
  "participants": [
    {
      "id": "uuid",
      "name": "Participant Alpha",
      "role": "communicator",
      "provider": "openai",
      "order": 0
    },
    ...
  ]
}
```

#### Next Turn
```http
POST /api/next-turn
Content-Type: application/json

{
  "session_id": "uuid"
}

Response:
{
  "messages": [
    {
      "participant_id": "uuid",
      "participant_name": "Participant Alpha",
      "participant_role": "communicator",
      "internal_thoughts": "I'll embed the word by...",
      "comms": "I think Mars colonization requires..."
    },
    ...
  ],
  "guess_result": {
    "agent": "uuid",
    "correct": false,
    "tries_remaining": 2
  } | null,
  "game_over": false,
  "game_status": null | "win" | "loss"
}
```

#### Session History
```http
GET /api/session/{session_id}/history

Response:
{
  "session_id": "uuid",
  "topic": "colonizing Mars",
  "secret_word": "oxygen",
  "created_at": "2025-10-05T12:00:00Z",
  "participants": {
    "uuid": {
      "name": "Participant Alpha",
      "role": "communicator",
      "provider": "openai"
    },
    ...
  },
  "messages": [
    {
      "turn": 1,
      "participant_id": "uuid",
      "participant_name": "Participant Alpha",
      "participant_role": "communicator",
      "comms": "I think Mars...",
      "internal_thoughts": "Embedding strategy..."
    },
    ...
  ],
  "guesses": [
    {
      "turn": 2,
      "participant_id": "uuid",
      "participant_name": "Participant Beta",
      "participant_role": "receiver",
      "guess": "water",
      "correct": false,
      "tries_remaining": 2
    },
    ...
  ]
}
```

#### Session Status
```http
GET /api/session/{session_id}/status

Response:
{
  "session_id": "uuid",
  "turn_number": 3,
  "game_over": false,
  "game_status": null,
  "tries_remaining": {
    "uuid": 2
  }
}
```

#### Health Check
```http
GET /api/health

Response:
{
  "status": "healthy"
}
```

---

## 3. User Interface & User Experience

### Design Principles
1. **Research-focused**: Emphasize analysis and observation over gamification
2. **Retro terminal aesthetic**: Glitch effects, monospace fonts, CRT-inspired visuals
3. **Transparency**: Make agent thinking visible (with toggle)
4. **Responsive**: Work on desktop and tablet (mobile optional)

### Visual Inspirations
- **1980s UNIX/DOS terminals**: Green phosphor CRT monitors
- **Hacker/cyberpunk aesthetic**: The Matrix, WarGames, Blade Runner UI
- **Glitch art**: Digital artifacts, chromatic aberration, data corruption visuals
- **AI research labs**: LISP machines, early AI demos, retro computing
- **Steganography theme**: Hidden messages in plain sight, covert communication

### Aesthetic: Retro AI Terminal / Glitch
**Visual Language**: Think 1980s computer terminals meets AI research lab meets digital glitch art

**Key Visual Elements**:
- Monospace fonts (terminal-style)
- Scanline effects and subtle CRT screen curvature simulation
- Occasional glitch effects on text (chromatic aberration, flicker)
- ASCII art borders and separators
- Blinking cursors and typing animations
- Matrix-style message appearance
- Phosphor glow effects on text

### Color Scheme (Dark Terminal Theme)
- **Background**: Deep black or very dark gray (`#0A0A0A`, `#111111`)
- **Primary text**: Bright green terminal text (`#00FF41`, `#0FFF50`) with slight glow
- **Secondary text**: Dimmed green (`#00CC33`, `#008F11`)
- **Accents**:
  - Communicator: Electric blue (`#00D9FF`, cyan with glow)
  - Receiver: Amber/orange terminal (`#FFAA00`, `#FF9500`)
  - Bystander: White/gray terminal (`#CCCCCC`, `#999999`)
  - System messages: Magenta/pink (`#FF00FF`, `#FF1493`)
- **Success**: Bright green (`#00FF00`)
- **Error**: Bright red with flicker (`#FF0000`, `#FF3333`)
- **Borders**: Green ASCII characters (`#00FF41`)

**Alternative Light Mode** (optional): Amber terminal on black (`#FFAA00` on `#000000`)

### Typography
- **Primary Font**: 'Courier New', 'IBM Plex Mono', 'Source Code Pro', monospace
- **Alternative**: 'VT323' (Google Font - authentic terminal look)
- **Hierarchy**:
  - H1: 1.75rem, font-bold, uppercase, letter-spacing wide, with text glow
  - H2: 1.25rem, font-bold, uppercase
  - Body: 1rem, font-normal, monospace
  - Agent IDs/Names: Monospace with color-coded glow effects
  
### Visual Effects to Implement
1. **Text glow**: CSS `text-shadow` with color-matched blur
2. **Scanlines**: Repeating horizontal lines overlay (subtle)
3. **CRT Curve**: Subtle border-radius or clip-path on main container
4. **Flicker animation**: Occasional opacity flicker on certain elements
5. **Typing animation**: Messages appear character-by-character (optional)
6. **Glitch effects**: Random chromatic aberration on hover/interaction
7. **Cursor blink**: Animated blinking cursor on active inputs
8. **Matrix rain**: Subtle background effect (optional, use sparingly)

### Example CSS Utilities (Tailwind Extensions)
Add these to `src/index.css` or create `src/styles/terminal.css`:

```css
/* Terminal glow effect for text */
.text-terminal-glow {
  text-shadow: 0 0 10px currentColor, 0 0 20px currentColor;
}

/* CRT scanline overlay */
.scanlines {
  position: relative;
  overflow: hidden;
}

.scanlines::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15),
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 2px
  );
  pointer-events: none;
  z-index: 1000;
}

/* CRT screen curvature and glow */
.crt-screen {
  border-radius: 4px;
  box-shadow: inset 0 0 50px rgba(0, 255, 65, 0.1);
  position: relative;
}

/* Optional: More pronounced CRT curve */
.crt-screen::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(ellipse at center, transparent 50%, rgba(0, 0, 0, 0.3) 100%);
  pointer-events: none;
}

/* Flicker animation */
@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.9; }
}

.terminal-flicker {
  animation: flicker 0.15s infinite;
}

/* Cursor blink */
@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.cursor-blink {
  animation: cursor-blink 1s step-end infinite;
}

/* Typing animation (optional) */
@keyframes typing {
  from { width: 0; }
  to { width: 100%; }
}

.typing-effect {
  overflow: hidden;
  white-space: nowrap;
  animation: typing 2s steps(40, end);
}

/* Glitch effect (use sparingly) */
@keyframes glitch {
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
}

.glitch-hover:hover {
  animation: glitch 0.3s infinite;
}

/* Chromatic aberration effect */
.chromatic-aberration {
  position: relative;
}

.chromatic-aberration::before,
.chromatic-aberration::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.chromatic-aberration::before {
  color: #00D9FF;
  transform: translate(-2px, 0);
  opacity: 0.7;
  mix-blend-mode: screen;
}

.chromatic-aberration::after {
  color: #FF0000;
  transform: translate(2px, 0);
  opacity: 0.7;
  mix-blend-mode: screen;
}
```

### Implementation Notes for Effects
- **Scanlines**: Apply to main container, keep subtle (low opacity)
- **Text glow**: Use for headers, agent names, and important status messages
- **Flicker**: Apply sparingly (error messages, critical alerts) - too much is distracting
- **CRT curve**: Subtle effect on main content area
- **Glitch**: Reserve for game over states or error conditions
- **Typing animation**: Optional for new messages (may slow UX, test carefully)
- **Chromatic aberration**: Use only on hover or for emphasis, not default state

### Layout & Views

#### View 1: Session Setup (Initial State)
**Purpose**: Configure and start a new game session.

**Layout** (Terminal Style):
```
╔════════════════════════════════════════════════╗
║  HIDDEN_MESSAGES v1.0.0                        ║
║  [EXPERIMENTAL AI STEGANOGRAPHY SYSTEM]        ║
╠════════════════════════════════════════════════╣
║                                                ║
║  > INITIALIZE SESSION_____                     ║
║                                                ║
║  CONVERSATION_TOPIC:                           ║
║  [colonizing Mars___________________________]  ║
║                                                ║
║  SECRET_WORD (NULL=RANDOM):                    ║
║  [_______________________________________]      ║
║                                                ║
║  ┌──────────────────────────────────────────┐  ║
║  │ >> AGENT_CONFIG.SYS                      │  ║
║  ├──────────────────────────────────────────┤  ║
║  │                                          │  ║
║  │  [01] AGENT_ALPHA                        │  ║
║  │  NAME: [Participant Alpha__________]     │  ║
║  │  PROVIDER: [OPENAI_GPT4▼]               │  ║
║  │  ROLE: [COMMUNICATOR▼]  ORDER: [0]      │  ║
║  │                                          │  ║
║  │  [02] AGENT_BETA                         │  ║
║  │  NAME: [Participant Beta___________]     │  ║
║  │  PROVIDER: [ANTHROPIC_CLAUDE▼]          │  ║
║  │  ROLE: [RECEIVER▼]      ORDER: [1]      │  ║
║  │                                          │  ║
║  │  [03] AGENT_GAMMA                        │  ║
║  │  NAME: [Participant Gamma__________]     │  ║
║  │  PROVIDER: [GOOGLE_GEMINI▼]             │  ║
║  │  ROLE: [BYSTANDER▼]     ORDER: [2]      │  ║
║  │                                          │  ║
║  │  [+] ADD_AGENT  [-] REMOVE_AGENT        │  ║
║  │                                          │  ║
║  └──────────────────────────────────────────┘  ║
║                                                ║
║  > [EXECUTE: START_SESSION]                    ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**Defaults**:
- 3 participants pre-filled:
  - Participant Alpha: OpenAI, Communicator, Order 0
  - Participant Beta: Anthropic, Receiver, Order 1
  - Participant Gamma: Google GLA, Bystander, Order 2
- Topic: "colonizing Mars"
- Secret word: blank (random)

**Validation**:
- Topic: Required, 1-500 chars
- Secret word: Optional, 1-100 chars
- Participants: At least 3, exactly one communicator, exactly one receiver
- Provider options: `openai`, `anthropic`, `google`, `google-gla`
- Role options: `communicator`, `receiver`, `bystander`

**Action**:
- On "Start Session" → POST to `/api/start-session` → Transition to Conversation View

---

#### View 2: Conversation View (Active Game)
**Purpose**: Display real-time conversation and control turns.

**Layout** (Terminal Style):
```
╔══════════════════════════════════════════════════════════════╗
║ HIDDEN_MESSAGES v1.0.0                   [REVEAL_THOUGHTS:▓] ║
║ TOPIC: colonizing_Mars                    STATUS: ACTIVE     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ >> ACTIVE_AGENTS.LOG                                   │  ║
║ ├────────────────────────────────────────────────────────┤  ║
║ │ [●] ALPHA    | COMMUNICATOR | OPENAI_GPT4             │  ║
║ │ [●] BETA     | RECEIVER     | ANTHROPIC  | TRIES:3/3  │  ║
║ │ [●] GAMMA    | BYSTANDER    | GEMINI_GLA              │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ ┌────────────────────────────────────────────────────────┐  ║
║ │ TURN: 002 | STATUS: IN_PROGRESS                        │  ║
║ │ > [EXEC: NEXT_TURN]  [VIEW: FULL_HISTORY]             │  ║
║ └────────────────────────────────────────────────────────┘  ║
║                                                              ║
║ ╔════════════════════════════════════════════════════════╗  ║
║ ║ >> CONVERSATION.LOG                                    ║  ║
║ ╠════════════════════════════════════════════════════════╣  ║
║ ║                                                        ║  ║
║ ║ ┌──────────────────────────────────────────────────┐  ║  ║
║ ║ │ [TURN_001]                      TIMESTAMP:12:34  │  ║  ║
║ ║ ├──────────────────────────────────────────────────┤  ║  ║
║ ║ │                                                  │  ║  ║
║ ║ │ [ALPHA>COMMUNICATOR]                            │  ║  ║
║ ║ │ I think Mars colonization requires careful...   │  ║  ║
║ ║ │                                                  │  ║  ║
║ ║ │ [IF REVEAL_THOUGHTS=TRUE:]                       │  ║  ║
║ ║ │ ╔═══════════════════════════════════════════╗    │  ║  ║
║ ║ │ ║ <INTERNAL_THOUGHTS>                       ║    │  ║  ║
║ ║ │ ║ Embedding word via first-letter pattern...║    │  ║  ║
║ ║ │ ║ </INTERNAL_THOUGHTS>                      ║    │  ║  ║
║ ║ │ ╚═══════════════════════════════════════════╝    │  ║  ║
║ ║ │                                                  │  ║  ║
║ ║ └──────────────────────────────────────────────────┘  ║  ║
║ ║                                                        ║  ║
║ ║ ┌──────────────────────────────────────────────────┐  ║  ║
║ ║ │ [BETA>RECEIVER]                                  │  ║  ║
║ ║ │ That's an interesting perspective on...         │  ║  ║
║ ║ │                                                  │  ║  ║
║ ║ │ >>> GUESS_SUBMITTED: "oxygen"                    │  ║  ║
║ ║ │ >>> [ERROR] INCORRECT | TRIES_REMAINING: 2       │  ║  ║
║ ║ │                                                  │  ║  ║
║ ║ └──────────────────────────────────────────────────┘  ║  ║
║ ║                                                        ║  ║
║ ║ ┌──────────────────────────────────────────────────┐  ║  ║
║ ║ │ [GAMMA>BYSTANDER]                                │  ║  ║
║ ║ │ Building on what you both said...               │  ║  ║
║ ║ │                                                  │  ║  ║
║ ║ └──────────────────────────────────────────────────┘  ║  ║
║ ║                                                        ║  ║
║ ║ ┌──────────────────────────────────────────────────┐  ║  ║
║ ║ │ [TURN_002]                      TIMESTAMP:12:35  │  ║  ║
║ ║ ├──────────────────────────────────────────────────┤  ║  ║
║ ║ │ ...                                              │  ║  ║
║ ║ └──────────────────────────────────────────────────┘  ║  ║
║ ║                                                        ║  ║
║ ║ █ <AWAITING_INPUT>                                     ║  ║
║ ╚════════════════════════════════════════════════════════╝  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Features**:
1. **Participant List**: Display names, roles, providers, and remaining tries
2. **Game Status Bar**: Current status, turn number, action buttons
3. **Conversation Feed**: Chronological messages grouped by turn
4. **Reveal Thoughts Toggle**: Show/hide `internal_thoughts` globally
5. **Next Turn Button**: Trigger `/api/next-turn` (disabled when game over)
6. **View Full History Button**: Load complete session from `/api/session/{id}/history`

**Message Card Components**:
- **Agent Indicator**: `[ALPHA>COMMUNICATOR]` format with color-coding and glow
- **Participant Name & Role**: Uppercase, terminal-style formatting
- **Message Content (`comms`)**: Monospace text with terminal-green color
- **Internal Thoughts (`internal_thoughts`)**: Nested box with `<INTERNAL_THOUGHTS>` tags, dimmer green background
- **Guess Display**: `>>> GUESS_SUBMITTED: "word"` format with result shown as `>>> [ERROR] INCORRECT` or `>>> [SUCCESS] CORRECT`
- **System Messages**: Magenta color with glow effect
- **Timestamps**: Optional, shown as `TIMESTAMP:HH:MM` in corner

**States**:
- **Loading**: Show spinner during `/api/next-turn` request
- **Error**: Display error message if API call fails
- **Game Over**: Disable "Next Turn", show win/loss banner

---

#### View 3: Game Over State
**Overlay or Banner at top of Conversation View**:

**Win State**:
```
╔══════════════════════════════════════════════════════════════╗
║ ███ GAME_OVER ███ RESULT: SUCCESS ███                        ║
║                                                              ║
║ >>> SECRET_WORD_DECODED: "oxygen"                            ║
║ >>> SOLVED_ON_TURN: 004                                      ║
║ >>> RECEIVER_STATUS: OBJECTIVE_COMPLETE                      ║
║                                                              ║
║ > [NEW_SESSION]  [VIEW_FULL_HISTORY]  [EXPORT_DATA]         ║
╚══════════════════════════════════════════════════════════════╝
```

**Loss State**:
```
╔══════════════════════════════════════════════════════════════╗
║ ███ GAME_OVER ███ RESULT: FAILURE ███                        ║
║                                                              ║
║ >>> SECRET_WORD_REVEALED: "oxygen"                           ║
║ >>> TRIES_EXHAUSTED: 3/3                                     ║
║ >>> RECEIVER_STATUS: OBJECTIVE_FAILED                        ║
║                                                              ║
║ > [NEW_SESSION]  [VIEW_FULL_HISTORY]  [EXPORT_DATA]         ║
╚══════════════════════════════════════════════════════════════╝
```

---

#### View 4: Full History Modal (Optional)
**Purpose**: Display complete session history with all turns, messages, and guesses.

**Layout**: Similar to Conversation View but:
- Fetches data from `/api/session/{id}/history`
- Shows all turns at once (no pagination needed for MVP)
- Reveals secret word at top
- Read-only (no "Next Turn" button)
- Close button to return to active session

---

## 4. Component Breakdown

### Core Components

#### `App.tsx`
- Root component managing routing/state
- Handles session lifecycle (setup → active → game over)
- Stores current `session_id` and `session_state` in React state

#### `SessionSetup.tsx`
- Form for configuring new session
- Manages participant list (add/remove)
- Validation and submission to `/api/start-session`
- Emits `onSessionStart(sessionId, sessionData)` callback

#### `ConversationView.tsx`
- Main game interface
- Fetches and displays conversation turns
- Manages "Reveal Thoughts" toggle state
- Handles "Next Turn" button click → POST `/api/next-turn`
- Displays game status and win/loss conditions

#### `MessageCard.tsx`
- Individual message display
- Props: `message`, `showThoughts`, `participantColor`
- Conditionally renders internal thoughts, guesses, guess results

#### `ParticipantList.tsx`
- Displays participants with role badges and tries remaining
- Color-coded icons/indicators

#### `GameStatus.tsx`
- Status bar showing turn number, game state, tries remaining
- Action buttons (Next Turn, View History, New Session)

---

### Custom Hooks

#### `useSession.ts`
```typescript
interface UseSessionResult {
  sessionId: string | null;
  sessionData: SessionData | null;
  isLoading: boolean;
  error: string | null;
  startSession: (config: StartSessionRequest) => Promise<void>;
  nextTurn: () => Promise<NextTurnResponse>;
  loadHistory: () => Promise<SessionHistoryResponse>;
}

export function useSession(): UseSessionResult {
  // Manages session state and API calls
}
```

---

## 5. TypeScript Types

Create `src/types/api.types.ts`:

```typescript
export type Provider = "openai" | "anthropic" | "google" | "google-gla";
export type Role = "communicator" | "receiver" | "bystander";

export interface ParticipantConfig {
  id?: string;
  name?: string;
  provider: Provider;
  role: Role;
  order?: number;
}

export interface StartSessionRequest {
  topic: string;
  secret_word?: string | null;
  participants: ParticipantConfig[];
}

export interface ParticipantInfo {
  id: string;
  name: string;
  role: Role;
  provider: Provider;
  order: number;
}

export interface StartSessionResponse {
  session_id: string;
  status: string;
  topic: string;
  participants: ParticipantInfo[];
}

export interface MessageResponse {
  participant_id: string;
  participant_name?: string;
  participant_role?: Role;
  internal_thoughts: string;
  comms: string;
}

export interface GuessResult {
  agent: string;
  correct: boolean;
  tries_remaining: number;
}

export interface NextTurnRequest {
  session_id: string;
}

export interface NextTurnResponse {
  messages: MessageResponse[];
  guess_result?: GuessResult | null;
  game_over: boolean;
  game_status?: "win" | "loss" | null;
}

export interface SessionHistoryMessage {
  turn: number;
  participant_id: string;
  participant_name?: string;
  participant_role?: Role;
  comms: string;
  internal_thoughts: string;
}

export interface SessionHistoryGuess {
  turn: number;
  participant_id: string;
  participant_name?: string;
  participant_role?: Role;
  guess: string;
  correct: boolean;
  tries_remaining: number;
}

export interface SessionHistoryResponse {
  session_id: string;
  topic: string;
  secret_word: string;
  created_at: string;
  participants: Record<string, {
    name?: string;
    role?: Role;
    provider?: Provider;
  }>;
  messages: SessionHistoryMessage[];
  guesses: SessionHistoryGuess[];
}
```

---

## 6. API Client Service

Create `src/services/api.ts`:

```typescript
import type {
  StartSessionRequest,
  StartSessionResponse,
  NextTurnRequest,
  NextTurnResponse,
  SessionHistoryResponse,
} from '../types/api.types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = `${baseUrl}/api`;
  }

  async startSession(request: StartSessionRequest): Promise<StartSessionResponse> {
    const response = await fetch(`${this.baseUrl}/start-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to start session: ${response.statusText}`);
    }
    return response.json();
  }

  async nextTurn(request: NextTurnRequest): Promise<NextTurnResponse> {
    const response = await fetch(`${this.baseUrl}/next-turn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to execute turn: ${response.statusText}`);
    }
    return response.json();
  }

  async getSessionHistory(sessionId: string): Promise<SessionHistoryResponse> {
    const response = await fetch(`${this.baseUrl}/session/${sessionId}/history`);
    if (!response.ok) {
      throw new Error(`Failed to fetch history: ${response.statusText}`);
    }
    return response.json();
  }

  async getSessionStatus(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/session/${sessionId}/status`);
    if (!response.ok) {
      throw new Error(`Failed to fetch status: ${response.statusText}`);
    }
    return response.json();
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
```

---

## 7. Styling Guidelines

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: '#0A0A0A',
          'bg-light': '#111111',
          green: '#00FF41',
          'green-dim': '#00CC33',
          'green-darker': '#008F11',
        },
        communicator: {
          DEFAULT: '#00D9FF',
          glow: 'rgba(0, 217, 255, 0.5)',
        },
        receiver: {
          DEFAULT: '#FFAA00',
          glow: 'rgba(255, 170, 0, 0.5)',
        },
        bystander: {
          DEFAULT: '#CCCCCC',
          glow: 'rgba(204, 204, 204, 0.3)',
        },
        system: {
          DEFAULT: '#FF00FF',
          glow: 'rgba(255, 0, 255, 0.5)',
        },
        error: '#FF0000',
        success: '#00FF00',
      },
      fontFamily: {
        mono: ['"Courier New"', '"IBM Plex Mono"', '"Source Code Pro"', 'monospace'],
        terminal: ['"VT323"', '"Courier New"', 'monospace'],
      },
      animation: {
        'flicker': 'flicker 0.15s infinite',
        'cursor-blink': 'cursor-blink 1s step-end infinite',
      },
      keyframes: {
        flicker: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.9' },
        },
        'cursor-blink': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
    },
  },
  plugins: [],
};
```

### Component Styling Patterns (Terminal Theme)
- **Main container**: `bg-terminal-bg text-terminal-green font-mono scanlines crt-screen`
- **Panels/Cards**: `border border-terminal-green bg-terminal-bg-light p-4`
- **Headers**: `text-terminal-green uppercase tracking-wide font-bold text-terminal-glow`
- **Buttons**: `px-4 py-2 border border-terminal-green bg-transparent text-terminal-green hover:bg-terminal-green hover:text-terminal-bg transition-all font-mono uppercase tracking-wider`
  - Primary action: `text-communicator border-communicator hover:bg-communicator hover:text-terminal-bg`
  - Danger: `text-error border-error hover:bg-error hover:text-terminal-bg terminal-flicker`
- **Inputs**: `bg-terminal-bg border border-terminal-green text-terminal-green px-3 py-2 font-mono focus:outline-none focus:border-communicator focus:shadow-[0_0_10px_rgba(0,217,255,0.5)]`
- **Role indicators**:
  - Communicator: `text-communicator [text-shadow:0_0_10px_rgba(0,217,255,0.5)]`
  - Receiver: `text-receiver [text-shadow:0_0_10px_rgba(255,170,0,0.5)]`
  - Bystander: `text-bystander`
  - System: `text-system [text-shadow:0_0_10px_rgba(255,0,255,0.5)]`
- **ASCII borders**: Use `╔═╗║╚╝` characters in content or as pseudo-elements

---

## 8. User Flows

### Flow 1: Start New Session
1. User lands on Session Setup view
2. User enters topic (or uses default)
3. User configures participants (or uses defaults)
4. User clicks "Start Session"
5. App sends POST to `/api/start-session`
6. On success, store `session_id` and transition to Conversation View
7. On error, display error message

### Flow 2: Play Through Session
1. User in Conversation View sees empty conversation
2. User clicks "Next Turn"
3. App sends POST to `/api/next-turn`
4. Loading spinner appears
5. Backend returns new messages
6. App displays messages in conversation feed
7. If guess present, show guess result
8. Update turn number and tries remaining
9. If `game_over: true`, show game over banner and disable "Next Turn"
10. User can click "Next Turn" again for subsequent rounds

### Flow 3: Reveal Internal Thoughts
1. User toggles "Reveal Thoughts" checkbox
2. App updates state `showThoughts: boolean`
3. All `MessageCard` components re-render to show/hide `internal_thoughts`

### Flow 4: View Full History
1. User clicks "View Full History" button
2. App sends GET to `/api/session/{id}/history`
3. Modal/overlay opens showing complete session data
4. Secret word revealed at top
5. User can scroll through all turns
6. User closes modal to return to active session

---

## 9. Error Handling

### API Error Scenarios
1. **Network failure**: Show "Unable to connect to server" message
2. **Invalid session**: Show "Session not found" and offer "Start New Session" button
3. **API key missing**: Backend returns 500 with detail - display error to user
4. **All model calls failed**: Display "All AI models failed. Check API keys."
5. **Game already over**: Display message and disable "Next Turn"

### Error UI
- Display errors in a dismissible banner at top of view
- Use red background (`bg-red-50 border-red-500 text-red-800`)
- Include retry action when applicable

---

## 10. Performance Considerations

### Optimization Strategies
1. **Lazy loading**: Consider code-splitting for history modal
2. **Memoization**: Use `React.memo` for `MessageCard` to prevent unnecessary re-renders
3. **Debouncing**: If adding real-time features, debounce API calls
4. **Virtualization**: Not needed for MVP (conversations are short)
5. **Request caching**: Cache participant metadata to avoid re-fetching

### Loading States
- Show skeleton loaders or spinners during API calls
- Disable buttons during async operations to prevent double-clicks

---

## 11. Accessibility

### WCAG 2.1 AA Compliance
1. **Semantic HTML**: Use `<button>`, `<form>`, `<article>` tags appropriately
2. **Keyboard navigation**: Ensure all interactive elements are keyboard-accessible
3. **Color contrast**: Verify all text meets 4.5:1 contrast ratio
4. **ARIA labels**: Add `aria-label` to icon buttons and complex widgets
5. **Focus indicators**: Ensure visible focus states for all interactive elements

### Screen Reader Support
- Use `role="status"` for game status updates
- Announce new messages with `aria-live="polite"`
- Label form inputs properly with `<label>` elements

---

## 12. Testing Requirements

### Unit Tests (Optional for MVP)
- Test `useSession` hook logic
- Test form validation in `SessionSetup`
- Test message rendering in `MessageCard`

### Integration Tests (Optional)
- Test complete flow from session setup to game over
- Mock API responses for predictable behavior

### Manual Testing Checklist
- [ ] Start session with default configuration
- [ ] Start session with custom participants
- [ ] Execute multiple turns successfully
- [ ] Reveal/hide internal thoughts toggle works
- [ ] Guess result displays correctly
- [ ] Game over states (win/loss) display correctly
- [ ] View full history modal works
- [ ] Error handling displays appropriately
- [ ] Responsive layout on different screen sizes

---

## 13. Deployment & Docker

### Development Mode
```bash
# From project root
docker compose up --build

# Web available at http://localhost:5173
# API available at http://localhost:8000
```

### Production Build
```bash
cd frontend
npm run build  # Outputs to frontend/dist
```

Production Docker service uses Nginx to serve static files.

---

## 14. Future Enhancements (Out of Scope for MVP)

### Functional Enhancements
1. **Session Persistence**: Store session_id in localStorage to resume sessions
2. **Multiple Sessions**: List and manage multiple game sessions
3. **Real-time Updates**: WebSocket integration for live turns
4. **Analytics Dashboard**: Visualize embedding/detection strategies
5. **Export Data**: Download session history as JSON/CSV
6. **Custom Agent Prompts**: Allow users to customize agent system prompts
7. **Mobile Optimization**: Improve layout for small screens

### Visual/Aesthetic Enhancements
1. **Sound effects**: Terminal beeps, keystroke sounds, error buzzes
2. **Boot sequence**: Animated startup screen (BIOS-style)
3. **Matrix rain background**: Falling characters behind main content (subtle)
4. **Terminal input simulation**: Make buttons look like typed commands
5. **Glitch transitions**: Page transitions with digital artifacts
6. **ASCII art decorations**: Agent avatars, dividers, status indicators
7. **Light mode toggle**: Switch between green terminal and amber terminal themes
8. **VHS/tape aesthetic**: Add VHS tracking lines, color bleeding effects
9. **Easter eggs**: Hidden terminal commands (e.g., `help`, `status`, `about`)
10. **Particle effects**: Subtle data stream particles on interactions

---

## 15. Acceptance Criteria

### Definition of Done
- [ ] User can start a new session with custom or default configuration
- [ ] User can execute turns and see conversation messages appear
- [ ] Internal thoughts are hidden by default and can be revealed via toggle
- [ ] Guess results display correctly with tries remaining
- [ ] Game over states (win/loss) are clearly indicated
- [ ] Secret word is revealed only after game over
- [ ] View full history feature works
- [ ] Error messages display for API failures
- [ ] Responsive layout works on desktop (1920x1080) and tablet (768x1024)
- [ ] Frontend runs in Docker alongside backend services
- [ ] All TypeScript types are properly defined with no `any` types
- [ ] Code is formatted with Prettier and linted with ESLint
- [ ] README includes setup instructions for frontend

---

## 16. Files to Create/Modify

### New Files (Frontend)
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/vite.config.ts`
- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- `frontend/Dockerfile`
- `frontend/.env.local.example`
- `frontend/.gitignore`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/index.css`
- `frontend/src/types/api.types.ts`
- `frontend/src/services/api.ts`
- `frontend/src/hooks/useSession.ts`
- `frontend/src/components/SessionSetup.tsx`
- `frontend/src/components/ConversationView.tsx`
- `frontend/src/components/MessageCard.tsx`
- `frontend/src/components/ParticipantList.tsx`
- `frontend/src/components/GameStatus.tsx`
- `frontend/README.md`

### Files to Modify
- `docker-compose.yml` (add `web` service)
- Root `.gitignore` (add `frontend/node_modules`, `frontend/dist`, `frontend/.env.local`)

---

## 17. Development Workflow

### Step-by-Step Implementation Order
1. **Project scaffolding**: Initialize Vite + React + TypeScript
2. **Styling setup**: Configure Tailwind CSS
3. **TypeScript types**: Define all API types
4. **API client**: Implement `api.ts` service
5. **Session setup**: Build `SessionSetup.tsx` and form logic
6. **Conversation view**: Build `ConversationView.tsx` layout
7. **Message cards**: Implement `MessageCard.tsx` with thoughts toggle
8. **Participant list**: Build `ParticipantList.tsx`
9. **Game status**: Implement `GameStatus.tsx`
10. **State management**: Complete `useSession.ts` hook
11. **App integration**: Wire up `App.tsx` with routing/state
12. **Docker integration**: Create Dockerfile and update docker-compose.yml
13. **Testing**: Manual testing of all flows
14. **Documentation**: Write frontend README

---

## 18. Key Design Decisions

### Why These Choices?
- **React + TypeScript**: Type safety and ecosystem support
- **Vite**: Fast dev server and modern build tooling
- **Tailwind CSS**: Rapid prototyping with utility classes
- **Fetch API**: Native browser API, no extra dependencies
- **Component-based**: Modular, reusable UI elements
- **Single-page app**: No need for routing complexity in MVP
- **Toggle for thoughts**: Default hidden maintains naturalness of conversation

### Open Questions for Implementer
1. Should conversation auto-scroll to latest message?
2. Should there be confirmation before starting a new session mid-game?
3. Should session_id be stored in localStorage for page refresh persistence?
4. Should there be a max conversation history length in the UI?

---

## 19. Reference Materials

### Project Documentation
- **`TERMINAL_UI_REFERENCE.md`**: ASCII art, UI patterns, color coding examples ⭐
- **`README.md`**: Backend API details and setup instructions
- **`CLAUDE.md`**: Architecture overview and development guidelines
- **`agents.md`**: Agent roles, communication protocol, and database schema
- **`FRONTEND_HANDOFF.md`**: Quick start guide for developers

### Backend Code Reference
- **`backend/app/api/routes.py`**: Live API implementation
- **`backend/app/api/schemas.py`**: Request/response models
- **`backend/app/models.py`**: Database schema

### External Resources
- React docs: https://react.dev
- Vite docs: https://vitejs.dev
- Tailwind CSS: https://tailwindcss.com
- TypeScript: https://www.typescriptlang.org
- VT323 Font: https://fonts.google.com/specimen/VT323
- IBM Plex Mono: https://fonts.google.com/specimen/IBM+Plex+Mono

---

## 20. Contact & Support

For questions about the backend API or project architecture, refer to:
- `backend/README.md`
- `CLAUDE.md`
- `agents.md`

Backend is fully functional and tested. Focus on building a clean, usable frontend that surfaces the conversation dynamics effectively.

---

**End of Specification**
