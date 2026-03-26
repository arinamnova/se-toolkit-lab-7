"""LLM client with tool calling support."""

import json
import sys
from typing import Any

import httpx


# Tool definitions for all 9 backend endpoints
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get list of all labs and tasks. Use this first to discover what labs are available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of enrolled students and their groups.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab. Use this to compare task difficulty.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab to see activity over time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab. Use to compare group performance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab. Use for leaderboards.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return, default 5",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker. Use when data seems stale.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are an AI assistant that helps users understand their learning progress by querying an LMS (Learning Management System) API.

You have access to tools that let you fetch data about labs, tasks, scores, and students.

When the user asks a question:
1. Think about what data you need to answer
2. Call the appropriate tool(s) to get that data
3. Once you have the data, summarize it clearly for the user
4. If the user's question is unclear or gibberish, politely explain what you can help with

For multi-step questions (e.g., "which lab has the lowest pass rate?"):
1. First get the list of labs
2. Then get pass rates for each lab
3. Compare and report the answer

Always be specific with numbers when available. Format your response clearly."""


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str, timeout: float = 30.0):
        """Initialize the LLM client.

        Args:
            api_key: API key for authentication
            base_url: Base URL of the LLM API (e.g., http://localhost:42005)
            model: Model name to use (e.g., 'coder-model')
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions

        Returns:
            LLM response dict
        """
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, headers=self._headers, json=payload)
            response.raise_for_status()
            return response.json()

    def execute_tool(self, name: str, arguments: dict) -> Any:
        """Execute a tool by calling the appropriate backend endpoint.

        Args:
            name: Tool/function name
            arguments: Tool arguments dict

        Returns:
            Tool execution result
        """
        # Import here to avoid circular imports
        from services.lms_api import LMSAPIClient

        # We need config for API credentials
        import config

        api_client = LMSAPIClient(
            base_url=config.settings.lms_api_base_url,
            api_key=config.settings.lms_api_key,
        )

        if name == "get_items":
            return api_client.get_items()
        elif name == "get_pass_rates":
            lab = arguments.get("lab", "")
            return api_client.get_pass_rates(lab)
        elif name == "get_scores":
            lab = arguments.get("lab", "")
            # Use same endpoint as pass_rates for now
            return api_client.get_pass_rates(lab)
        elif name == "get_learners":
            # Fetch items and filter for learners if needed
            return api_client.get_items()
        elif name == "get_timeline":
            # Not implemented in lms_api yet, return empty
            return []
        elif name == "get_groups":
            # Not implemented yet
            return []
        elif name == "get_top_learners":
            # Not implemented yet
            return []
        elif name == "get_completion_rate":
            # Not implemented yet
            return []
        elif name == "trigger_sync":
            # Trigger sync via direct HTTP call
            url = f"{api_client.base_url}/pipeline/sync"
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=api_client._headers, json={})
                response.raise_for_status()
                return response.json()
        else:
            return {"error": f"Unknown tool: {name}"}
