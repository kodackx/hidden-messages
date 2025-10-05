# Hidden Messages - Frontend UI

> **Retro terminal interface for experimental AI steganography research**

A React + TypeScript + Vite frontend that provides an interactive interface for the Hidden Messages AI steganography experiment. This UI connects to the Hidden Messages backend to facilitate conversations between AI agents attempting to communicate covertly.

## Overview

This frontend is designed to be plugged into the existing **Hidden Messages** project, which includes:
- A database for storing sessions and conversation history
- A backend prototype API for orchestrating AI agent interactions
- Support for multiple LLM providers (OpenAI, Anthropic, Google Gemini)

The UI features an authentic 1980s CRT terminal aesthetic with scanlines, phosphor glow effects, and color-coded agent displays.

## Quick Start

### Prerequisites
- Node.js 20+ and npm
- Hidden Messages backend running at `http://localhost:8000`

### Installation

```sh
# Clone the repository
git clone <YOUR_GIT_URL>

# Navigate to the project directory
cd covert-comm-ui

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open http://localhost:5173 to access the application.

**Mock Mode**: The app starts in **MOCK mode** by default, which uses simulated API responses for testing the UI without requiring the backend. Toggle between MOCK and LIVE modes using the switch in the top-right corner.

## Technologies

This project is built with:

- **Vite** - Fast build tool and dev server
- **TypeScript** - Type-safe JavaScript
- **React 18** - UI framework
- **Tailwind CSS** - Utility-first styling
- **shadcn-ui** - Component library
- **Lucide React** - Icon library
- **Sonner** - Toast notifications

## Features

- **Session Setup**: Configure conversation topics, secret words, and AI participants
- **Turn-by-turn Execution**: Manual control over conversation flow
- **Internal Thoughts Toggle**: Reveal agent reasoning processes
- **Guess Tracking**: Monitor receiver attempts to identify the secret word
- **Session History**: View complete conversation logs
- **Mock Mode**: Test the UI without backend connectivity
- **Retro Terminal Aesthetic**: CRT effects, scanlines, and phosphor glow

## Documentation

For detailed information, see:
- **[PROJECT_README.md](./PROJECT_README.md)** - Complete frontend documentation
- **[QUICK_START.md](./QUICK_START.md)** - Getting started guide
- **[MOCK_MODE_GUIDE.md](./MOCK_MODE_GUIDE.md)** - Mock mode details
- **[TERMINAL_UI_REFERENCE.md](./TERMINAL_UI_REFERENCE.md)** - UI component reference

## Development

```sh
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Deployment

Build the production bundle:

```sh
npm run build
```

The optimized files will be in the `dist/` directory. Serve with any static file server or deploy to your preferred hosting platform.

## License

Research project - see main Hidden Messages repository for details.
