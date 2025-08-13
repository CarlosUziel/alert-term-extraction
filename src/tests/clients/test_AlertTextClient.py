import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError

from clients.AlertTextClient import AlertTextClient
from models.alerts import Alert, AlertList


@pytest.fixture
def mock_requests_get():
    """Fixture to patch requests.get."""
    with patch("requests.get") as mock_get:
        yield mock_get


def test_fetch_alerts_success(mock_requests_get):
    """
    Test successful fetching and validation of alerts.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": "1",
            "contents": [{"text": "alert1", "type": "title", "language": "en"}],
            "date": "2023-01-01T12:00:00Z",
            "inputType": "test",
        }
    ]
    mock_requests_get.return_value = mock_response

    client = AlertTextClient()

    # Act
    alerts = client.fetch_alerts()

    # Assert
    assert isinstance(alerts, AlertList)
    assert len(alerts.alerts) == 1
    assert isinstance(alerts.alerts[0], Alert)
    assert alerts.alerts[0].id == "1"
    assert isinstance(alerts.alerts[0].date, datetime)
    mock_requests_get.assert_called_once()


def test_fetch_alerts_http_error(mock_requests_get):
    """
    Test handling of an HTTP error during API call.
    """
    # Arrange
    mock_requests_get.side_effect = requests.RequestException("API is down")
    client = AlertTextClient()

    # Act & Assert
    with pytest.raises(requests.RequestException):
        client.fetch_alerts()


def test_fetch_alerts_validation_error(mock_requests_get):
    """
    Test handling of a Pydantic validation error for malformed data.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": "1"}]
    mock_requests_get.return_value = mock_response

    client = AlertTextClient()

    # Act & Assert
    with pytest.raises(ValidationError):
        client.fetch_alerts()


def test_fetch_alerts_request_error(mock_requests_get):
    """
    Test handling of request errors (e.g., connection errors).
    """
    # Arrange
    mock_requests_get.side_effect = requests.ConnectionError("Failed to connect")
    client = AlertTextClient()

    # Act & Assert
    with pytest.raises(requests.ConnectionError, match="Failed to connect"):
        client.fetch_alerts()


def test_fetch_alerts_invalid_response_format(mock_requests_get):
    """
    Test handling of an invalid API response format (not a list).
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "not a list"}
    mock_requests_get.return_value = mock_response

    client = AlertTextClient()

    # Act & Assert
    with pytest.raises(ValueError, match="API response is not a list as expected."):
        client.fetch_alerts()


def test_client_initialization_missing_config():
    """
    Test that the client raises an error if configuration is missing.
    """
    with patch("config.settings.settings.alert_text_api_url", new=None):
        with pytest.raises(ValueError, match="Alert text API URL is not configured."):
            AlertTextClient()

    with patch("config.settings.settings.alert_api_key", new=None):
        with pytest.raises(ValueError, match="Alert API key is not configured."):
            AlertTextClient()


@pytest.mark.parametrize("calls, delay", [(1, 0), (3, 0.1)])
def test_fetch_alerts_performance(calls, delay, mock_requests_get):
    """
    Test the performance of fetching alerts multiple times.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": "1",
            "contents": [{"text": "alert1", "type": "title", "language": "en"}],
            "date": "2023-01-01T12:00:00Z",
            "inputType": "test",
        }
    ]
    mock_requests_get.return_value = mock_response

    client = AlertTextClient()
    alerts = None

    # Act
    for _ in range(calls):
        if delay > 0:
            time.sleep(delay)
        alerts = client.fetch_alerts()

    # Assert
    assert isinstance(alerts, AlertList)
    assert alerts is not None
    assert len(alerts.alerts) > 0
