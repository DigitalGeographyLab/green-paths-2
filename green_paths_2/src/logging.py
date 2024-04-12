import os
import sys
import logging
from enum import Enum

# define ANSI color codes
COLORS = {
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "RED": "\033[91m",
    "PURPLE": "\033[95m",
    "CYAN": "\033[96m",
    "ORANGE": "\033[33m",
    "RESET": "\033[0m",
}


class LoggerColors(Enum):
    """Enum for logger colors."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    BLUE = "BLUE"
    RED = "RED"
    PURPLE = "PURPLE"
    CYAN = "CYAN"
    ORANGE = "ORANGE"
    RESET = "RESET"


class CustomFormatter(logging.Formatter):
    def __init__(self, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color

    def format(self, record):
        record.msg = (
            f"{COLORS.get(self.color, COLORS['RESET'])}{record.msg}{COLORS['RESET']}"
        )
        return super().format(record)


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False otherwise.
    """
    plat = sys.platform
    supported_platform = plat != "win32" or "ANSICON" in os.environ
    # Windows does not support ANSI escape characters in cmd by default, so check for ANSICON
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported_platform and is_a_tty


def setup_logger(name, color="RESET"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    if supports_color():
        formatter = CustomFormatter(
            color, "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    ch.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(ch)

    return logger
