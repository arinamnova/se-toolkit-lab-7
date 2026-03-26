"""LMS API client with Bearer token authentication."""

import httpx


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        """Initialize the API client.
        
        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002)
            api_key: Bearer token for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._headers = {"Authorization": f"Bearer {api_key}"}

    def get_items(self) -> list[dict] | None:
        """Fetch all items (labs and tasks).
        
        Returns:
            List of items, or None if the request fails.
            
        Raises:
            httpx.RequestError: If the request fails.
        """
        url = f"{self.base_url}/items/"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self._headers)
            response.raise_for_status()
            return response.json()

    def get_pass_rates(self, lab: str) -> list[dict] | None:
        """Fetch pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., "lab-04")
            
        Returns:
            List of pass rate objects, or None if the request fails.
            
        Raises:
            httpx.RequestError: If the request fails.
        """
        url = f"{self.base_url}/analytics/pass-rates"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self._headers, params={"lab": lab})
            response.raise_for_status()
            return response.json()
