# Terminal UI Reference Guide

Quick reference for maintaining the retro terminal aesthetic throughout the Hidden Messages interface.

## ASCII Art Elements

### Box Drawing Characters
```
╔═══════════════════════════╗
║  Header                   ║
╠═══════════════════════════╣
║  Content                  ║
╚═══════════════════════════╝

┌───────────────────────────┐
│  Lighter box style        │
├───────────────────────────┤
│  Content                  │
└───────────────────────────┘

>>> System message
[STATUS] Message with tag
> Prompt indicator
█ Cursor block
_ Cursor underscore
```

### Usage in Components
```tsx
// Header with ASCII border
<div className="terminal-panel">
  <div className="text-terminal-glow uppercase">
    ╔════════════════════════════╗
  </div>
  <div className="text-terminal-glow uppercase">
    ║ SYSTEM_STATUS             ║
  </div>
  <div className="text-terminal-glow uppercase">
    ╚════════════════════════════╝
  </div>
</div>

// Inline separators
<span>FIELD_1</span>
<span className="text-muted-foreground"> | </span>
<span>FIELD_2</span>

// System messages
<p>&gt;&gt;&gt; SYSTEM_MESSAGE</p>
<p>&gt; PROMPT_TEXT<span className="cursor-blink">█</span></p>
```

## Color Coding Patterns

### Agent Roles
```tsx
// Communicator (Electric Cyan)
<span className="text-communicator-glow">
  [ALPHA>COMMUNICATOR]
</span>

// Receiver (Amber/Orange)  
<span className="text-receiver-glow">
  [BETA>RECEIVER]
</span>

// Bystander (Gray)
<span className="text-bystander-glow">
  [GAMMA>BYSTANDER]
</span>

// System (Magenta)
<span className="text-system-glow">
  &lt;SYSTEM_MESSAGE&gt;
</span>
```

### Status Indicators
```tsx
// Active/Success (Green)
<span className="text-success">●</span> ACTIVE
<span className="text-primary text-terminal-glow">ONLINE</span>

// Error/Critical (Red with flicker)
<span className="text-error terminal-flicker">ERROR</span>
<span className="text-destructive">⚠ WARNING</span>

// Neutral/Info
<span className="text-muted-foreground">INFO</span>
```

## Typography Patterns

### Headers
```tsx
// H1 - Main title
<h1 className="text-2xl font-bold uppercase tracking-widest text-terminal-glow">
  HIDDEN_MESSAGES v1.0.0
</h1>

// H2 - Section headers
<h2 className="text-lg uppercase tracking-wide text-terminal-glow">
  &gt;&gt; SECTION_NAME
</h2>

// H3 - Subsections
<h3 className="text-sm uppercase tracking-wide text-muted-foreground">
  &gt; SUBSECTION
</h3>
```

### Body Text
```tsx
// Standard terminal text
<p className="text-sm font-mono">
  System operational...
</p>

// Emphasized text
<p className="text-sm font-mono text-terminal-glow">
  IMPORTANT_MESSAGE
</p>

// Dimmed/secondary text
<p className="text-xs text-muted-foreground">
  Additional information
</p>
```

### Labels
```tsx
// Input labels
<label className="block text-xs uppercase tracking-wide mb-1">
  FIELD_NAME:
</label>

// Inline labels
<span className="text-muted-foreground">LABEL:</span>{' '}
<span className="text-primary">VALUE</span>
```

## Button Patterns

### Standard Terminal Button
```tsx
<button className="terminal-button">
  ACTION_NAME
</button>
```

### Accent Button (Cyan - Primary Actions)
```tsx
<button className="terminal-button-accent">
  <Icon size={16} />
  PRIMARY_ACTION
</button>
```

### Danger Button (Red - Destructive Actions)
```tsx
<button className="terminal-button-danger">
  DANGEROUS_ACTION
</button>
```

### With Loading State
```tsx
<button className="terminal-button" disabled={loading}>
  {loading ? (
    <>PROCESSING<span className="cursor-blink">_</span></>
  ) : (
    'EXECUTE'
  )}
</button>
```

## Form Elements

### Text Input
```tsx
<input
  type="text"
  className="terminal-input w-full"
  placeholder="Enter data..."
/>
```

### Select Dropdown
```tsx
<select className="terminal-select w-full">
  <option value="option1">OPTION_1</option>
  <option value="option2">OPTION_2</option>
</select>
```

