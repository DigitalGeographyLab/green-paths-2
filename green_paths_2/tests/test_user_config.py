""" test user config ans parser """

import pytest
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.preprocessing.preprocessing_exceptions import (
    ConfigError,
    ConfigDataError,
)
from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.PURPLE.value)

# TODO: tee testit 2 kpl valid/invalid yaml
# TODO: vois tehä eri virheitä per eri validointi ja sit assettaa niihin


def test_user_config_parser(user_config_path):
    """Test user config parser."""
    user_config = UserConfig()
    user_config.parse_config(user_config_path)

    assert user_config.project_crs == 3879
    assert (
        user_config.osm_network.osm_pbf_file_path == "tests/data/lintsi_pieni.osm.pbf"
    )
    assert user_config.osm_network.original_crs == 4326

    # assert user_config.osm_network.network_type == "walking"
    # assert user_config.osm_network.network_buffer_unit == "meters"
    # assert user_config.osm_network.network_buffer_rounding == 0


def test_user_config_parser_invalid_yaml(invalid_user_config_path):
    """Test user config parser with invalid yaml."""
    with pytest.raises(ConfigError):
        user_config = UserConfig()
        user_config.parse_config(invalid_user_config_path)


# def test_user_config_parser_invalid_data():
#     """ Test user config parser with invalid data. """
#     with pytest.raises(ConfigDataError):
#         user_config = UserConfig()
#         user_config.parse_config("tests/data/invalid_config_data.yaml")
