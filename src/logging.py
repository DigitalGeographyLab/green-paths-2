import logging


# def setup_logger(name: str = "noname_logger", level=logging.INFO):
#     """
#     Set up a basic logger.

#     :param level: The logging level, e.g., logging.DEBUG, logging.INFO.
#     """
#     # create logger for the calling module
#     logger = logging.getLogger(name)
#     # set level
#     logger.setLevel(level)
#     # create console handler
#     console_handler = logging.StreamHandler()
#     # set format for the logger
#     formatter = logging.Formatter(
#         "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#     )
#     console_handler.setFormatter(formatter)
#     # add the handler to the logger
#     logger.addHandler(console_handler)
#     return logger


# import logging
# import os
# import sys


# class CustomFormatter(logging.Formatter):
#     """Custom formatter to add colors to logging output based on module name"""

#     COLORS = {
#         "WARNING": "\033[93m",  # Yellow
#         "INFO": "\033[94m",  # Blue
#         "DEBUG": "\033[92m",  # Green
#         "CRITICAL": "\033[91m",  # Red
#         "ERROR": "\033[91m",  # Red
#         "RESET": "\033[0m",  # Reset
#     }

#     # CUSTOM_COLORS = {
#     #     "TIME_LOG": "\033[95m",  # Purple
#     #     "CONFIG_INFO": "\033[96m",  # Cyan
#     # }

#     def format(self, record):
#         # Check if the module name is in the CUSTOM_COLORS, else use default colors
#         color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
#         # self.CUSTOM_COLORS.get(record.name,        )
#         record.msg = f"{color}{record.msg}{self.COLORS['RESET']}"
#         return super(CustomFormatter, self).format(record)

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


import logging


def setup_logger(name, color="RESET"):
    """Set up and return a logger with a custom formatter based on color"""
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to see all log levels

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)  # Set handler to DEBUG to pass all log levels

    # create formatter with color
    formatter = CustomFormatter(
        color, "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger, check if it already has handlers
    if not logger.handlers:
        logger.addHandler(ch)

    return logger
