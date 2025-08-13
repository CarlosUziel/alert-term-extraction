"""Pydantic models for representing query terms used in extraction."""

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field


class QueryTerm(BaseModel):
    """
    Represents a single query term used for searching within alerts.

    Attributes:
        id: The unique identifier for the query term.
        text: The text to search for. Multiple words are space-separated.
        language: A two-letter language code (e.g., 'en', 'de').
        keepOrder: A boolean indicating the matching strategy.
            - If `True`, the words in `text` must appear as an exact phrase.
            - If `False`, the words can appear in any order in the text.
    """

    id: int = Field(..., description="Unique identifier for the query term.")
    text: str = Field(
        ..., description="The text to search for (words are space-separated)."
    )
    language: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Two-letter language code for the term (e.g., 'en').",
    )
    keepOrder: bool = Field(
        ...,
        alias="keepOrder",
        description="If true, match text as an exact phrase; otherwise, match words in any order.",
    )


class QueryTermList(BaseModel):
    """
    Represents a list of query terms, with a timestamp for creation.

    Attributes:
        terms: A list of `QueryTerm` objects.
        created_at: The UTC timestamp indicating when the list was created.
    """

    terms: List[QueryTerm] = Field(..., description="A list of query term objects.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The UTC timestamp of when the term list was created.",
    )
