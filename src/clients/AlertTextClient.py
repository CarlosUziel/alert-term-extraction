import requests

from config.settings import settings
from models.alerts import AlertList


class AlertTextClient:
    """
    Client to fetch alert objects from the Prewave API.

    This client handles communication with the alert text API, including
    authentication and data validation.
    """

    def __init__(self, timeout: int = 10):
        """
        Initializes the AlertTextClient.

        Args:
            timeout: The timeout for API requests in seconds.
        """
        if not settings.alert_text_api_url:
            raise ValueError("Alert text API URL is not configured.")
        if not settings.alert_api_key:
            raise ValueError("Alert API key is not configured.")

        self.base_url = settings.alert_text_api_url
        self.api_key = settings.alert_api_key
        self.timeout = timeout

    def fetch_alerts(self) -> AlertList:
        """
        Fetches the list of alerts from the API.

        Returns:
            An `AlertList` object containing the validated alerts.

        Raises:
            requests.RequestException: If the API request fails.
            ValidationError: If the API response is not a valid list of alerts.
            ValueError: If the API response is not in the expected format.
        """
        url = f"{self.base_url}?key={self.api_key}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise ValueError("API response is not a list as expected.")

        return AlertList.model_validate({"alerts": data})
