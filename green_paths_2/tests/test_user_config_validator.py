import os

import pytest

from ..src.green_paths_exceptions import ConfigError
from ..src.preprocessing.user_config_parser import UserConfig

USER_CONFIG_PATH = "green_paths_2/user/config.yaml"


def test_validator_valid_config(config_dir, valid_user_config):
    config_path = os.path.join(config_dir, valid_user_config)
    user_config = UserConfig(config_path).parse_config()

    assert user_config is not None
    assert user_config.data_source_names is not None
    assert user_config.errors == []


def test_validator_invalid_config(config_dir, invalid_user_config):
    config_path_of_invalid_yml = os.path.join(config_dir, invalid_user_config)

    # assert throwing ConfigError and capture the exception
    with pytest.raises(ConfigError) as excinfo:
        _ = UserConfig(config_path_of_invalid_yml).parse_config()

    # Assert that the error message is not empty
    assert excinfo.value.args[0]  # Check if the exception has a message

    # Split the error message by newlines to get individual error messages
    actual_errors = excinfo.value.args[0].split("\n\n")

    # The expected errors
    errors_that_should_be_thrown = [
        "Missing project group in user_config.yaml.",
        "Missing project group in user_config.yaml.",
        "Didn't find osm network pbf file with provided user confs. Path was None",
        "Invalid or missing filepath configuration. Path path/to/allPollutants_2023-12-15T04.nc not found.",
        "Invalid or missing ORIGINS path configuration in routing parameters.",
        "Invalid or missing DESTINATIONS path configuration in routing parameters.",
        "Routing Exposure parameter name not found in Preprocessing data sources. Check that the name matches with the data source name.",
        "Invalid cumulative ranges in analysing parameters. Should be list of float or integers.",
    ]

    # Assert that all expected errors are in the actual error message
    for error in errors_that_should_be_thrown:
        assert error in actual_errors
