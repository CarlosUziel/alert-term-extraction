"""FastAPI application for alert term extraction."""

import multiprocessing
import time
from typing import Optional

from fastapi import FastAPI, HTTPException

from app.utils import extraction_worker
from config.logger import logger
from models.api import ExtractionRequest, ExtractionResponse

# Constants for process management
GRACEFUL_SHUTDOWN_TIMEOUT = 5  # seconds
FORCEFUL_TERMINATION_TIMEOUT = 2  # seconds

# Global variables to track the extraction process
extraction_process: Optional[multiprocessing.Process] = None
should_stop = multiprocessing.Event()

app = FastAPI(
    title="Alert Term Extraction API",
    description="API for starting and stopping alert term extraction processes",
    version="1.0.0",
)


@app.post(
    "/start-extraction", response_model=ExtractionResponse, tags=["Extraction Process"]
)
async def start_extraction(request: ExtractionRequest):
    """
    Start the alert term extraction process in the background.

    Validates that no other extraction process is currently running.
    Initializes and starts a new process for term extraction.

    Args:
        request: An `ExtractionRequest` containing:
            - `frequency_ms`: The interval in milliseconds for checking alerts (100-1000).
            - `total_checks` (optional): The total number of checks before stopping.
                                        If None, runs indefinitely.

    Returns:
        An `ExtractionResponse` with a success message and the process ID.

    Raises:
        HTTPException (400): If an extraction process is already running.
        HTTPException (500): If there is an internal error starting the process.
    """
    global extraction_process, should_stop

    # Check if extraction is already running
    if extraction_process is not None and extraction_process.is_alive():
        raise HTTPException(
            status_code=400,
            detail="Extraction process is already running. Stop it first before starting a new one.",
        )

    try:
        # Reset the stop event
        should_stop.clear()

        # Create and start the extraction process
        extraction_process = multiprocessing.Process(
            target=extraction_worker,
            args=(request.frequency_ms, request.total_checks, should_stop),
        )
        extraction_process.start()

        logger.info(f"Started extraction process with PID: {extraction_process.pid}")

        total_checks_msg = request.total_checks or "infinite"
        return ExtractionResponse(
            message=f"Extraction started with frequency {request.frequency_ms}ms and {total_checks_msg} checks",
            process_id=extraction_process.pid,
        )

    except Exception as e:
        logger.error(f"Failed to start extraction process: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start extraction: {str(e)}"
        )


@app.post(
    "/stop-extraction", response_model=ExtractionResponse, tags=["Extraction Process"]
)
async def stop_extraction():
    """
    Stop the currently running alert term extraction process.

    Signals the background process to stop gracefully. If it does not respond
    within a timeout, it will be forcefully terminated.

    Returns:
        An `ExtractionResponse` with a success message.

    Raises:
        HTTPException (400): If no extraction process is currently running.
        HTTPException (500): If there is an internal error stopping the process.
    """
    global extraction_process, should_stop

    # Check if extraction is running
    if extraction_process is None or not extraction_process.is_alive():
        raise HTTPException(
            status_code=400, detail="No extraction process is currently running."
        )

    try:
        # Signal the process to stop
        should_stop.set()

        # Wait for the process to finish gracefully (up to 5 seconds)
        extraction_process.join(timeout=GRACEFUL_SHUTDOWN_TIMEOUT)

        if extraction_process.is_alive():
            # Force terminate if it doesn't stop gracefully
            logger.warning("Extraction process didn't stop gracefully, terminating...")
            extraction_process.terminate()
            extraction_process.join(timeout=FORCEFUL_TERMINATION_TIMEOUT)

            if extraction_process.is_alive():
                # Kill if terminate doesn't work
                logger.error("Forcefully killing extraction process")
                extraction_process.kill()
                extraction_process.join()

        logger.info("Extraction process stopped successfully")
        extraction_process = None

        return ExtractionResponse(message="Extraction process stopped successfully")

    except Exception as e:
        logger.error(f"Failed to stop extraction process: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to stop extraction: {str(e)}"
        )


@app.get("/extraction-status", tags=["Extraction Process"])
async def get_extraction_status():
    """
    Get the current status of the alert term extraction process.

    Checks if the background process is alive and returns its status.

    Returns:
        A dictionary containing the status (`running` or `stopped`),
        the process ID (if running), and a descriptive message.
    """
    global extraction_process

    if extraction_process is None:
        return {
            "status": "stopped",
            "message": "No extraction process has been started",
        }

    is_alive = extraction_process.is_alive()

    return {
        "status": "running" if is_alive else "stopped",
        "process_id": extraction_process.pid if is_alive else None,
        "message": "Extraction is running"
        if is_alive
        else "Extraction process has stopped",
    }


@app.get("/health", tags=["Status"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}
