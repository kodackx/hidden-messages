# Documentation Index

This directory contains all documentation for the Hidden Messages project.

## Quick Reference

### Getting Started
- **[Integration Guide](INTEGRATION_GUIDE.md)** - Complete guide for setting up and running the full stack
- **[Makefile Reference](MAKEFILE_REFERENCE.md)** - All available make commands with examples and workflows

### Development
- **[Agents Overview](agents.md)** - Detailed explanation of agent roles, communication protocols, and output contracts
- **[Testing Summary](TESTING_SUMMARY.md)** - Overview of testing approach, strategies, and results
- **[E2E Tests](E2E_TESTS_ADDED.md)** - End-to-end testing setup and documentation
- **[E2E Test Output](e2etests_output_oct2.md)** - Sample output from end-to-end test runs

### Frontend
- **[Frontend Spec](FRONTEND_SPEC.md)** - Complete frontend architecture and design specification
- **[Frontend Handoff](FRONTEND_HANDOFF.md)** - Frontend integration notes and handoff documentation
- **[Terminal UI Reference](TERMINAL_UI_REFERENCE.md)** - Terminal-style UI component guide

### Project History
- **[Spec Updates Summary](SPEC_UPDATES_SUMMARY.md)** - Historical changes and evolution of project specifications

## Documentation Organization

### Root Level (../)
Essential files kept in the root for immediate reference:
- `README.md` - Main project overview and quick start
- `CLAUDE.md` - Guidelines for AI coding assistants
- `CODE_REVIEW_FEEDBACK.md` - Code review insights

### Backend (../backend/)
Backend-specific documentation:
- `backend/README.md` - Backend setup and API documentation
- `backend/tests/README.md` - Backend testing guide

### Frontend (../frontend/)
Frontend-specific documentation:
- `frontend/README.md` - Frontend development guide
- `frontend/QUICK_START.md` - Quick start for frontend development
- `frontend/MOCK_MODE_GUIDE.md` - Guide for using mock mode during development
- `frontend/PROJECT_README.md` - Detailed project information

### Ideas (../ideas/)
Design and planning documents:
- `ideas/prd.md` - Product requirements document
- `ideas/prompts_ideas.md` - Ideas for agent prompts and strategies
- `ideas/ui-ux-design.md` - UI/UX design notes and mockups

## Quick Links

### For Developers
1. Start here: [Integration Guide](INTEGRATION_GUIDE.md)
2. Then review: [Makefile Reference](MAKEFILE_REFERENCE.md)
3. Understand agents: [Agents Overview](agents.md)

### For Frontend Work
1. [Frontend Spec](FRONTEND_SPEC.md) - Architecture overview
2. [Terminal UI Reference](TERMINAL_UI_REFERENCE.md) - Component guide
3. [Frontend Handoff](FRONTEND_HANDOFF.md) - Integration notes

### For Testing
1. [Testing Summary](TESTING_SUMMARY.md) - Overall testing approach
2. [E2E Tests](E2E_TESTS_ADDED.md) - End-to-end test setup
3. Backend tests: `../backend/tests/README.md`

## Contributing to Documentation

When adding new documentation:
1. Place it in the appropriate directory (`docs/`, `backend/`, `frontend/`, or `ideas/`)
2. Update this index with a link and brief description
3. Update the main `README.md` if it's a major guide
4. Use clear, descriptive filenames (e.g., `INTEGRATION_GUIDE.md` not `guide.md`)

## File Naming Convention

- `UPPERCASE_WITH_UNDERSCORES.md` - Guides, references, and summaries
- `lowercase-with-dashes.md` - Design docs and planning materials
- `README.md` - Entry point documentation for each directory
