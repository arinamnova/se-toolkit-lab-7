"""Handler for /scores command."""

import httpx

import config


def handle_scores(lab_id: str | None = None) -> str:
    """Handle the /scores command.

    Args:
        lab_id: Lab identifier to filter scores (e.g., "lab-04").

    Returns:
        Pass rates for the specified lab or error message.
    """
    base_url = config.settings.lms_api_base_url
    api_key = config.settings.lms_api_key

    if not base_url or not api_key:
        return "Backend configuration missing. Check .env.bot.secret"

    if not lab_id:
        return "Please specify a lab ID. Usage: /scores lab-04"

    try:
        url = f"{base_url}/analytics/pass-rates"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"lab": lab_id}

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                return f"No pass rate data found for {lab_id}."

            # Format the response
            lines = [f"Pass rates for {lab_id}:"]
            for item in data:
                task_name = item.get("task", "Unknown")
                avg_score = item.get("avg_score", 0)  # Already a percentage
                attempts = item.get("attempts", 0)
                lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")

            return "\n".join(lines)

    except httpx.ConnectError:
        return f"Backend error: connection refused ({base_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"No data found for lab {lab_id}. Check the lab ID."
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"Backend error: {e}. Check your network configuration."
    except Exception as e:
        return f"Backend error: {e}"
