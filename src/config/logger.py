import sys
from pathlib import Path

from loguru import logger

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define the directory for log files
LOG_DIR = BASE_DIR / ".logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Define paths for different log files
GENERAL_LOG_FILE = LOG_DIR / "general.log"
EXTRACTED_ALERTS_LOG_FILE = LOG_DIR / "extracted_alerts.jsonl"

# Remove default logger to configure custom ones
logger.remove()

# Configure logger for general application logs (console and file)
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
logger.add(
    sys.stdout,
    level="INFO",
    format=log_format,
    filter=lambda record: "extracted_alert" not in record["extra"],
)
logger.add(
    GENERAL_LOG_FILE,
    rotation="10 MB",
    retention="10 days",
    level="INFO",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    filter=lambda record: "extracted_alert" not in record["extra"],
)

# Configure a separate logger for extracted alerts (JSONL format)
logger.add(
    EXTRACTED_ALERTS_LOG_FILE,
    level="INFO",
    encoding="utf-8",
    enqueue=True,
    backtrace=False,
    diagnose=False,
    format="{message}",
    filter=lambda record: "extracted_alert" in record["extra"],
    serialize=False,  # We are logging pre-formatted JSON
)
