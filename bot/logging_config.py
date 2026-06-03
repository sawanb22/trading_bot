"""
bot/logging_config.py
─────────────────────
Singleton-style logger configuration.
- Appends all records to bot_execution.log (file never truncated)
- Console gets WARNING+ only (keeps CLI clean for rich output)
- Guards against duplicate handlers (safe to call multiple times)
- Log format: [YYYY-MM-DD HH:MM:SS] [LEVEL] — message
"""

import logging
import os
from pathlib import Path

_LOGGER_NAME = "trading_bot"
_LOG_FILE = Path(__file__).parent.parent / "bot_execution.log"


def get_logger() -> logging.Logger:
    """
    Return the singleton logger for the trading bot.
    Configures handlers only once — subsequent calls return the same logger.
    """
    logger = logging.getLogger(_LOGGER_NAME)

    # Guard: if handlers already attached, return as-is (prevents duplication)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # Capture everything at logger level

    # ── File Handler ────────────────────────────────────────────────────────
    # Writes DEBUG and above to bot_execution.log (append mode)
    file_handler = logging.FileHandler(_LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-8s] — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # ── Console Handler ──────────────────────────────────────────────────────
    # Only WARNING+ reaches the terminal — rich handles the UI, not logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter(
        fmt="[%(levelname)s] %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.debug("Logger initialised. Log file: %s", _LOG_FILE)
    return logger
