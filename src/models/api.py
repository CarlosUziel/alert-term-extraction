"""Pydantic models for the API request and response structures."""

from typing import Optional

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """
    Defines the request body for starting an alert term extraction process.

    Attributes:
        frequency_ms: The interval in milliseconds for checking new alerts.
                      Must be between 100 and 1000.
        total_checks: The total number of checks to perform before stopping.
                      If `None`, the process will run indefinitely. Must be at least 1.
    """

    frequency_ms: int = Field(
        ...,
        ge=100,
        le=1000,
        description="Frequency of checks in milliseconds (must be between 100 and 1000).",
    )
    total_checks: Optional[int] = Field(
        default=None,
        ge=1,
        description="Total number of checks to perform. If null, runs indefinitely.",
    )


class ExtractionResponse(BaseModel):
    """
    Defines the JSON response for extraction-related endpoints.

    Attributes:
        message: A descriptive message about the result of the operation.
        process_id: The process ID of the background extraction task, if applicable.
    """

    message: str = Field(
        ..., description="A descriptive message about the operation's result."
    )
    process_id: Optional[int] = Field(
        default=None,
        description="The process ID of the background task, if applicable.",
    )
