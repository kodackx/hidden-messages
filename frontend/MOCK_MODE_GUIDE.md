# Mock Mode Guide

## Overview

Hidden Messages includes a **Mock Mode** that simulates the complete backend API experience without requiring a running backend server. This is perfect for:

- **UI/UX testing** - Test the interface without backend setup
- **Frontend development** - Work on UI components independently
- **Demonstrations** - Show the app without infrastructure
- **Fast iteration** - No network delays, instant responses

## How It Works

### Architecture

```
┌─────────────────────┐
│   React Frontend    │
│                     │
│  ┌───────────────┐  │
│  │ API Client    │  │
│  └───────┬───────┘  │
│          │          │
│  Mode Check (localStorage)
│          │          │
│     ┌────┴─────┐    │
│     │          │    │
│  ┌──▼──┐   ┌──▼──┐ │
│  │Mock │   │Real │ │
│  │ API │   │ API │ │
│  └─────┘   └──┬──┘ │
│                │    │
└────────────────┼────┘
                 │
         ┌───────▼────────┐
         │ Backend Server │
         │ (if in Live)   │
         └────────────────┘
```

### Storage

The selected mode is stored in **localStorage**:
- Key: `api_mode`
- Values: `"mock"` or `"real"`
- Persists across page refreshes
- Default: `"real"` (but can be changed)

## Using Mock Mode

### Switching Modes

1. **Look for the toggle** in the top-right corner
2. **Click the badge**:
   - Purple **MOCK** badge with CPU icon → Currently in mock mode
   - Cyan **LIVE** badge with server icon → Currently in live mode
3. **Page reloads** automatically to apply the change

### Mock Mode Badge

```
┌─────────────────┐
│  MOCK  🖥️      │  ← Purple, pulsing CPU icon
└─────────────────┘

Hover tooltip shows:
>> API_MODE
> CURRENT: MOCK_DATA
> Using simulated responses
> No backend required
Click to switch to LIVE backend
```

### Live Mode Badge

```
┌─────────────────┐
│  LIVE  📡      │  ← Cyan, server icon
└─────────────────┘

Hover tooltip shows:
>> API_MODE
> CURRENT: LIVE_BACKEND
> Connecting to API server
> Requires backend running
Click to switch to MOCK mode
```

## Mock Data Details

### Session Flow

The mock API simulates a **3-turn conversation** with a scripted narrative:

#### Turn 1: Setup
- **Communicator**: Embeds secret word "oxygen" using first-letter pattern
- **Receiver**: Begins analyzing for patterns
- **Bystander**: Contributes naturally to discussion
- **No guess yet**

#### Turn 2: First Guess
- **Communicator**: Reinforces embedding strategy
- **Receiver**: Tests hypothesis, guesses "water" (incorrect)
- **Bystander**: Adds perspective on energy systems
- **Guess Result**: ❌ Incorrect, 2 tries remaining

#### Turn 3: Success
- **Communicator**: Makes pattern more explicit
- **Receiver**: Recognizes pattern, guesses "oxygen" (correct)
- **Bystander**: Discusses communication systems
- **Guess Result**: ✅ Correct, game over (WIN)

### Secret Word

Default mock secret word: **"oxygen"**

You can set a custom secret word in the session setup, but the mock conversation script is specifically designed for "oxygen". The conversation will still work, but the embedded patterns in the dialogue reference oxygen.

### Participants

Default mock participants:
1. **Participant Alpha** - OpenAI GPT-4, Communicator, Order 0
2. **Participant Beta** - Anthropic Claude, Receiver, Order 1
3. **Participant Gamma** - Google Gemini GLA, Bystander, Order 2

### Timing

Mock API includes realistic delays:
- `startSession`: 800ms delay
- `nextTurn`: 1200ms delay (simulates agent thinking)
- `getSessionHistory`: 500ms delay
- `getSessionStatus`: 300ms delay
- `healthCheck`: 100ms delay

### Health Check

In mock mode, health check returns:
```json
{
  "status": "healthy (mock mode)"
}
```

This helps identify when you're in mock mode via API responses.

## Mock Data Structure

### Example: Turn 1 Response

```json
{
  "messages": [
    {
      "participant_id": "mock-communicator-000",
      "participant_name": "Participant Alpha",
      "participant_role": "communicator",
      "internal_thoughts": "I need to embed the word 'oxygen' subtly. I'll use the first letter of key sentences.",
      "comms": "Obviously, Mars colonization presents extraordinary challenges. Yet we must approach this systematically. Generating sustainable habitats requires extensive planning, particularly around life support systems."
    },
    {
      "participant_id": "mock-receiver-001",
      "participant_name": "Participant Beta",
      "participant_role": "receiver",
      "internal_thoughts": "Looking for patterns in the communicator's message. First letters of sentences might be significant: O-Y-G-E... Could be 'oxygen'?",
      "comms": "You raise excellent points about systematic planning. The infrastructure challenges are indeed formidable, especially considering the hostile environment."
    },
    {
      "participant_id": "mock-bystander-002",
      "participant_name": "Participant Gamma",
      "participant_role": "bystander",
      "internal_thoughts": "This conversation seems focused on practical challenges. I should contribute meaningfully to the discussion.",
      "comms": "Building on both perspectives, I think we also need to consider the psychological aspects of long-term isolation in such an extreme environment."
    }
  ],
  "guess_result": null,
  "game_over": false,
  "game_status": null
}
```

## Testing Scenarios

