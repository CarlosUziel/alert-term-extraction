import time
from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError

from clients.AlertTermsClient import AlertTermsClient
from models.query_terms import QueryTerm, QueryTermList


@pytest.fixture
def mock_requests_get():
    """Fixture to patch requests.get."""
    with patch("requests.get") as mock_get:
        yield mock_get


def test_fetch_terms_success(mock_requests_get):
    """
    Test successful fetching and validation of alert terms.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "text": "term1", "language": "en", "keepOrder": True}
    ]
    mock_requests_get.return_value = mock_response

    client = AlertTermsClient()

    # Act
    terms = client.fetch_terms()

    # Assert
    assert isinstance(terms, QueryTermList)
    assert len(terms.terms) == 1
    assert isinstance(terms.terms[0], QueryTerm)
    assert terms.terms[0].id == 1
    mock_requests_get.assert_called_once()


def test_fetch_terms_http_error(mock_requests_get):
    """
    Test handling of an HTTP error during API call.
    """
    # Arrange
    mock_requests_get.side_effect = requests.RequestException("API is down")
    client = AlertTermsClient()

    # Act & Assert
    with pytest.raises(requests.RequestException):
        client.fetch_terms()


def test_fetch_terms_validation_error(mock_requests_get):
    """
    Test handling of a Pydantic validation error for malformed data.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "text": "term1"}]  # Missing fields
    mock_requests_get.return_value = mock_response

    client = AlertTermsClient()

    # Act & Assert
    with pytest.raises(ValidationError):
        client.fetch_terms()


def test_fetch_terms_invalid_response_format(mock_requests_get):
    """
    Test handling of an invalid API response format (not a list).
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "not a list"}
    mock_requests_get.return_value = mock_response

    client = AlertTermsClient()

    # Act & Assert
    with pytest.raises(ValueError, match="API response is not a list as expected."):
        client.fetch_terms()


def test_client_initialization_missing_config():
    """
    Test that the client raises an error if configuration is missing.
    """
    with patch("config.settings.settings.alert_terms_api_url", new=None):
        with pytest.raises(ValueError, match="Alert terms API URL is not configured."):
            AlertTermsClient()

    with patch("config.settings.settings.alert_api_key", new=None):
        with pytest.raises(ValueError, match="Alert API key is not configured."):
            AlertTermsClient()


@pytest.mark.parametrize("calls, delay", [(1, 0), (3, 0.1)])
def test_fetch_terms_performance(calls, delay, mock_requests_get):
    """
    Test the performance of fetching terms multiple times.
    This is a simplified version of the original test.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "text": "term1", "language": "en", "keepOrder": True}
    ]
    mock_requests_get.return_value = mock_response

    client = AlertTermsClient()
    terms = None

    # Act
    for _ in range(calls):
        if delay > 0:
            time.sleep(delay)
        terms = client.fetch_terms()

    # Assert
    assert isinstance(terms, QueryTermList)
    assert terms is not None
    assert len(terms.terms) > 0


def test_fetch_terms_request_error(mock_requests_get):
    """
    Test handling of a request error (e.g., connection error) during API call.
    """
    # Arrange
    mock_requests_get.side_effect = requests.ConnectionError("Failed to connect")
    client = AlertTermsClient()

    # Act & Assert
    with pytest.raises(requests.ConnectionError, match="Failed to connect"):
        client.fetch_terms()
