# Frontend Spec Updates Summary

## Changes Made

Updated the frontend specification to incorporate a **retro terminal / glitch aesthetic** based on user feedback.

## Documents Created/Updated

### 1. **FRONTEND_SPEC.md** (Updated)
Complete technical specification with retro terminal aesthetic:

#### Key Changes:
- **Design Aesthetic Section**: Added detailed description of 1980s terminal / glitch art visual language
- **Color Scheme**: Changed from clean light theme to dark terminal theme
  - Background: Deep black (`#0A0A0A`)
  - Primary text: Bright green terminal (`#00FF41`)
  - Agent colors: Cyan/Blue, Amber, Gray, Magenta (all with glow effects)
- **Typography**: Changed from Inter/sans-serif to monospace (Courier New, IBM Plex Mono, VT323)
- **Visual Effects**: Added comprehensive CSS for:
  - CRT scanlines
  - Text glow/phosphor effects
  - Flicker animations
  - Cursor blink
  - Glitch effects
  - Chromatic aberration
  - Typing animations
- **UI Mockups**: Redesigned all ASCII mockups with terminal-style box characters (`╔═╗║`)
- **Component Patterns**: Updated Tailwind utilities for terminal aesthetic
- **Tailwind Config**: Extended with terminal colors, animations, and custom utilities

### 2. **TERMINAL_UI_REFERENCE.md** (New)
Quick reference guide for implementing terminal aesthetic:
- ASCII art box-drawing characters
- Button styles (terminal-themed)
- Input field patterns
- Status indicators
- Message formatting templates
- Panel layouts
- Agent color coding examples
- Animation suggestions
- Font recommendations
- Implementation tips

### 3. **FRONTEND_HANDOFF.md** (Updated)
Quick start guide with updated design aesthetic section:
- Visual style description
- Color-coded agent specifications
- Visual effects checklist
- Research-focused approach

## Visual Theme Summary

### From: Clean Modern UI
- Light background
- Inter font
- Subtle blue/orange/gray colors
- Card-based design
- Standard buttons and inputs

### To: Retro Terminal / Glitch
- Black background with green terminal text
- Monospace VT323/Courier fonts
- Neon glow effects (cyan, amber, magenta)
- ASCII art borders (`╔═╗║`)
- CRT scanline overlay
- Terminal-style command prompts
- Glitch/flicker animations
- 1980s computer aesthetic

## Visual Inspirations
- 1980s UNIX/DOS terminals (green phosphor CRT)
- The Matrix, WarGames, Blade Runner UI
- Glitch art and digital artifacts
- AI research lab retro computing
- Steganography/covert communication theme

## Technical Implementation

### New CSS Classes
- `.text-terminal-glow` - Phosphor text glow
- `.scanlines` - CRT scanline overlay
- `.crt-screen` - Screen curvature and ambient glow
- `.terminal-flicker` - Flicker animation
- `.cursor-blink` - Blinking cursor
- `.glitch-hover` - Glitch effect on hover
- `.chromatic-aberration` - RGB split effect

### New Tailwind Colors
```javascript
terminal: {
  bg: '#0A0A0A',
  green: '#00FF41',
}
communicator: '#00D9FF' (cyan with glow)
receiver: '#FFAA00' (amber with glow)
bystander: '#CCCCCC' (gray)
system: '#FF00FF' (magenta with glow)
```

### Fonts
- Primary: VT323 (Google Font)
- Fallbacks: IBM Plex Mono, Source Code Pro, Courier New

## Component Updates

### Session Setup
- Changed to terminal command-style interface
- ASCII box borders
- Terminal input fields with underscores
- `> EXECUTE: START_SESSION` button style

### Conversation View
- Messages formatted as `[AGENT>ROLE]`
- Internal thoughts in nested ASCII boxes
- Guess results as `>>> [ERROR] INCORRECT`
- Turn headers with timestamps
- Blinking cursor for input states

### Game Over States
- `███ GAME_OVER ███` banner style
- `>>> SECRET_WORD_DECODED:` format
- Terminal-style status messages

## Files for AI Developer

The AI agent should read in this order:
1. **FRONTEND_HANDOFF.md** - Quick overview
2. **FRONTEND_SPEC.md** - Complete specification
3. **TERMINAL_UI_REFERENCE.md** - UI patterns and examples
4. Backend docs (README.md, CLAUDE.md, agents.md) - API reference

## Acceptance Criteria (Aesthetic)
- [ ] Black background with green terminal text
- [ ] Monospace font (VT323 or similar)
- [ ] CRT scanline effect applied subtly
- [ ] Text glow on headers and agent names
- [ ] ASCII art box borders (`╔═╗║╚╝`)
- [ ] Color-coded agents with glow effects
- [ ] Terminal-style buttons and inputs
- [ ] Blinking cursor animation
- [ ] Messages formatted as `[AGENT>ROLE]`
- [ ] System messages in magenta
- [ ] Flicker effect on errors (optional)
- [ ] Overall retro terminal aesthetic

## Open Questions for Developer

1. **Scanline intensity**: How strong should the CRT effect be?
2. **Glow strength**: Should glow be subtle or pronounced?
3. **Animations**: How much flicker/glitch is too much?
4. **Typing effect**: Should messages appear character-by-character or instantly?
5. **Sound effects**: Out of scope or worth considering?
6. **ASCII art**: Use actual characters or CSS borders?

## Notes

- **Usability first**: Despite retro aesthetic, maintain readability and usability
- **Subtle effects**: Scanlines, glow, and flicker should enhance, not distract
- **Performance**: Keep animations lightweight
- **Accessibility**: Ensure sufficient contrast despite dark theme
- **Responsive**: Terminal aesthetic should work on tablet/desktop

---

**Next Step**: Hand off FRONTEND_SPEC.md, TERMINAL_UI_REFERENCE.md, and FRONTEND_HANDOFF.md to AI frontend developer for implementation.