### Checkbox/Toggle
```tsx
<button
  onClick={toggleState}
  className={`terminal-button ${state ? 'bg-primary text-background' : ''}`}
>
  OPTION:{state ? '▓' : '░'}
</button>
```

## Panel Layouts

### Basic Panel
```tsx
<div className="terminal-panel">
  <div className="text-sm uppercase tracking-wide mb-3 text-terminal-glow">
    &gt;&gt; PANEL_TITLE
  </div>
  <div>
    Content goes here
  </div>
</div>
```

### Panel with Border Variants
```tsx
// Success border
<div className="terminal-panel border-success">
  Success content
</div>

// Error border
<div className="terminal-panel border-error">
  Error content
</div>

// System border  
<div className="terminal-panel border-system">
  System content
</div>
```

### Nested Panels
```tsx
<div className="terminal-panel">
  <h2 className="text-terminal-glow uppercase mb-4">OUTER_PANEL</h2>
  
  <div className="border border-muted p-3 rounded-sm bg-card/50">
    <p className="text-sm">Nested content</p>
  </div>
</div>
```

## Message Display Patterns

### Agent Message Card
```tsx
<div className="border border-muted p-4 rounded-sm mb-3 bg-card/50">
  {/* Header */}
  <div className="flex justify-between items-start mb-3">
    <span className="text-communicator-glow font-bold uppercase text-sm">
      [ALPHA>COMMUNICATOR]
    </span>
    <span className="text-xs text-muted-foreground">
      TURN_001
    </span>
  </div>
  
  {/* Message content */}
  <p className="text-sm leading-relaxed">
    Agent message text...
  </p>
  
  {/* Internal thoughts (optional) */}
  <div className="border-l-2 border-system pl-3 py-2 bg-secondary/30 rounded-sm mt-3">
    <div className="text-xs text-system-glow uppercase mb-1 font-bold">
      &lt;INTERNAL_THOUGHTS&gt;
    </div>
    <p className="text-xs text-muted-foreground">
      Agent reasoning...
    </p>
    <div className="text-xs text-system-glow uppercase mt-1 font-bold">
      &lt;/INTERNAL_THOUGHTS&gt;
    </div>
  </div>
</div>
```

### System Message
```tsx
<div className="border border-system p-3 rounded-sm bg-system/10">
  <div className="text-system-glow text-sm font-bold uppercase mb-1">
    &gt;&gt;&gt; SYSTEM_EVENT
  </div>
  <div className="text-xs space-y-1">
    <div>
      <span className="text-muted-foreground">PARAMETER:</span>{' '}
      <span className="text-primary">VALUE</span>
    </div>
  </div>
</div>
```

### Guess Result Display
```tsx
<div className="border border-system p-3 rounded-sm bg-system/10">
  <div className="text-system-glow text-sm font-bold uppercase mb-1">
    &gt;&gt;&gt; GUESS_SUBMITTED
  </div>
  <div className="text-xs space-y-1">
    <div>
      <span className="text-muted-foreground">AGENT:</span>{' '}
      <span className="text-receiver-glow">BETA</span>
    </div>
    <div className={correct ? 'text-success' : 'text-error'}>
      &gt;&gt;&gt; [{correct ? 'SUCCESS' : 'ERROR'}]{' '}
      {correct ? 'CORRECT' : 'INCORRECT'}
    </div>
    {!correct && (
      <div>
        <span className="text-muted-foreground">TRIES_REMAINING:</span>{' '}
        <span className="text-primary">{tries}</span>
      </div>
    )}
  </div>
</div>
```

## Status Displays

### Turn Counter
```tsx
<div className="text-sm">
  <span className="text-muted-foreground uppercase">TURN:</span>{' '}
  <span className="text-primary text-terminal-glow font-bold">
    {String(turnNumber).padStart(3, '0')}
  </span>
</div>
```

### Game Status
```tsx
<div className="text-sm">
  <span className="text-muted-foreground uppercase">STATUS:</span>{' '}
  <span className={`uppercase font-bold ${
    gameOver ? 'text-error terminal-flicker' : 'text-success'
  }`}>
    {gameOver ? 'COMPLETE' : 'IN_PROGRESS'}
  </span>
</div>
```

### Participant Status
```tsx
<div className="flex items-center gap-3 text-xs">
  <span className="text-success">●</span>
  <span className="text-communicator-glow font-bold uppercase">ALPHA</span>
  <span className="text-muted-foreground">|</span>
  <span className="uppercase">COMMUNICATOR</span>
  <span className="text-muted-foreground">|</span>
  <span className="uppercase">OPENAI_GPT4</span>
</div>
```

