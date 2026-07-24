"""Structured logger and in-memory log buffer for Travel Buddy troubleshooting."""

import logging
from datetime import datetime


class MemoryLogHandler(logging.Handler):
    """Custom log handler storing formatted log records in memory for Streamlit display."""

    def __init__(self):
        super().__init__()
        self.log_records = []

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_records.append(msg)
        except Exception:
            self.handleError(record)

    def get_logs(self) -> str:
        return "\n".join(self.log_records)

    def clear(self):
        self.log_records.clear()


_memory_handler = MemoryLogHandler()
_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%H:%M:%S"
)
_memory_handler.setFormatter(_formatter)

# Configure parent logger for travel_buddy package
_root_tb_logger = logging.getLogger("travel_buddy")
_root_tb_logger.setLevel(logging.DEBUG)
if _memory_handler not in _root_tb_logger.handlers:
    _root_tb_logger.addHandler(_memory_handler)


def get_logger(module_name: str) -> logging.Logger:
    """Get a configured logger for a given Travel Buddy module."""
    logger = logging.getLogger(f"travel_buddy.{module_name}")
    logger.setLevel(logging.DEBUG)
    if _memory_handler not in logger.handlers:
        logger.addHandler(_memory_handler)
    return logger


def get_session_logs() -> str:
    """Retrieve all logged messages for the current session."""
    logs = _memory_handler.get_logs()
    if not logs:
        return "[SYSTEM LOG]: Session started. Agent logs will appear here during execution."
    return logs


def clear_session_logs():
    """Clear in-memory log buffer."""
    _memory_handler.clear()
