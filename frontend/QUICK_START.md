# Quick Start Guide - Hidden Messages UI

Get the interface running in **under 1 minute** - no backend required!

## 🚀 Fastest Path (Mock Mode)

```bash
npm install
npm run dev
```

**That's it!** Open http://localhost:5173 and you'll see the app running in **MOCK mode**.

## What You'll See

### 1. Session Setup Screen
The retro terminal interface will greet you with:
- Pre-filled topic: "colonizing Mars"
- 3 default agents ready to go
- Green terminal aesthetic with scanlines

**Just click** `> [EXECUTE: START_SESSION]` to begin.

### 2. Conversation View
After starting, you'll see:
- **Top-right toggle**: Purple "MOCK" badge (that's mock mode!)
- Participant list with all 3 agents
- Empty conversation waiting for you
- `EXEC: NEXT_TURN` button ready

### 3. Watch the Story Unfold
Click `EXEC: NEXT_TURN` three times to see:

**Turn 1**: Communicator embeds secret word "oxygen" using first-letter pattern
- All 3 agents contribute naturally
- Toggle `REVEAL_THOUGHTS` to see agent reasoning

**Turn 2**: Receiver makes first guess attempt
- Guesses "water" (incorrect)
- Tries remaining: 2/3
- Conversation continues naturally

**Turn 3**: Receiver solves the puzzle!
- Guesses "oxygen" (correct)
- Game over: **SUCCESS** banner appears
- Click `FULL_HISTORY` to see complete conversation with secret word revealed

## The Mock Experience

### What Makes Mock Mode Great?

✅ **No Setup** - Works instantly, zero configuration  
✅ **No Backend** - Pure frontend, no servers needed  
✅ **Fast** - Simulated delays (~1 sec), instant responses  
✅ **Consistent** - Same story every time, perfect for demos  
✅ **Complete** - Shows full win scenario with all features  

### The Story

The mock mode tells a scripted story where:
1. **Communicator (Alpha)** tries to convey "oxygen" through clever sentence patterns
2. **Receiver (Beta)** analyzes the patterns, makes educated guesses
3. **Bystander (Gamma)** contributes naturally without knowing the secret
4. After 2 turns, Beta cracks the code and wins!

It's designed to showcase:
- Natural conversation flow
- Steganographic embedding strategies
- Pattern recognition and analysis
- Guess mechanics and game state
- Beautiful terminal UI with all effects

## Quick Feature Tour

### Toggle Internal Thoughts
**Try this**: Click `REVEAL_THOUGHTS` toggle at the top
- **ON**: See agent reasoning and strategy
- **OFF**: Clean conversation only

Watch how the communicator embeds patterns and the receiver analyzes them!

### View Full History
**After game ends**: Click `FULL_HISTORY`
- See complete conversation log
- Secret word revealed at top
- All guesses and results
- Toggle thoughts on/off
- Modal with scrollable content

### API Mode Toggle (Top-Right)
**Purple MOCK badge**: You're in mock mode
- Hover to see tooltip
- Click to switch to LIVE mode (requires backend)

**Cyan LIVE badge**: Connected to real backend
- Click to switch back to MOCK mode

## When to Switch to Live Mode

Stay in **MOCK mode** for:
- Learning the interface
- UI/UX exploration
- Quick demonstrations
- Frontend development
- No backend available

Switch to **LIVE mode** when:
- Backend is running (see main README)
- Want real AI conversations
- Testing actual LLM integrations
- Experimenting with different topics/strategies

## Switching to Live Mode

### Step 1: Start Backend
```bash
# In a separate terminal (see backend README)
docker compose up api
```

### Step 2: Toggle to Live
Click the **MOCK** badge → Page reloads in **LIVE** mode (cyan badge)

### Step 3: Start Session
Now you're connected to real AI agents! Conversations will:
- Use actual LLMs (OpenAI, Anthropic, Google)
- Take longer (~5-10 seconds per turn)
- Produce dynamic, unpredictable results
- Cost API credits

## Visual Guide

```
┌─────────────────────────────────────────────┐
│  MOCK MODE                                  │
│  ┌──────────┐                               │
│  │  MOCK 🖥️ │ ← Purple badge (top-right)   │
│  └──────────┘                               │
│                                             │
│  ╔═══════════════════════════════════════╗  │
│  ║  HIDDEN_MESSAGES v1.0.0               ║  │
│  ║  SESSION: colonizing Mars             ║  │
│  ╠═══════════════════════════════════════╣  │
│  ║                                       ║  │
│  ║  Turn 1: Agents introduce patterns   ║  │
│  ║  Turn 2: First guess (incorrect)     ║  │
│  ║  Turn 3: Correct guess - WIN! 🎉     ║  │
│  ║                                       ║  │
│  ╚═══════════════════════════════════════╝  │
│                                             │
│  Features working:                          │
│  ✅ Reveal thoughts                         │
│  ✅ Guess tracking                          │
│  ✅ Full history                            │
│  ✅ Game over states                        │
│  ✅ All visual effects                      │
└─────────────────────────────────────────────┘
```

## Keyboard Shortcuts & Tips

### UI Tips
- **Hover over badges** for detailed tooltips
- **Messages auto-scroll** to latest turn
- **Thoughts toggle** applies globally to all messages
- **History modal** opens as overlay (ESC to close)

### Browser Console
```javascript
// Check current mode
localStorage.getItem('api_mode')  // "mock" or "real"

// Force switch to mock
localStorage.setItem('api_mode', 'mock')
location.reload()

// Force switch to live
localStorage.setItem('api_mode', 'real')
location.reload()
```

## Troubleshooting

### Not seeing the app?
- Check browser console for errors
- Ensure port 5173 isn't already in use
- Try `npm run dev` again

### Toggle not appearing?
- Refresh page (Ctrl+R or Cmd+R)
- Clear browser cache
- Check browser window is wide enough

### Mock mode not working?
```javascript
// In browser console
localStorage.clear()
location.reload()
```

### Want to start fresh?
- Reload page to reset mock session
- Each page load = new mock session
- No persistence between refreshes

## Next Steps

### Explore the UI
1. Start multiple sessions
2. Try different topics in session setup
3. Add/remove participants
4. Watch internal thoughts
5. View full history after game ends

### Customize Mock Data
Edit `src/services/mockApi.ts` to:
- Change conversation content
- Add more turns
- Modify secret words
- Adjust agent strategies

### Connect to Backend
When ready for real AI:
1. Follow backend setup (main README)
2. Start backend server
3. Click MOCK badge to switch
4. Enjoy dynamic AI conversations!

## Summary

```
┌─────────────────────────────────────────┐
│  Quick Start Checklist                  │
├─────────────────────────────────────────┤
│  ✅ npm install                          │
│  ✅ npm run dev                          │
│  ✅ Open http://localhost:5173           │
│  ✅ Click "START_SESSION"                │
│  ✅ Click "NEXT_TURN" 3 times            │
│  ✅ Toggle "REVEAL_THOUGHTS"             │
│  ✅ View "FULL_HISTORY" at end           │
│  ✅ Notice MOCK badge top-right          │
│  ✅ Enjoy the retro terminal aesthetic!  │
└─────────────────────────────────────────┘
```

**That's it! You're now exploring Hidden Messages in mock mode. No backend, no config, just pure UI experimentation.** 🚀

When you're ready for the real experience, check out the main README for backend setup and switch to LIVE mode!
