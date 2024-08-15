""" Validation module for user configuration. """

from .config import USER_CONFIG_PATH
from .green_paths_exceptions import ConfigError
from .preprocessing.user_config_parser import UserConfig
from .logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.YELLOW.value)
LOG_SUCCESS = setup_logger(f"{__name__}_success", LoggerColors.GREEN.value)
LOG_ERROR = setup_logger(f"{__name__}_error", LoggerColors.RED.value)


def validate_user_config(custom_config_path: str = None) -> bool | None:
    """
    Validate user configuration.
    Will fail on the first error found.
    """
    LOG.info("Starting validation for user configuration.")
    try:
        config_path = custom_config_path if custom_config_path else USER_CONFIG_PATH
        UserConfig(config_path).parse_config()
        LOG.info("VALIDATING...\n\n\n")
        LOG_SUCCESS.info("CONFIGURATION VALID.")
    except ConfigError as e:
        LOG.info("VALIDATING...\n\n\n")
        LOG_ERROR.error(f"USER CONFIGURATION INVALID")
        LOG_ERROR.error(f"FOUND ERROR: {str(e)}")
        return False
    LOG.info("Validation finished.")
    return True
