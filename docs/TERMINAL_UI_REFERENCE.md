# Terminal UI Reference Guide

Quick reference for implementing the retro terminal aesthetic.

## ASCII Art Characters

### Box Drawing Characters
```
╔ ╗ ╚ ╝  ═  ║  (double line)
┌ ┐ └ ┘  ─  │  (single line)
├ ┤ ┬ ┴ ┼     (single line intersections)
╠ ╣ ╦ ╩ ╬     (double line intersections)
```

### Common UI Elements
```
► ▼ ◄ ▲  (arrows)
● ○ ■ □  (bullets/checkboxes)
█ ▓ ▒ ░  (blocks/shading)
... ─── ═══  (separators)
```

## Button Styles

### Primary Action Button
```
┌──────────────────┐
│ > EXECUTE_ACTION │
└──────────────────┘
```
CSS: `border: 1px solid #00FF41; color: #00D9FF; hover: bg-cyan`

### Secondary Button
```
[ CANCEL ]  [ RESET ]  [ BACK ]
```
CSS: Square brackets in content, simpler border

### Disabled State
```
[ ░░░░░ ]  or  [DISABLED]
```
CSS: Reduced opacity, gray color

## Input Fields

### Text Input (Active)
```
USERNAME: [konstantin_____________█]
```
█ = blinking cursor

### Text Input (Filled)
```
TOPIC: [colonizing_Mars___________]
```

### Dropdown/Select
```
PROVIDER: [OPENAI_GPT4 ▼]
```

### Checkbox/Toggle
```
[✓] REVEAL_THOUGHTS    [☐] REVEAL_THOUGHTS
or
[█] ENABLED           [░] DISABLED
```

## Status Indicators

### Agent Status
```
[●] ONLINE    [○] OFFLINE    [▓] BUSY
```

### Loading/Progress
```
[█████░░░░░] 50%
LOADING... ███
PROCESSING [▓▓▓▓▓▓░░░░] 60%
```

### Success/Error
```
>>> [SUCCESS] OPERATION_COMPLETE
>>> [ERROR] INVALID_INPUT
>>> [WARN] API_KEY_MISSING
```

## Message Formatting

### Agent Message Header
```
[ALPHA>COMMUNICATOR]                 TIMESTAMP:12:34:56
```

### System Message
```
>>> SYSTEM: GUESS_RESULT_INCORRECT
>>> TRIES_REMAINING: 2/3
```

### Internal Thoughts Container
```
╔═══════════════════════════════════════════╗
║ <INTERNAL_THOUGHTS>                       ║
║ Analyzing patterns in previous messages...║
║ Embedding strategy: first-letter acrostic ║
║ </INTERNAL_THOUGHTS>                      ║
╚═══════════════════════════════════════════╝
```

## Panel Layouts

### Header Panel
```
╔════════════════════════════════════════════════╗
║  HIDDEN_MESSAGES v1.0.0         STATUS: ACTIVE ║
╚════════════════════════════════════════════════╝
```

### Content Panel
```
┌────────────────────────────────────────────┐
│ >> SECTION_TITLE                           │
├────────────────────────────────────────────┤
│                                            │
│  Content goes here...                      │
│                                            │
└────────────────────────────────────────────┘
```

### Nested Panels
```
╔══════════════════════════════════════════════╗
║ ┌──────────────────────────────────────┐   ║
║ │ Inner panel                          │   ║
║ └──────────────────────────────────────┘   ║
╚══════════════════════════════════════════════╝
```

## List Items

### Agent List
```
[●] ALPHA    | COMMUNICATOR | OPENAI_GPT4
[●] BETA     | RECEIVER     | ANTHROPIC   | TRIES:3/3
[●] GAMMA    | BYSTANDER    | GEMINI_GLA
```

### Turn History
```
[TURN_001] ────────────────────────────────
[ALPHA>COMMUNICATOR] Mars colonization...
[BETA>RECEIVER] Interesting perspective...
>>> GUESS: "oxygen" [ERROR] INCORRECT
```

## Table Layout

