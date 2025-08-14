"""Tests for the extraction utility functions."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from config.settings import settings
from extraction.utils import _is_term_in_alert, find_term_matches
from models.alerts import Alert, AlertContent, AlertList
from models.extraction import TermMatch
from models.query_terms import QueryTerm, QueryTermList


# Fixtures for reusable test data
@pytest.fixture
def sample_alert() -> Alert:
    """Returns a sample Alert object for testing."""
    return Alert(
        id="alert_123",
        contents=[
            AlertContent(
                text="A major supply chain disruption occurred.",
                type="title",
                language="en",
            ),
            AlertContent(
                text="The disruption in the supply chain affects all sectors.",
                type="snippet",
                language="en",
            ),
            AlertContent(
                text="Eine Störung der Lieferkette.", type="title", language="de"
            ),
        ],
        date=datetime(2023, 1, 1),
        inputType="news",
    )


@pytest.fixture
def simple_alert() -> Alert:
    """Returns a simple Alert object with one content piece."""
    return Alert(
        id="alert_simple",
        contents=[
            AlertContent(
                text="The quick brown fox jumps over the lazy dog.",
                type="text",
                language="en",
            )
        ],
        date=datetime(2023, 1, 1),
        inputType="news",
    )


# --- Tests for _is_term_in_alert ---


@pytest.mark.parametrize(
    "term_text, keep_order, expected",
    [
        ("supply chain", True, True),
        ("SUPPLY CHAIN", True, True),  # Case-insensitivity
        ("supply chain disruption", True, True),
        ("sectors", True, True),
        ("chain supply", True, False),  # Order matters
        ("supply chain", False, True),
        ("chain supply", False, True),  # Order does not matter
        ("disruption sectors", False, True),
        ("nonexistent term", True, False),
        ("nonexistent term", False, False),
        ("supply nonexistent", False, True),  # One word matches
        ("nonexistent supply", False, True),  # One word matches, different order
    ],
)
def test_is_term_in_alert_various_cases(term_text, keep_order, expected, sample_alert):
    """Test term matching with different term texts and keepOrder flags."""
    term = QueryTerm(id=1, text=term_text, language="en", keepOrder=keep_order)
    settings.filter_by_language = True
    assert _is_term_in_alert(term, sample_alert) is expected


def test_is_term_in_alert_language_mismatch(sample_alert):
    """Test that a term does not match if its language is not in the alert (with filtering)."""
    term = QueryTerm(id=1, text="supply chain", language="fr", keepOrder=True)
    settings.filter_by_language = True
    assert not _is_term_in_alert(term, sample_alert)


def test_is_term_in_alert_whole_word_matching(simple_alert):
    """Test that matching respects whole word boundaries."""
    term_positive = QueryTerm(id=1, text="fox", language="en", keepOrder=False)
    term_negative = QueryTerm(id=2, text="ox", language="en", keepOrder=False)
    settings.filter_by_language = True
    assert _is_term_in_alert(term_positive, simple_alert)
    assert not _is_term_in_alert(term_negative, simple_alert)


# --- Tests for find_term_matches ---


@pytest.fixture
def mock_alert_client() -> MagicMock:
    """Fixture for a mocked AlertTextClient."""
    client = MagicMock()
    alerts = [
        Alert(
            id="a1",
            contents=[AlertContent(text="term one", language="en", type="")],
            date=datetime.now(),
            inputType="test",
        ),
        Alert(
            id="a2",
            contents=[AlertContent(text="term two", language="en", type="")],
            date=datetime.now(),
            inputType="test",
        ),
    ]
    client.fetch_alerts.return_value = AlertList(alerts=alerts)
    return client


@pytest.fixture
def mock_terms_client() -> MagicMock:
    """Fixture for a mocked AlertTermsClient."""
    client = MagicMock()
    terms = [
        QueryTerm(id=1, text="term one", language="en", keepOrder=True),
        QueryTerm(id=2, text="two term", language="en", keepOrder=False),
        QueryTerm(id=3, text="no match", language="en", keepOrder=True),
    ]
    client.fetch_terms.return_value = QueryTermList(terms=terms)
    return client


def test_find_term_matches_finds_correct_matches(mock_alert_client, mock_terms_client):
    """Test that find_term_matches correctly identifies and returns unique matches."""
    settings.filter_by_language = True
    result = find_term_matches(mock_alert_client, mock_terms_client)

    assert len(result.matches) == 3
    assert TermMatch(alert_id="a1", term_id=1) in result.matches
    assert TermMatch(alert_id="a2", term_id=2) in result.matches
    assert TermMatch(alert_id="a1", term_id=2) in result.matches


def test_find_term_matches_returns_sorted_results(mock_alert_client, mock_terms_client):
    """Test that the returned matches are sorted."""
    # Add another match to test sorting
    mock_alert_client.fetch_alerts.return_value.alerts.append(
        Alert(
            id="a0",
            contents=[AlertContent(text="term two", language="en", type="")],
            date=datetime.now(),
            inputType="test",
        )
    )
    result = find_term_matches(mock_alert_client, mock_terms_client)

    assert result.matches == [
        TermMatch(alert_id="a0", term_id=2),
        TermMatch(alert_id="a1", term_id=1),
        TermMatch(alert_id="a1", term_id=2),
        TermMatch(alert_id="a2", term_id=2),
    ]


def test_find_term_matches_no_matches(mock_alert_client, mock_terms_client):
    """Test that an empty list is returned when no matches are found."""
    mock_terms_client.fetch_terms.return_value.terms = [
        QueryTerm(id=3, text="no match", language="en", keepOrder=True)
    ]
    result = find_term_matches(mock_alert_client, mock_terms_client)
    assert len(result.matches) == 0


# --- Tests for TermMatch model ---


def test_term_match_equality_and_hashing():
    """Test the equality and hash implementation of the TermMatch model."""
    match1 = TermMatch(alert_id="alert_1", term_id=1)
    match2 = TermMatch(alert_id="alert_1", term_id=1)
    match3 = TermMatch(alert_id="alert_2", term_id=1)
    match4 = TermMatch(alert_id="alert_1", term_id=2)

    # Test equality
    assert match1 == match2
    assert match1 != match3
    assert match1 != match4
    assert match1 != "not a match"

    # Test hashing
    match_set = {match1, match2}
    assert len(match_set) == 1
    assert match1 in match_set

    match_set.add(match3)
    assert len(match_set) == 2
    assert match3 in match_set