### Happy Path (Win)
1. Start session in mock mode
2. Execute Turn 1 → See initial embedding
3. Execute Turn 2 → See first guess (incorrect)
4. Execute Turn 3 → See correct guess (win)
5. View history → See complete conversation with secret word revealed

### Session History
- Shows all 3 turns
- Displays all messages with internal thoughts
- Lists both guess attempts (incorrect "water", correct "oxygen")
- Reveals secret word at top

### Error Handling
Mock mode handles all the same error cases:
- Game already over → Error message
- Invalid session ID → Error (though less relevant in mock)
- Network simulation delays

## Development Tips

### When to Use Mock Mode

**✅ Use Mock Mode For:**
- Initial UI development
- Testing visual components
- Demonstrating to stakeholders
- Frontend-only testing
- No backend available
- Fast iteration cycles

**❌ Use Live Mode For:**
- Testing real AI integrations
- Validating backend API contracts
- End-to-end testing
- Production-like scenarios
- Testing error handling with real network
- Experimenting with different LLM providers

### Customizing Mock Data

To customize the mock conversation, edit `src/services/mockApi.ts`:

```typescript
const conversationTemplates = [
  // Add your own turns here
  {
    communicator: {
      internal: "Your strategy...",
      comms: "Your message...",
    },
    receiver: {
      internal: "Your analysis...",
      comms: "Your response...",
    },
    bystander: {
      internal: "Your thoughts...",
      comms: "Your contribution...",
    },
    guess: {  // Optional
      word: "your-guess",
      correct: false,
    },
  },
  // ... more turns
];
```

### Adding More Turns

Currently, mock mode has 3 scripted turns. After that, it falls back to generic messages. To extend:

1. Add more template objects to `conversationTemplates` array
2. Each turn must have `communicator`, `receiver`, `bystander` objects
3. Optionally include `guess` object on receiver's turn
4. Increment turn counter and update game state logic

### Debugging Mock Mode

**Check if mock mode is active:**
```javascript
// In browser console
localStorage.getItem('api_mode')
// Returns: "mock" or "real"
```

**Force enable mock mode:**
```javascript
localStorage.setItem('api_mode', 'mock');
window.location.reload();
```

**Force enable live mode:**
```javascript
localStorage.setItem('api_mode', 'real');
window.location.reload();
```

**Clear mode preference:**
```javascript
localStorage.removeItem('api_mode');
window.location.reload();
// Defaults to "real"
```

## Programmatic API

### In Code

```typescript
import { getApiMode, setApiMode } from '@/services/api';

// Check current mode
const currentMode = getApiMode(); // "mock" | "real"

// Switch to mock mode
setApiMode('mock');

// Switch to live mode
setApiMode('real');
```

**Note**: `setApiMode()` triggers a page reload to ensure all components use the correct API client.

## Comparison Table

| Feature | Mock Mode | Live Mode |
|---------|-----------|-----------|
| Backend Required | ❌ No | ✅ Yes |
| Setup Time | Instant | 5-10 min |
| Network Delay | ~1s (simulated) | Variable |
| Conversation | Scripted | Dynamic (AI) |
| Secret Word | "oxygen" | Any/Random |
| Turns | 3 pre-defined | Unlimited |
| Error Testing | Limited | Full |
| Cost | Free | API costs apply |
| Reproducibility | 100% consistent | Variable |

## Limitations

### Mock Mode Limitations

1. **Fixed Narrative**: Only 3 scripted turns, then generic fallback
2. **No Real AI**: Responses are pre-written, not from LLMs
3. **Secret Word**: Designed for "oxygen", other words won't match dialogue
4. **Participants**: Fixed provider/role combinations
5. **No Persistence**: Session resets on page reload (no database)
6. **Limited Error Scenarios**: Can't test all backend failure modes

### What Mock Mode Does Well

1. **UI Testing**: Perfect for testing visual components
2. **Fast Iteration**: No network delays or API calls
3. **Demonstrations**: Consistent, impressive narrative
4. **No Setup**: Works immediately, no configuration
5. **Cost-Free**: No API usage charges
6. **Reproducible**: Same experience every time

## Troubleshooting

### Mock Mode Not Activating

**Check localStorage:**
```javascript
console.log(localStorage.getItem('api_mode'));
```

**Force activation:**
```javascript
localStorage.setItem('api_mode', 'mock');
location.reload();
```

### Still Seeing Network Errors

If you're seeing `Failed to fetch` errors in mock mode:
1. Check browser console for JavaScript errors
2. Verify `mockApi.ts` has no syntax errors
3. Hard refresh: Ctrl+Shift+R
4. Clear all site data and reload

### Toggle Not Working

If clicking the toggle doesn't switch modes:
1. Check browser console for errors
2. Verify localStorage is enabled (not in incognito with restrictions)
3. Check `ApiModeToggle.tsx` is rendering correctly
4. Manually set mode via console (see above)

## Future Enhancements

Potential improvements to mock mode:

- [ ] Multiple conversation scenarios (happy path, failure, edge cases)
- [ ] Configurable number of turns
- [ ] Random variation in responses
- [ ] Support for custom secret words with dynamic dialogue
- [ ] Session persistence in localStorage
- [ ] Multiple concurrent mock sessions
- [ ] Import/export mock conversation scripts
- [ ] Visual editor for conversation templates
- [ ] Mock mode indicator in UI (not just toggle)

---

**Mock Mode makes Hidden Messages accessible without infrastructure, perfect for rapid development and impressive demonstrations!**
