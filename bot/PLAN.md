# LMS Telegram Bot - Development Plan

## Overview

This document outlines the development plan for building a Telegram bot that integrates with the LMS (Learning Management System) backend. The bot provides students with commands to check their scores, view available labs, and ask questions using an LLM-powered intent router.

## Architecture

### Core Pattern: Separation of Concerns

The bot follows a layered architecture where **handlers** are pure functions that take input and return text responses. They have no dependency on Telegram. The Telegram-specific code lives only in the entry point (`bot.py`), which calls these handlers. This pattern enables:

- **Testability**: Handlers can be tested via `--test` mode without Telegram
- **Reusability**: Same handler logic works from CLI, tests, or Telegram
- **Maintainability**: Changes to Telegram API don't affect business logic

### Directory Structure

```
bot/
├── bot.py              # Entry point: Telegram polling + --test mode
├── config.py           # Environment variable loading with pydantic
├── handlers/           # Command handlers (pure functions)
│   ├── __init__.py
│   ├── start/          # /start command
│   ├── help/           # /help command
│   ├── health/         # /health command (checks backend)
│   ├── labs/           # /labs command
│   ├── scores/         # /scores command
│   └── intent/         # LLM-powered intent router (Task 3)
├── services/           # External service clients
│   ├── __init__.py
│   ├── lms_api.py      # LMS API client with Bearer auth
│   └── llm_client.py   # LLM client for intent routing
└── PLAN.md             # This file
```

## Task Breakdown

### Task 1: Scaffold and Test Mode

Create the project skeleton with `--test` mode. Handlers return placeholder text. The entry point supports:
- `uv run bot.py --test "/command"` - prints handler response to stdout
- `uv run bot.py` - starts Telegram polling (later tasks)

**Key files**: `bot.py`, `config.py`, `handlers/__init__.py`, `pyproject.toml`

### Task 2: Backend Integration

Implement real API calls to the LMS backend. Create an API client service that:
- Reads `LMS_API_BASE_URL` and `LMS_API_KEY` from `.env.bot.secret`
- Uses Bearer token authentication (`Authorization: Bearer <key>`)
- Handles errors gracefully (timeouts, 401, 404, 500)

**Key files**: `services/lms_api.py`, updated handlers (`labs.py`, `scores.py`, `health.py`)

### Task 3: LLM Intent Routing

Add natural language understanding using the LLM. Users can type plain text like "what labs are available?" instead of `/labs`. The intent router:
- Sends user message + tool descriptions to LLM
- LLM returns which tool (handler) to call
- Bot calls the appropriate handler

**Key files**: `services/llm_client.py`, `handlers/intent.py`

**Tool descriptions** are critical - they tell the LLM what each handler does. Quality of descriptions > prompt engineering.

### Task 4: Docker Deployment

Containerize the bot for deployment. Key considerations:
- Docker networking uses service names, not `localhost`
- Environment variables passed via `.env.docker.secret`
- Health checks and restart policies

**Key files**: `Dockerfile`, `docker-compose.yml` updates

## Configuration

Secrets are loaded from `.env.bot.secret` (gitignored):
- `BOT_TOKEN` - Telegram bot authentication
- `LMS_API_BASE_URL` - Backend API endpoint
- `LMS_API_KEY` - Bearer token for API auth
- `LLM_API_KEY` - LLM service authentication
- `LLM_API_BASE_URL` - LLM endpoint

## Testing Strategy

1. **Unit tests**: Call handlers directly with mock inputs
2. **Test mode**: `--test` flag for manual CLI testing
3. **Integration tests**: Deploy to VM, test in Telegram

## Deployment Flow

1. Local development with `--test` mode
2. Git workflow: issue → branch → PR → review → merge
3. Pull on VM: `git pull`
4. Restart bot: `pkill -f bot.py && nohup uv run bot.py > bot.log 2>&1 &`
5. Verify in Telegram
