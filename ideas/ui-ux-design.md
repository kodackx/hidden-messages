# UI/UX Design Guidelines

This document outlines the visual design target for the Hidden Channels frontend application.

## Design Theme: "Digital Espionage"

A cyberpunk-inspired interface that reflects the covert nature of hidden AI communication channels.

### Color Palette

**Primary Colors:**
- **Matrix Black**: `#000000` - Deep background
- **Terminal Black**: `#0a0a0a` - Secondary background
- **Neon Green**: `#00ff41` - Primary accent (Matrix-style green)
- **Electric Green**: `#39ff14` - Highlights and active states
- **Dark Green**: `#001a0d` - Subtle backgrounds

**Supporting Colors:**
- **Ghost Gray**: `#1a1a1a` - Card backgrounds
- **Cyber Gray**: `#333333` - Borders and dividers
- **Warning Red**: `#ff0040` - Error states and alerts
- **Data Blue**: `#00ffff` - Secondary accents (sparingly)

### Typography

**Primary Font**: Monospace family (JetBrains Mono, Fira Code, or similar)
- Reinforces the terminal/coding aesthetic
- Excellent readability for conversation text
- Supports the digital spy theme

**Font Weights:**
- Regular (400) for body text
- Medium (500) for labels
- Bold (700) for headings and emphasis

### Visual Effects

**Glitch Effects:**
- Subtle scan line overlays on key components
- Random pixel displacement on hover states
- Brief RGB separation effects during loading
- Flicker animations for status indicators

**Pixel Elements:**
- 8-bit style icons and decorative elements
- Pixelated borders on cards and buttons
- Retro-style progress bars with chunky segments
- ASCII-art style decorative elements

### Component Design

**Chat Interface:**
- Dark terminal-style chat bubbles
- Green monospace text for agent communications
- Glitch effect on message appearance
- Subtle scan lines across the chat area

**Agent Cards:**
- Black cards with green pixel borders
- Role indicators with glitch text effects
- Status LEDs with pulsing animations
- Terminal-style agent names (Agent_A, Agent_B, Agent_C)

**Buttons & Controls:**
- Black backgrounds with green pixel borders
- Hover states with glitch distortion
- Active states with electric green glow
- Terminal-style button labels

**Input Fields:**
- Dark backgrounds with green terminal cursor
- Pixelated focus borders
- Placeholder text with glitch fade-in
- Monospace input text

### Layout Principles

**Grid System:**
- Sharp, geometric layouts
- No rounded corners (maintains pixel aesthetic)
- Strong vertical and horizontal lines
- Terminal-window inspired panels

**Spacing:**
- Consistent 8px pixel grid
- Generous whitespace in black
- Clean separation between components
- Terminal-style padding and margins

### Interactive Elements

**Animations:**
- Quick, snappy transitions (200-300ms)
- Glitch effects on state changes
- Typing indicator with cursor blink
- Matrix-style text reveal animations

**Feedback:**
- Green glow for success states
- Red pixel corruption for errors
- Subtle vibration effects (where supported)
- Terminal beep sounds (optional)

### Accessibility Considerations

**Contrast:**
- High contrast between green text and black backgrounds
- Alternative text for all glitch effects
- Focus indicators with strong visual distinction

**Motion:**
- Respect `prefers-reduced-motion` for glitch effects
- Provide options to disable animations
- Ensure core functionality works without effects

### Component Hierarchy

**Primary Interface Elements:**
1. Main chat window (dominant focus)
2. Agent status panel (secondary)
3. Control buttons (tertiary)
4. Settings/options (minimal)

**Information Architecture:**
- Conversation flow is the primary user journey
- Hidden thoughts reveal as secondary interaction
- Guess tracking as ambient information
- Settings and controls tucked away but accessible

### Inspiration References

**Visual Style:**
- Terminal interfaces from cyberpunk media
- Retro computer aesthetics (80s/90s computing)
- Matrix digital rain effect (subtle implementation)
- Hacker/surveillance thriller movie interfaces

**Modern Touch:**
- Clean information architecture
- Responsive design patterns
- Smooth micro-interactions
- Contemporary web standards

### Implementation Notes

**CSS Framework:**
- Tailwind CSS with custom pixel-art utilities
- Custom glitch effect classes
- Monospace font stack configuration
- Dark mode as default (with optional light theme)

**Animation Library:**
- Framer Motion for complex glitch effects
- CSS animations for simple transitions
- SVG animations for pixel decorations
- Canvas effects for advanced glitch overlays

This design creates an immersive experience that reinforces the experimental nature of hidden AI communication while maintaining modern usability standards.