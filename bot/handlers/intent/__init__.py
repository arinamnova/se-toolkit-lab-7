"""Intent-based natural language router using LLM."""

import json
import sys

# Import config and services directly (bot_dir is in sys.path)
import config
from services.llm_client import LLMClient, SYSTEM_PROMPT, TOOLS


def route(message: str) -> str:
    """Route a natural language message through the LLM.

    Args:
        message: User's natural language query

    Returns:
        LLM-generated response
    """
    # Check if LLM is configured
    if not config.settings.llm_api_key or not config.settings.llm_api_base_url:
        return "LLM is not configured. Please set LLM_API_KEY and LLM_API_BASE_URL in .env.bot.secret"

    client = LLMClient(
        api_key=config.settings.llm_api_key,
        base_url=config.settings.llm_api_base_url,
        model=config.settings.llm_api_model,
    )

    # Initialize conversation with system prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    max_iterations = 10  # Prevent infinite loops, allow more for multi-step queries
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call LLM
        print(f"[LLM] Calling LLM (iteration {iteration})", file=sys.stderr)
        response = client.chat(messages, tools=TOOLS)

        # Check if LLM wants to call tools
        choice = response.get("choices", [{}])[0]
        message_data = choice.get("message", {})

        # Check for tool calls
        tool_calls = message_data.get("tool_calls", [])

        if not tool_calls:
            # LLM returned a final answer
            content = message_data.get("content", "")
            print(f"[LLM] Final response: {content[:100]}...", file=sys.stderr)
            return content

        # Execute tool calls
        print(f"[tool] LLM called {len(tool_calls)} tool(s)", file=sys.stderr)

        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            name = func.get("name", "")
            arguments_str = func.get("arguments", "{}")

            try:
                arguments = (
                    json.loads(arguments_str)
                    if isinstance(arguments_str, str)
                    else arguments_str
                )
            except json.JSONDecodeError:
                arguments = {}

            print(f"[tool] Executing: {name}({arguments})", file=sys.stderr)

            try:
                result = client.execute_tool(name, arguments)
                print(f"[tool] Result: {str(result)[:100]}...", file=sys.stderr)
            except Exception as e:
                result = {"error": str(e)}
                print(f"[tool] Error: {e}", file=sys.stderr)

            # Add tool result to conversation
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call],
                }
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", "unknown"),
                    "content": json.dumps(result, default=str)
                    if not isinstance(result, str)
                    else result,
                }
            )

        print(
            f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM",
            file=sys.stderr,
        )

    return "I'm having trouble processing your request. Please try rephrasing."