## Loading States

### Spinner with Text
```tsx
<div className="flex items-center gap-3">
  <Loader className="animate-spin" size={20} />
  <span className="uppercase">LOADING<span className="cursor-blink">_</span></span>
</div>
```

### Processing State
```tsx
<div className="text-center py-12">
  <p className="uppercase text-sm">PROCESSING_REQUEST...</p>
  <span className="inline-block mt-2 cursor-blink">█</span>
</div>
```

### Awaiting Input
```tsx
<div className="text-center py-12 text-muted-foreground">
  <p className="uppercase text-sm">AWAITING_INPUT...</p>
  <p className="text-xs mt-2">Execute NEXT_TURN to begin</p>
  <span className="inline-block mt-2 cursor-blink">█</span>
</div>
```

## Error States

### Error Banner
```tsx
<div className="terminal-panel border-error bg-destructive/10">
  <div className="text-error terminal-flicker uppercase font-bold">
    ERROR: {errorMessage}
  </div>
</div>
```

### Error Page
```tsx
<div className="terminal-panel border-error max-w-2xl">
  <h1 className="text-3xl font-bold uppercase mb-4 text-error terminal-flicker">
    ███ SYSTEM_ERROR ███
  </h1>
  <p className="text-sm text-muted-foreground mb-4">
    &gt;&gt; {errorDetails}
  </p>
  <button className="terminal-button-danger w-full">
    REBOOT_SYSTEM
  </button>
</div>
```

## Game Over States

### Win Banner
```tsx
<div className="terminal-panel border-success">
  <div className="text-center">
    <div className="text-2xl font-bold uppercase mb-4 text-success">
      ███ GAME_OVER ███ RESULT: SUCCESS ███
    </div>
    <div className="space-y-2 text-sm">
      <div>&gt;&gt;&gt; OBJECTIVE_COMPLETE</div>
      <div>&gt;&gt;&gt; RECEIVER_STATUS: SUCCESS</div>
    </div>
  </div>
</div>
```

### Loss Banner
```tsx
<div className="terminal-panel border-error">
  <div className="text-center">
    <div className="text-2xl font-bold uppercase mb-4 text-error terminal-flicker">
      ███ GAME_OVER ███ RESULT: FAILURE ███
    </div>
    <div className="space-y-2 text-sm">
      <div>&gt;&gt;&gt; OBJECTIVE_FAILED</div>
      <div>&gt;&gt;&gt; TRIES_EXHAUSTED: 3/3</div>
    </div>
  </div>
</div>
```

## Animation Classes

### Flicker (for errors/alerts)
```tsx
<span className="terminal-flicker">CRITICAL_ERROR</span>
```

### Cursor Blink
```tsx
<span className="cursor-blink">█</span>
<span className="cursor-blink">_</span>
```

### Glitch Hover
```tsx
<button className="glitch-hover">UNSTABLE_BUTTON</button>
```

## Layout Utilities

### Full Page Container
```tsx
<div className="min-h-screen p-4 scanlines crt-screen">
  <div className="max-w-6xl mx-auto">
    {/* Content */}
  </div>
</div>
```

### Centered Modal/Dialog
```tsx
<div className="fixed inset-0 bg-terminal-bg/95 backdrop-blur-sm flex items-center justify-center z-50 scanlines crt-screen">
  <div className="terminal-panel max-w-4xl">
    {/* Modal content */}
  </div>
</div>
```

### Scrollable Content Area
```tsx
<div className="max-h-[600px] overflow-y-auto pr-2">
  {/* Scrollable content */}
</div>
```

## Spacing Conventions

```tsx
// Component spacing
<div className="space-y-4">  {/* Vertical spacing between items */}
<div className="space-x-2">  {/* Horizontal spacing between items */}
<div className="gap-3">      {/* Flex/Grid gap */}

// Padding
<div className="p-4">   {/* Standard panel padding */}
<div className="px-3 py-2">  {/* Input padding */}

// Margins
<div className="mb-4">  {/* Bottom margin between sections */}
<div className="mt-6">  {/* Top margin for separation */}
```

## Responsive Patterns

### Mobile-First Flex
```tsx
<div className="flex flex-col sm:flex-row gap-4">
  {/* Stacks on mobile, row on desktop */}
</div>
```

### Responsive Grid
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
  {/* 1 column mobile, 2 columns desktop */}
</div>
```

---

**Remember**: Consistency is key! Always use UPPERCASE for system text, monospace fonts, and semantic color coding for agent roles.
