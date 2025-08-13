import requests

from config.settings import settings
from models.query_terms import QueryTermList


class AlertTermsClient:
    """
    Client to fetch alert query terms from the Prewave API.

    This client handles the communication with the alert terms API,
    including authentication and data validation.
    """

    def __init__(self, timeout: int = 10):
        """
        Initializes the AlertTermsClient.

        Args:
            timeout: The timeout for API requests in seconds.
        """
        if not settings.alert_terms_api_url:
            raise ValueError("Alert terms API URL is not configured.")
        if not settings.alert_api_key:
            raise ValueError("Alert API key is not configured.")

        self.base_url = settings.alert_terms_api_url
        self.api_key = settings.alert_api_key
        self.timeout = timeout

    def fetch_terms(self) -> QueryTermList:
        """
        Fetches the list of query terms from the API.

        Returns:
            A `QueryTermList` object containing the validated query terms.

        Raises:
            requests.RequestException: If the API request fails.
            ValidationError: If the API response is not a valid list of terms.
            ValueError: If the API response is not in the expected format.
        """
        url = f"{self.base_url}?key={self.api_key}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise ValueError("API response is not a list as expected.")

        return QueryTermList.model_validate({"terms": data})
