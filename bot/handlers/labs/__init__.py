"""Handler for /labs command."""

import httpx

import config


def handle_labs() -> str:
    """Handle the /labs command.

    Returns:
        List of available labs from the backend.
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

            if not items:
                return "No labs available."

            # Group items by lab
            labs = {}
            for item in items:
                if item.get("type") == "lab":
                    lab_id = item.get("id", "unknown")
                    lab_title = item.get("title", f"Lab {lab_id}")
                    labs[lab_id] = lab_title

            if not labs:
                return "No labs available."

            lines = ["Available labs:"]
            for lab_id, lab_name in sorted(labs.items()):
                lines.append(f"- {lab_name}")

            return "\n".join(lines)

    except httpx.ConnectError:
        return f"Backend error: connection refused ({base_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"Backend error: {e}. Check your network configuration."
    except Exception as e:
        return f"Backend error: {e}"
