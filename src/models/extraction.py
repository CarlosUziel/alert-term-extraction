"""Pydantic models for representing term matching results."""

from datetime import datetime, timezone
from typing import List

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


class TermMatchList(BaseModel):
    """
    Represents a list of term matches, with a timestamp for creation.

    Attributes:
        matches: A list of `TermMatch` objects.
        created_at: The UTC timestamp indicating when the list was generated.
    """

    matches: List[TermMatch] = Field(..., description="A list of unique term matches.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The UTC timestamp of when the match list was created.",
    )
