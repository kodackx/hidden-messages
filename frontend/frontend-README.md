# Hidden Messages - Frontend

React + TypeScript + Vite frontend for the Hidden Messages AI steganography research platform.

## Features

- **Retro Terminal UI**: 1980s CRT terminal aesthetic with scanlines, phosphor glow, and glitch effects
- **Session Management**: Configure and start AI conversation sessions
- **Real-time Conversation**: Watch agents converse turn-by-turn
- **Internal Thoughts**: Toggle to reveal agent reasoning processes
- **Guess Tracking**: Monitor receiver guess attempts and success/failure
- **Session History**: View complete conversation logs with secret word reveal
- **Responsive Design**: Works on desktop and tablet devices

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Sonner** for toast notifications

## Development Setup

### Prerequisites
- Node.js 20+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Edit .env.local with your backend URL (default: http://localhost:8000)
# VITE_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Docker Development

```bash
# Build and run with Docker Compose (includes backend)
docker compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

## Project Structure

```
src/
├── components/
│   ├── SessionSetup.tsx       # Session configuration form
│   ├── ConversationView.tsx   # Main conversation interface
│   ├── MessageCard.tsx        # Individual message display
│   ├── ParticipantList.tsx    # Agent roster with status
│   ├── GameStatus.tsx         # Turn controls and status
│   └── HistoryModal.tsx       # Full session history viewer
├── services/
│   └── api.ts                 # Backend API client
├── types/
│   └── api.types.ts           # TypeScript interfaces
├── pages/
│   └── Index.tsx              # Main page component
├── App.tsx                    # Root component
├── main.tsx                   # Entry point
└── index.css                  # Global styles and design system
```

## Design System

The UI follows a retro terminal/glitch aesthetic:

### Colors (HSL)
- **Background**: `0 0% 4%` (deep black)
- **Terminal Green**: `127 100% 50%` (phosphor green)
- **Communicator**: `191 100% 50%` (electric cyan)
- **Receiver**: `38 100% 50%` (amber)
- **Bystander**: `0 0% 80%` (gray)
- **System**: `300 100% 50%` (magenta)

### Typography
- **Primary**: VT323, Courier New, IBM Plex Mono (monospace)
- All text in UPPERCASE for system messages
- Phosphor glow effects via `text-terminal-glow` class

### Visual Effects
- **Scanlines**: CRT scanline overlay
- **Text Glow**: Phosphor-style text shadows
- **Flicker**: Subtle animation for errors/alerts
- **Cursor Blink**: Blinking terminal cursor
- **CRT Curvature**: Subtle screen curve simulation

## API Integration

The frontend communicates with the Python/FastAPI backend:

### Endpoints
- `POST /api/start-session` - Initialize new game session
- `POST /api/next-turn` - Execute one conversation round
- `GET /api/session/{id}/history` - Fetch complete session data
- `GET /api/session/{id}/status` - Get current game state
- `GET /api/health` - Health check

### Environment Variables
- `VITE_API_BASE_URL` - Backend API base URL (default: http://localhost:8000)

## Usage Flow

1. **Session Setup**: Configure topic, secret word (optional), and participants
2. **Start Session**: Backend initializes agents and creates session
3. **Execute Turns**: Click "Next Turn" to advance conversation
4. **Reveal Thoughts**: Toggle to see agent internal reasoning
5. **Monitor Guesses**: Watch receiver attempts and tries remaining
6. **Game Over**: Win (correct guess) or Loss (3 failed attempts)
7. **View History**: Access full conversation log with revealed secret word

## Building for Production

```bash
# Create production build
npm run build

# Output in dist/ directory
# Serve with any static file server or use Docker production stage
```

## Docker Production

```bash
# Build production image
docker build --target production -t hidden-messages-frontend .

# Run production container
docker run -p 80:80 hidden-messages-frontend
```

## Development Notes

### Component Guidelines
- All components use TypeScript with strict typing
- No `any` types - all API responses are typed
- Error handling with try/catch and user-friendly messages
- Loading states for all async operations

### Styling Guidelines
- Use design system tokens from `index.css`
- Avoid inline styles or arbitrary Tailwind values
- Color-code agent roles consistently
- Maintain retro terminal aesthetic throughout

### Performance
- Messages auto-scroll to latest on new turn
- History modal loads on-demand
- No real-time WebSockets (polling via manual "Next Turn")
- Responsive layout optimized for desktop/tablet

## Testing

### Manual Testing Checklist
- [ ] Start session with default configuration
- [ ] Start session with custom participants
- [ ] Execute multiple turns successfully
- [ ] Toggle reveal thoughts on/off
- [ ] Verify guess results display correctly
- [ ] Game over states (win/loss) appear correctly
- [ ] View full history modal works
- [ ] Error messages display on API failures
- [ ] Responsive on 1920x1080 (desktop) and 768x1024 (tablet)

### Test Backend Connection
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Should return: {"status":"healthy"}
```

## Troubleshooting

### Backend Connection Errors
- Verify backend is running on correct port
- Check `VITE_API_BASE_URL` in `.env.local`
- Ensure CORS is enabled on backend

### Build Errors
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run type-check`
- Verify all imports are correct

### Docker Issues
- Rebuild without cache: `docker compose build --no-cache`
- Check logs: `docker compose logs web`
- Verify environment variables are passed correctly

## License

Research project - see main repository for licensing information.
