"""Handler for /health command."""

import httpx

import config


def handle_health() -> str:
    """Handle the /health command.

    Returns:
        Backend API health status with item count or error message.
    """
    base_url = config.settings.lms_api_base_url
    api_key = config.settings.lms_api_key

    if not base_url or not api_key:
        return "Backend configuration missing. Check .env.bot.secret"

    try:
        url = f"{base_url}/items/"
        headers = {"Authorization": f"Bearer {api_key}"}
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            items = response.json()
            count = len(items) if isinstance(items, list) else "unknown"
            return f"Backend is healthy. {count} items available."
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({base_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"Backend error: {e}. Check your network configuration."
    except Exception as e:
        return f"Backend error: {e}"
