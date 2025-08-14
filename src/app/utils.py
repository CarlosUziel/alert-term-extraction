"""Utility functions for the FastAPI application."""

from typing import TYPE_CHECKING, Optional

from clients.AlertTermsClient import AlertTermsClient
from clients.AlertTextClient import AlertTextClient
from config.logger import logger
from extraction.utils import find_term_matches

if TYPE_CHECKING:
    from multiprocessing.synchronize import Event


def extraction_worker(
    frequency_ms: int,
    total_checks: Optional[int],
    stop_event: "Event",
):
    """
    Worker function that runs the alert term extraction process.

    This function is designed to be executed in a separate process. It periodically
    fetches alert texts and a list of terms, then searches for matches.

    Args:
        frequency_ms: The interval in milliseconds between each extraction check.
        total_checks: The total number of checks to perform. If None, it runs indefinitely.
        stop_event: A `multiprocessing.Event` used to signal when to stop the worker.
    """
    logger.info(
        f"Starting extraction worker with frequency {frequency_ms}ms, total_checks: {total_checks or 'infinite'}"
    )

    # Create API clients
    terms_api_client = AlertTermsClient()
    alert_api_client = AlertTextClient()

    check_count = 0
    frequency_seconds = frequency_ms / 1000.0

    try:
        while not stop_event.is_set():
            # Check if we've reached the total number of checks
            if total_checks is not None and check_count >= total_checks:
                logger.info(f"Completed {total_checks} checks. Stopping extraction.")
                break

            try:
                # Perform the extraction with the API clients
                log_entry = find_term_matches(alert_api_client, terms_api_client)
                logger.info(
                    f"Check {check_count + 1}/{total_checks or '∞'}: Found {len(log_entry.matches)} matches"
                )

                # Log the entire TermMatchList object as a JSON string
                if log_entry.matches:
                    logger.bind(extracted_alert=True).info(log_entry.model_dump_json())

            except Exception as e:
                logger.error(f"Error during extraction check: {e}")

            check_count += 1

            # Wait for the specified frequency or until stop event is set
            if stop_event.wait(timeout=frequency_seconds):
                break

    except Exception as e:
        logger.error(f"Unexpected error in extraction worker: {e}")
    finally:
        logger.info(f"Extraction worker stopped after {check_count} checks")
