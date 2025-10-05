# Hidden Messages - Frontend Implementation

> **Retro terminal interface for experimental AI steganography research**

A React + TypeScript + Vite frontend that brings the Hidden Messages AI steganography experiment to life with an authentic 1980s CRT terminal aesthetic.

## 🎨 Visual Design

### Aesthetic: Retro AI Terminal / Glitch Art
The UI captures the essence of 1980s computer terminals meets modern AI research:

- **CRT Monitor Effects**: Scanlines, phosphor glow, subtle screen curvature
- **Terminal Typography**: VT323 and IBM Plex Mono monospace fonts
- **Glitch Elements**: Chromatic aberration, flicker animations, digital artifacts
- **Color-Coded Agents**: Each agent role has distinct glowing terminal colors
- **ASCII Borders**: Authentic terminal-style UI separators

### Color Palette
```
Background:    #0A0A0A (deep black)
Primary:       #00FF41 (terminal green with glow)
Communicator:  #00D9FF (electric cyan)
Receiver:      #FFAA00 (amber/orange)
Bystander:     #CCCCCC (gray)
System:        #FF00FF (magenta)
Error:         #FF0000 (red with flicker)
Success:       #00FF00 (bright green)
```

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- npm or yarn
- Backend API running at http://localhost:8000 (see main README)

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:5173 to see the app.

**Mock Mode**: The app starts in **MOCK mode** by default, which uses simulated API responses. This lets you test the UI without needing the backend running. Click the toggle in the top-right corner to switch between MOCK and LIVE modes.

### Using Docker

```bash
# Build and run full stack (frontend + backend)
docker compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🧪 Mock Mode vs Live Mode

### Mock Mode (Default)
- **No backend required** - Perfect for UI testing and development
- Uses realistic simulated conversation data
- Demonstrates full game flow (3 turns with guess attempts)
- Shows both win scenario (correct guess) and provides consistent experience
- Stored in localStorage, persists across page refreshes

### Live Mode
- Connects to real backend API at `http://localhost:8000`
- Requires backend server running (see main README)
- Real AI agent responses from OpenAI, Anthropic, Google
- Dynamic conversation based on actual LLM outputs
- True steganographic experimentation

### Switching Modes
Click the **MOCK/LIVE toggle** in the top-right corner:
- **Purple "MOCK" badge** = Mock mode (pulsing CPU icon)
- **Cyan "LIVE" badge** = Live mode (server icon)
- Hover for tooltip with mode details
- Page reloads automatically when switching

## 📁 Project Structure

```
src/
├── components/
│   ├── SessionSetup.tsx       # Session configuration form
│   ├── ConversationView.tsx   # Main game interface
│   ├── MessageCard.tsx        # Individual message display
│   ├── ParticipantList.tsx    # Agent roster with status
│   ├── GameStatus.tsx         # Turn controls and game status
│   ├── HistoryModal.tsx       # Full session history viewer
│   └── ErrorBoundary.tsx      # Global error handler
├── services/
│   └── api.ts                 # Backend API client
├── types/
│   └── api.types.ts           # TypeScript type definitions
├── pages/
│   ├── Index.tsx              # Main application page
│   └── NotFound.tsx           # 404 error page
├── App.tsx                    # Root component
├── main.tsx                   # Entry point
└── index.css                  # Global styles + design system
```

## 🎮 Features

### 1. Session Setup
- Configure conversation topic (default: "colonizing Mars")
- Set secret word (leave blank for random)
- Add/remove participants (minimum 3)
- Configure each agent:
  - Name
  - AI Provider (OpenAI, Anthropic, Google Gemini)
  - Role (Communicator, Receiver, Bystander)
  - Turn order

### 2. Conversation View
- **Turn-by-turn execution**: Manual control over conversation flow
- **Message display**: Shows all agent responses grouped by turn
- **Reveal Thoughts Toggle**: Show/hide agent internal reasoning
- **Guess tracking**: Monitor receiver attempts and remaining tries
- **Auto-scroll**: Automatically scrolls to latest messages
- **Real-time status**: Current turn, game state, participant info

