# """ test user config ans parser """

# import pytest
# from ..src.preprocessing.user_config_parser import UserConfig
# from ..src.green_paths_exceptions import (
#     ConfigError,
#     ConfigDataError,
# )
# import pytest
# from unittest.mock import patch

# from ..src.logging import setup_logger, LoggerColors

# LOG = setup_logger(__name__, LoggerColors.PURPLE.value)

# import pytest

# import os
# import sys
# import pytest

# sys.path.insert(
#     0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
# )


# def test_valid_config():
#     config_path = "tests/config_files/valid_config.yml"
#     config = UserConfig(config_path)
#     config.parse_config()

#     assert config.project_crs == 3879
#     assert config.osm_network["osm_pbf_file_path"] == "path/to/user_network.osm.pbf"


# def test_missing_fields():
#     config_path = "tests/config_files/missing_fields.yml"
#     with pytest.raises(
#         ConfigError
#     ):  # Adjust the Exception type based on what you expect
#         config = UserConfig(config_path)
#         config.parse_config()


# def test_invalid_types():
#     config_path = "tests/config_files/invalid_types.yml"
#     with pytest.raises(ConfigError):  # Adjust as needed
#         config = UserConfig(config_path)
#         config.parse_config()
