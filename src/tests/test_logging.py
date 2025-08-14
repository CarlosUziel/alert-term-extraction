"""Tests for the logging configuration and output."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from models.alerts import Alert, AlertContent, AlertList
from models.extraction import LogEntry
from models.query_terms import QueryTerm, QueryTermList

from extraction.utils import find_term_matches


@pytest.fixture
def mock_api_clients():
    """Fixture to create mock API clients with predefined data."""
    alert_client = MagicMock()
    terms_client = MagicMock()

    # Mock data for alerts
    mock_alerts = AlertList(
        alerts=[
            Alert(
                id="alert1",
                contents=[
                    AlertContent(
                        text="This is a test alert.", type="text", language="en"
                    )
                ],
                date=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                inputType="test",
            )
        ]
    )
    alert_client.fetch_alerts.return_value = mock_alerts

    # Mock data for query terms
    mock_terms = QueryTermList(
        terms=[
            QueryTerm(
                id=1,
                text="test",
                language="en",
                keepOrder=True,
            )
        ]
    )
    terms_client.fetch_terms.return_value = mock_terms

    return alert_client, terms_client, mock_alerts, mock_terms


def test_log_entry_schema(mock_api_clients):
    """
    Test that the generated log entry conforms to the LogEntry schema.
    """
    alert_client, terms_client, mock_alerts, mock_terms = mock_api_clients

    # Run the extraction process
    log_entry = find_term_matches(alert_client, terms_client)

    # Validate the structure of the log entry
    assert isinstance(log_entry, LogEntry)
    assert log_entry.alert_text_data == mock_alerts
    assert log_entry.alert_query_term_data == mock_terms
    assert len(log_entry.matches) == 1
    assert log_entry.matches[0].alert_id == "alert1"
    assert log_entry.matches[0].term_id == 1

    # Check that the output can be serialized to JSON and then parsed back
    # into a valid LogEntry model
    json_output = log_entry.model_dump_json()
    parsed_log_entry = LogEntry.model_validate(json.loads(json_output))

    assert parsed_log_entry == log_entry
