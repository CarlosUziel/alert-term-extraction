"""Pydantic models for representing alerts and their contents."""

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field, field_validator


class AlertContent(BaseModel):
    """
    Represents a single piece of content within an alert.

    Attributes:
        text: The main text of the content.
        type: The type of content (e.g., 'title', 'snippet').
        language: The language of the text (e.g., 'en', 'de').
    """

    text: str = Field(..., description="The main text of the content.")
    type: str = Field(
        ..., description="The type of content (e.g., 'title', 'snippet')."
    )
    language: str = Field(
        ..., description="The language of the text (e.g., 'en', 'de')."
    )


class Alert(BaseModel):
    """
    Represents a single alert from the API.

    Attributes:
        id: The unique identifier for the alert.
        contents: A list of `AlertContent` objects.
        date: The timestamp when the alert was issued.
        inputType: The source or type of the alert input.
    """

    id: str = Field(..., description="The unique identifier for the alert.")
    contents: List[AlertContent] = Field(
        ..., description="A list of content pieces for the alert."
    )
    date: datetime = Field(..., description="The timestamp when the alert was issued.")
    inputType: str = Field(..., description="The source or type of the alert input.")

    @field_validator("date", mode="before")
    @classmethod
    def ensure_timezone(cls, v):
        """Ensure the datetime object is timezone-aware (UTC)."""
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class AlertList(BaseModel):
    """
    Represents a list of alerts, with a timestamp for when the list was created.

    Attributes:
        alerts: A list of `Alert` objects.
        created_at: The UTC timestamp of when the list was created.
    """

    alerts: List[Alert] = Field(..., description="A list of alert objects.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The UTC timestamp indicating when the list was created.",
    )
