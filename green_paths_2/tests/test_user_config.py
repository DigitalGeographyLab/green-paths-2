""" test user config ans parser """

import pytest
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.green_paths_exceptions import (
    ConfigError,
    ConfigDataError,
)
import pytest
from unittest.mock import patch

from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.PURPLE.value)

# TODO: tee testit 2 kpl valid/invalid yaml
# TODO: vois tehä eri virheitä per eri validointi ja sit assettaa niihin


# def test_user_config_parser(user_config_path):
#     """Test user config parser."""
#     user_config = UserConfig()
#     user_config.parse_config(user_config_path)

#     assert user_config.project_crs == 3879
#     assert (
#         user_config.osm_network.osm_pbf_file_path == "tests/data/lintsi_pieni.osm.pbf"
#     )
#     assert user_config.osm_network.original_crs == 4326

#     # assert user_config.osm_network.network_type == "walking"
#     # assert user_config.osm_network.network_buffer_unit == "meters"
#     # assert user_config.osm_network.network_buffer_rounding == 0


# def test_user_config_parser_invalid_yaml(invalid_user_config_path):
#     """Test user config parser with invalid yaml."""
#     with pytest.raises(ConfigError):
#         user_config = UserConfig()
#         user_config.parse_config(invalid_user_config_path)


# def test_user_config_parser_invalid_data():
#     """ Test user config parser with invalid data. """
#     with pytest.raises(ConfigDataError):
#         user_config = UserConfig()
#         user_config.parse_config("tests/data/invalid_config_data.yaml")

# TODO: fix and create tests...


@pytest.mark.parametrize(
    "config,expected_error",
    [
        # Example of a missing data name
        (
            {
                "data_sources": [
                    {"filepath": "path/to/data.gpkg", "data_type": "vector"}
                ]
            },
            ConfigDataError,
        ),
        # Example of a valid data source with all required fields
        (
            {
                "data_sources": [
                    {
                        "name": "valid_data",
                        "filepath": "path/to/data.gpkg",
                        "data_type": "vector",
                        "data_column": "column1",
                        "raster_cell_resolution": 10,
                    }
                ]
            },
            None,
        ),
        # Example of an invalid CRS
        ({"project_crs": "invalid_crs"}, ConfigError),
        # Example of a valid CRS
        ({"project_crs": "EPSG:3857"}, None),
        # Add more examples here
    ],
)
def test_configuration_validation(config, expected_error):
    # Assuming UserConfig's methods can be independently called, you might need to use 'mocker' from pytest-mock to mock file reading or any external dependencies.
    user_config = UserConfig("path/to/config.yml")
    if expected_error:
        with pytest.raises(expected_error):
            user_config.validate_config(config)
    else:
        # No error expected, validate_config should complete without raising an exception
        assert user_config.validate_config(config) is None
