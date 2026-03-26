#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Supports two modes:
- Test mode: uv run bot.py --test "/command" or uv run bot.py --test "natural language query"
- Telegram mode: uv run bot.py - starts Telegram polling
"""

import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent import route as route_intent


# Command registry: maps command strings to handler functions
COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def run_test_mode(query: str) -> None:
    """Run a command or natural language query in test mode.

    Args:
        query: The command or natural language query (e.g., "/start" or "what labs are available")
    """
    query = query.strip()

    # Check if it's a slash command
    if query.startswith("/"):
        parts = query.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd not in COMMANDS:
            print(f"Unknown command: {cmd}")
            print(f"Available commands: {', '.join(COMMANDS.keys())}")
            sys.exit(0)

        # Call the handler
        handler = COMMANDS[cmd]

        # Handle commands with arguments
        if cmd == "/scores" and args:
            response = handler(args[0])
        else:
            response = handler()
    else:
        # Natural language query - route through LLM
        response = route_intent(query)

    # Print response to stdout (for autochecker verification)
    print(response)
    sys.exit(0)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: bot.py --test <command>", file=sys.stderr)
        print('Example: bot.py --test "/start"', file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Error: --test requires a command argument", file=sys.stderr)
            print('Example: bot.py --test "/start"', file=sys.stderr)
            sys.exit(1)
        run_test_mode(sys.argv[2])
    else:
        print(f"Unknown mode: {sys.argv[1]}", file=sys.stderr)
        print("Use --test <command> to run in test mode", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
