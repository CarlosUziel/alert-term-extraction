"""Pydantic models for representing term matching results."""

from datetime import datetime, timezone
from typing import List

from models.alerts import AlertList
from models.query_terms import QueryTermList
from pydantic import BaseModel, Field


class TermMatch(BaseModel):
    """
    Represents a unique match between an alert and a query term.

    This model is hashable to allow for efficient storage in sets,
    preventing duplicate matches.

    Attributes:
        alert_id: The ID of the alert where the match was found.
        term_id: The ID of the term that was matched.
    """

    alert_id: str = Field(..., description="The ID of the matched alert.")
    term_id: int = Field(..., description="The ID of the matched query term.")

    def __hash__(self) -> int:
        """
        Provide a hash based on the composite key of alert_id and term_id.
        """
        return hash((self.alert_id, self.term_id))

    def __eq__(self, other: object) -> bool:
        """
        Define equality based on the alert_id and term_id.
        """
        if not isinstance(other, TermMatch):
            return NotImplemented
        return self.alert_id == other.alert_id and self.term_id == other.term_id


class LogEntry(BaseModel):
    """
    Represents a single log entry for the extraction process.

    Attributes:
        created_at: The UTC timestamp indicating when the list was generated.
        alert_text_data: The alert text data fetched from the API.
        alert_query_term_data: The query term data fetched from the API.
        matches: A list of `TermMatch` objects.
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The UTC timestamp of when the match list was created.",
    )
    alert_text_data: AlertList = Field(
        ..., description="The alert text data fetched from the API."
    )
    alert_query_term_data: QueryTermList = Field(
        ..., description="The query term data fetched from the API."
    )
    matches: List[TermMatch] = Field(..., description="A list of unique term matches.")
