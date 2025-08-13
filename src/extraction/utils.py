import re
from typing import List, Set

from clients.AlertTermsClient import AlertTermsClient
from clients.AlertTextClient import AlertTextClient
from config.settings import settings
from models.alerts import Alert
from models.extraction import TermMatch, TermMatchList
from models.query_terms import QueryTerm


def find_term_matches(
    alert_client: AlertTextClient,
    terms_client: AlertTermsClient,
) -> TermMatchList:
    """
    Find matches between query terms and alert content from API clients.

    This function orchestrates the process of fetching alerts and terms,
    then iterates through them to find and return all unique matches.

    Args:
        alert_client: An instance of `AlertTextClient` to fetch alerts.
        terms_client: An instance of `AlertTermsClient` to fetch terms.

    Returns:
        A `TermMatchList` containing all unique matches found.

    Raises:
        requests.RequestException: If an API call fails.
        pydantic.ValidationError: If API responses do not match the expected schema.
    """
    alerts = alert_client.fetch_alerts()
    terms = terms_client.fetch_terms()

    matches: Set[TermMatch] = set()

    for alert in alerts.alerts:
        for term in terms.terms:
            if _is_term_in_alert(term, alert):
                matches.add(TermMatch(alert_id=alert.id, term_id=term.id))

    return TermMatchList(
        matches=sorted(list(matches), key=lambda m: (m.alert_id, m.term_id))
    )


def _is_term_in_alert(term: QueryTerm, alert: Alert) -> bool:
    """
    Check if a query term is present in the content of an alert.

    This function handles different matching strategies based on the term's
    properties, such as language filtering and word order.

    Args:
        term: The `QueryTerm` to search for.
        alert: The `Alert` to search within.

    Returns:
        `True` if the term is found in the alert, `False` otherwise.
    """
    alert_texts = _get_relevant_alert_texts(term, alert)
    if not alert_texts:
        return False

    combined_text = " ".join(alert_texts).lower()
    term_text = term.text.lower()

    if term.keepOrder:
        # Exact phrase match (case-insensitive)
        return term_text in combined_text
    else:
        # All words must be present, but order does not matter.
        # We use regex word boundaries to ensure whole word matching.
        return all(
            re.search(r"\b" + re.escape(word) + r"\b", combined_text)
            for word in term_text.split()
        )


def _get_relevant_alert_texts(term: QueryTerm, alert: Alert) -> List[str]:
    """
    Extract relevant text from an alert based on the query term's language.

    If `settings.filter_by_language` is True, only content matching the
    term's language is returned. Otherwise, all content is returned.

    Args:
        term: The `QueryTerm` specifying the language.
        alert: The `Alert` containing the text content.

    Returns:
        A list of strings, each representing a piece of relevant alert text.
    """
    if settings.filter_by_language:
        return [
            content.text
            for content in alert.contents
            if content.language == term.language
        ]
    else:
        return [content.text for content in alert.contents]