### 3. Internal Thoughts
- Toggle to reveal agent reasoning processes
- Displayed in nested panels with `<INTERNAL_THOUGHTS>` tags
- Helps understand steganographic strategies
- Hidden by default to maintain conversation naturalness

### 4. Guess Display
- Shows when receiver submits a guess
- Indicates correct/incorrect with visual feedback
- Displays remaining tries (3 total)
- Terminal-style formatting with color coding

### 5. Game Over States
**Win Condition**: Receiver correctly guesses secret word
```
███ GAME_OVER ███ RESULT: SUCCESS ███
>>> OBJECTIVE_COMPLETE
>>> RECEIVER_STATUS: SUCCESS
```

**Loss Condition**: 3 failed guess attempts
```
███ GAME_OVER ███ RESULT: FAILURE ███
>>> OBJECTIVE_FAILED
>>> TRIES_EXHAUSTED: 3/3
```

### 6. Session History
- View complete conversation log
- See all turns, messages, and guesses
- Secret word revealed at top
- Toggle internal thoughts
- Read-only archive view

## 🎨 Design System

### Typography
All text uses monospace terminal fonts:
- **VT323**: Authentic CRT terminal look
- **IBM Plex Mono**: Modern monospace with character
- **Courier New**: Fallback terminal font

### Visual Effects

#### Scanlines
```css
.scanlines::before {
  /* CRT horizontal scanline overlay */
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15),
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 2px
  );
}
```

#### Text Glow (Phosphor Effect)
```css
.text-terminal-glow {
  text-shadow: 
    0 0 10px currentColor,
    0 0 20px currentColor;
}
```

#### Agent Color Classes
- `.text-communicator-glow` - Electric cyan with glow
- `.text-receiver-glow` - Amber/orange with glow
- `.text-bystander-glow` - Gray with subtle glow
- `.text-system-glow` - Magenta with glow

### Components

#### Terminal Panel
```tsx
<div className="terminal-panel">
  {/* Content */}
</div>
```
Standard bordered panel with terminal styling.

#### Terminal Button
```tsx
<button className="terminal-button">
  ACTION
</button>
```
Monospace uppercase button with border and hover effects.

#### Terminal Button Accent (Cyan)
```tsx
<button className="terminal-button-accent">
  PRIMARY_ACTION
</button>
```
Cyan-colored button for primary actions.

#### Terminal Input
```tsx
<input className="terminal-input" />
```
Terminal-styled text input with focus glow.

## 🔌 API Integration

### Environment Variables
Create `.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### API Endpoints

#### Start Session
```typescript
POST /api/start-session
{
  "topic": "string",
  "secret_word": "string" | null,
  "participants": [
    {
      "name": "string",
      "provider": "openai" | "anthropic" | "google" | "google-gla",
      "role": "communicator" | "receiver" | "bystander",
      "order": number
    }
  ]
}

Response:
{
  "session_id": "uuid",
  "status": "string",
  "topic": "string",
  "participants": [...]
}
```

#### Next Turn
```typescript
POST /api/next-turn
{
  "session_id": "uuid"
}

Response:
{
  "messages": [
    {
      "participant_id": "uuid",
      "participant_name": "string",
      "participant_role": "communicator" | "receiver" | "bystander",
      "internal_thoughts": "string",
      "comms": "string"
    }
  ],
  "guess_result": {
    "agent": "uuid",
    "correct": boolean,
    "tries_remaining": number
  } | null,
  "game_over": boolean,
  "game_status": "win" | "loss" | null
}
```

#### Session History
```typescript
GET /api/session/{session_id}/history

