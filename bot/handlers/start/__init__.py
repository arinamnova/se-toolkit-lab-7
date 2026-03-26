"""Handler for /start command."""

# Inline keyboard buttons for common actions
START_KEYBOARD = {
    "inline_keyboard": [
        [
            {"text": "📚 Available Labs", "callback_data": "labs"},
            {"text": "📊 My Scores", "callback_data": "scores"},
        ],
        [
            {"text": "💪 Lab Health", "callback_data": "health"},
            {"text": "❓ Help", "callback_data": "help"},
        ],
        [
            {"text": "🏆 Top Students", "callback_data": "top_learners"},
            {"text": "📈 Completion Rate", "callback_data": "completion"},
        ],
    ]
}


def handle_start() -> str:
    """Handle the /start command.

    Returns:
        Welcome message for new users with keyboard hint.
    """
    return "Welcome to the LMS Bot! Use /help to see available commands."
