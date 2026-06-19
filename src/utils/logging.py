"""Unified logging utilities.

All modules should use `logger = get_logger(__name__)` instead of print().
"""

import logging
import sys

_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized: bool = False


def setup_logging(
    level: int = logging.INFO,
    fmt: str | None = None,
    date_fmt: str | None = None,
) -> None:
    """Configure the root logger once for the entire application.

    Args:
        level: Logging level (e.g. logging.DEBUG, logging.INFO).
        fmt: Log message format string.
        date_fmt: Date format string.
    """
    global _initialized
    if _initialized:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt=fmt or _DEFAULT_FORMAT,
            datefmt=date_fmt or _DEFAULT_DATE_FORMAT,
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name, initializing the root logger if needed.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)