### Participant Configuration
```
╔═══════════╤══════════════╤════════════╗
║ AGENT_ID  │ ROLE         │ PROVIDER   ║
╠═══════════╪══════════════╪════════════╣
║ ALPHA     │ COMMUNICATOR │ OPENAI     ║
║ BETA      │ RECEIVER     │ ANTHROPIC  ║
║ GAMMA     │ BYSTANDER    │ GEMINI     ║
╚═══════════╧══════════════╧════════════╝
```

## Game Over Banners

### Success
```
╔══════════════════════════════════════════════╗
║ ███ OBJECTIVE_COMPLETE ███                   ║
║                                              ║
║ >>> SECRET_WORD_DECODED: "oxygen"            ║
║ >>> TURNS_ELAPSED: 004                       ║
║                                              ║
╚══════════════════════════════════════════════╝
```

### Failure
```
╔══════════════════════════════════════════════╗
║ ▓▓▓ OBJECTIVE_FAILED ▓▓▓                     ║
║                                              ║
║ >>> SECRET_WORD_REVEALED: "oxygen"           ║
║ >>> TRIES_EXHAUSTED: 3/3                     ║
║                                              ║
╚══════════════════════════════════════════════╝
```

## Color Usage Examples

### Agent Color Coding
```html
<!-- Communicator (cyan/blue) -->
<span class="text-communicator [text-shadow:0_0_10px_rgba(0,217,255,0.5)]">
  [ALPHA>COMMUNICATOR]
</span>

<!-- Receiver (amber/orange) -->
<span class="text-receiver [text-shadow:0_0_10px_rgba(255,170,0,0.5)]">
  [BETA>RECEIVER]
</span>

<!-- Bystander (white/gray) -->
<span class="text-bystander">
  [GAMMA>BYSTANDER]
</span>

<!-- System (magenta/pink) -->
<span class="text-system [text-shadow:0_0_10px_rgba(255,0,255,0.5)]">
  >>> SYSTEM_MESSAGE
</span>
```

## Animation Suggestions

### Cursor Blink
```html
<span class="animate-cursor-blink">█</span>
```

### Text Appear (Typing Effect)
```html
<div class="typing-effect">Initializing agents...</div>
```

### Flicker (Error States)
```html
<div class="terminal-flicker text-error">
  >>> [ERROR] CONNECTION_FAILED
</div>
```

### Glitch (Hover Effect)
```html
<button class="glitch-hover">
  [EXECUTE]
</button>
```

## Terminal Prompt Styles

### Command Prompt
```
> _
> EXECUTE: START_SESSION
> LOADING...
```

### Multi-line Command
```
$ INIT_AGENTS --topic="Mars" \
              --participants=3 \
              --secret-word=null
```

### Status Output
```
[OK]    Session initialized
[OK]    Agents loaded
[WAIT]  Connecting to API...
[OK]    Connection established
```

## Separator Styles

### Light Separator
```
─────────────────────────────────────
```

### Heavy Separator
```
═════════════════════════════════════
```

### Dotted Separator
```
. . . . . . . . . . . . . . . . . . .
```

### ASCII Separator
```
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

## Implementation Tips

1. **Consistency**: Pick one box-drawing style (single or double) and stick with it for similar elements
2. **Contrast**: Use double-line borders (`╔═╗`) for primary containers, single-line (`┌─┐`) for secondary
3. **Spacing**: Terminal UIs benefit from generous whitespace/padding
4. **Alignment**: Monospace fonts make alignment easy - use it!
5. **Readability**: Despite the retro aesthetic, prioritize readability
6. **Glow effects**: Apply sparingly to avoid overwhelming the user
7. **Animation**: Keep subtle - too much flicker/glitch is distracting

## Font Recommendations

### Primary Choices (in order of preference)
1. **VT323** (Google Font) - Most authentic terminal look
2. **IBM Plex Mono** - Clean, modern monospace
3. **Source Code Pro** - Popular code font
4. **Courier New** - Universal fallback

### Font Loading (index.html)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=VT323&display=swap" rel="stylesheet">
```

### CSS Usage
```css
body {
  font-family: 'VT323', 'Courier New', monospace;
  font-size: 1.125rem; /* VT323 needs larger size */
}
```

---

**Remember**: The goal is "research terminal aesthetic" not "unusable gimmick". Prioritize usability while maintaining the retro vibe.