Response:
{
  "session_id": "uuid",
  "topic": "string",
  "secret_word": "string",
  "created_at": "ISO timestamp",
  "participants": {...},
  "messages": [...],
  "guesses": [...]
}
```

## 🧪 Testing

### Manual Test Flow
1. Open http://localhost:5173
2. Review default session configuration
3. Click "EXECUTE: START_SESSION"
4. Wait for session initialization
5. Click "EXEC: NEXT_TURN" multiple times
6. Toggle "REVEAL_THOUGHTS" on/off
7. Observe guess attempts and results
8. Continue until game over (win or loss)
9. Click "FULL_HISTORY" to view complete log
10. Click "NEW_SESSION" to start fresh

### Test Scenarios

**Scenario 1: Default Configuration**
- Use pre-filled defaults
- Start session
- Execute 5-10 turns
- Verify all messages display correctly

**Scenario 2: Custom Configuration**
- Change topic to "space exploration"
- Add 4th participant (bystander)
- Set custom secret word "rocket"
- Verify configuration persists

**Scenario 3: Error Handling**
- Stop backend server
- Try to start session
- Verify error message displays
- Restart backend
- Try again successfully

**Scenario 4: Game Over States**
- Play until receiver guesses correctly → Win state
- OR play until 3 failed guesses → Loss state
- Verify correct banner displays

## 🐛 Troubleshooting

### "Failed to fetch" in Live Mode
**Symptom**: Network errors when starting session in LIVE mode  
**Solution**: 
- Switch to MOCK mode (toggle in top-right) to test UI without backend
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check `.env.local` has correct `VITE_API_BASE_URL`
- Ensure no CORS issues (backend should allow localhost:5173)

### Mock Mode Not Working
**Symptom**: Errors even in MOCK mode  
**Solution**:
- Clear localStorage: Open DevTools → Application → Local Storage → Clear
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Check browser console for JavaScript errors

### Toggle Not Appearing
**Symptom**: Can't see MOCK/LIVE toggle  
**Solution**:
- Check browser window is wide enough (toggle is top-right)
- Clear cache and hard reload
- Verify ApiModeToggle component is imported

### Build Errors
**Symptom**: TypeScript compilation errors  
**Solution**:
```bash
# Clear and reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run build
```

### Visual Effects Not Showing
**Symptom**: No scanlines or glow effects  
**Solution**:
- Clear browser cache
- Check browser console for CSS errors
- Verify VT323 font loaded (Network tab)
- Try hard reload (Ctrl+Shift+R)

### Docker Issues
**Symptom**: Container fails to start  
**Solution**:
```bash
# Rebuild without cache
docker compose down
docker compose build --no-cache
docker compose up

# Check logs
docker compose logs web
docker compose logs api
```

## 📦 Building for Production

```bash
# Create optimized production build
npm run build

# Output in dist/ directory
# Serve with any static file server:
npx serve dist

# Or use Docker production image
docker build --target production -t hidden-messages-frontend .
docker run -p 80:80 hidden-messages-frontend
```

## 🎯 Performance Considerations

- **No real-time updates**: Manual turn advancement reduces server load
- **Client-side state**: Session state managed in React (no localStorage yet)
- **Optimized re-renders**: `React.memo` on MessageCard components
- **Auto-scroll**: Smooth scroll to latest message on each turn
- **Lazy modals**: History modal loads data on-demand

## 🔮 Future Enhancements

### Planned Features
- [ ] Session persistence (localStorage)
- [ ] Multiple session management
- [ ] WebSocket real-time updates
- [ ] Export session data (JSON/CSV)
- [ ] Advanced analytics dashboard
- [ ] Sound effects (terminal beeps, keystrokes)
- [ ] Boot sequence animation
- [ ] Mobile optimization

### Visual Enhancements
- [ ] Matrix rain background effect
- [ ] VHS tape tracking lines
- [ ] ASCII art agent avatars
- [ ] Terminal command Easter eggs
- [ ] Light mode (amber on black)
- [ ] Customizable color themes

## 📄 License

Research project - see main repository for details.

## 🙏 Credits

**Design Inspiration:**
- 1980s CRT terminals (VT100, IBM PC)
- The Matrix (1999) - Terminal UI
- WarGames (1983) - WOPR interface
- Blade Runner - Retro-futuristic aesthetics
- Early LISP machines and AI research labs

**Technologies:**
- React 18 + TypeScript
- Vite (build tooling)
- Tailwind CSS (styling)
- Lucide React (icons)
- Sonner (toasts)

---

**Built for the Hidden Messages AI Steganography Research Project**
