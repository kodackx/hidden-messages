# Frontend Development Handoff

## Quick Start for AI Developer

This project needs a complete frontend built from scratch. The backend is **fully functional and tested** - you just need to build the UI.

### What You're Building
A React + TypeScript + Tailwind CSS interface for an experimental AI game where LLM agents attempt covert communication through natural conversation.

### Key Documents
1. **`FRONTEND_SPEC.md`** - Complete technical specification (READ THIS FIRST)
2. **`CLAUDE.md`** - Project architecture and development guidelines
3. **`agents.md`** - Agent roles and communication protocol
4. **`README.md`** - Backend API documentation
5. **`backend/app/api/routes.py`** - Live API implementation for reference

### Your Mission
Build a frontend that allows users to:
1. Configure and start AI conversation sessions
2. Watch agents converse in real-time (turn-by-turn)
3. Reveal/hide agent internal thoughts
4. See guess attempts and results
5. View game outcomes (win/loss)

### Tech Stack (Non-negotiable)
- React 18+ with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Docker integration with existing docker-compose.yml

### Critical Requirements
✅ **Must Have:**
- Session setup form with participant configuration
- Conversation view showing messages grouped by turn
- Toggle to reveal/hide internal thoughts
- Display guess results and tries remaining
- Clear win/loss states
- Full session history view
- Docker integration (Dockerfile + docker-compose service)

❌ **Do NOT Build:**
- Authentication/user accounts
- Session persistence/localStorage (unless time permits)
- Real-time WebSockets
- Mobile-specific optimizations
- Backend modifications

### Backend API (Already Working)
```
POST /api/start-session       → Start new game
POST /api/next-turn            → Execute one conversation round
GET  /api/session/{id}/history → Get complete session data
GET  /api/session/{id}/status  → Get current game state
GET  /api/health               → Health check
```

Base URL: `http://localhost:8000`

### File Structure You'll Create
```
frontend/
├── src/
│   ├── components/
│   │   ├── SessionSetup.tsx
│   │   ├── ConversationView.tsx
│   │   ├── MessageCard.tsx
│   │   ├── ParticipantList.tsx
│   │   └── GameStatus.tsx
│   ├── hooks/
│   │   └── useSession.ts
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── api.types.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── Dockerfile
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

### Development Workflow
1. Read `FRONTEND_SPEC.md` thoroughly
2. Initialize Vite + React + TypeScript project in `frontend/` folder
3. Set up Tailwind CSS
4. Implement TypeScript types from the spec
5. Build API client service
6. Create components (start with SessionSetup, then ConversationView)
7. Wire up state management with useSession hook
8. Create Dockerfile and update docker-compose.yml
9. Test all user flows manually
10. Document setup in frontend/README.md

### Testing Your Work
```bash
# Start full stack
docker compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

**Test Flow:**
1. Open http://localhost:5173
2. Use default configuration or customize participants
3. Click "Start Session"
4. Click "Next Turn" multiple times to see conversation develop
5. Toggle "Reveal Thoughts" on/off
6. Wait for receiver to guess (or guess incorrectly 3 times)
7. Verify game over state shows correctly

### Design Aesthetic: Retro Terminal / Glitch
- **Visual style**: 1980s computer terminals meets AI research lab meets glitch art
- **Dark terminal theme**: Black background (`#0A0A0A`), bright green terminal text (`#00FF41`)
- **Monospace fonts**: Courier New, IBM Plex Mono, VT323
- **Visual effects**: 
  - CRT scanline effects
  - Text glow/phosphor effects
  - Occasional flicker animations
  - ASCII art borders (`╔═╗║╚╝`)
  - Blinking cursors
- **Color-coded agents**: 
  - Communicator: Electric blue/cyan (`#00D9FF`) with glow
  - Receiver: Amber/orange (`#FFAA00`) with glow
  - Bystander: White/gray (`#CCCCCC`)
  - System: Magenta/pink (`#FF00FF`) with glow
- **Research-focused**: Emphasize observation, not gamification

### Common Pitfalls to Avoid
❌ Don't hardcode API URL - use environment variables  
❌ Don't use `any` types - define proper TypeScript interfaces  
❌ Don't forget Docker configuration  
❌ Don't build authentication - it's not needed  
❌ Don't modify backend code  
❌ Don't skip error handling - API calls can fail

### Acceptance Criteria
Before marking this complete, verify:
- [ ] Session setup form works with defaults and custom config
- [ ] Conversation displays messages correctly
- [ ] Internal thoughts toggle works
- [ ] Guess results show with tries remaining
- [ ] Win/loss states display clearly
- [ ] Full history view works
- [ ] Errors display when API fails
- [ ] Responsive on desktop (1920x1080) and tablet (768x1024)
- [ ] Runs in Docker with backend
- [ ] No TypeScript errors
- [ ] Code is clean and formatted

### Need Help?
- API endpoint details → `backend/app/api/routes.py` and `backend/app/api/schemas.py`
- Response formats → See `FRONTEND_SPEC.md` Section 2
- Component details → See `FRONTEND_SPEC.md` Section 4
- Styling guidelines → See `FRONTEND_SPEC.md` Section 7

### Estimated Effort
- **Setup & scaffolding**: 30 minutes
- **Core components**: 2-3 hours
- **State management & API integration**: 1-2 hours
- **Styling & polish**: 1-2 hours
- **Docker & testing**: 30 minutes

**Total**: 5-8 hours for experienced developer

---

**You have everything you need. The backend is solid. Now build a clean, functional UI that brings this experiment to life!**
