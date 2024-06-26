""" conftest.py is a file that is used to configure the pytest test runner. """

import pytest

from ..src.preprocessing.user_config_parser import UserConfig
from ..src.logging import setup_logger, LoggerColors
from ..src.preprocessing.osm_network_handler import OsmNetworkHandler
from ..src.green_paths_exceptions import ConfigDataError

LOG = setup_logger(__name__, LoggerColors.YELLOW.value)


TEST_CONFIG_PATH = "tests/data/test_valid_user_config.yaml"
TEST_INVALID_CONFIG_PATH = "tests/data/test_invalid_user_config.yaml"


@pytest.fixture
def user_config_path():
    yield UserConfig()._load_config(TEST_CONFIG_PATH)


# @pytest.fixture
# def invalid_user_config_path():
#     yield UserConfig()._load_config(TEST_INVALID_CONFIG_PATH)


# @pytest.fixture
# def osm_network_handler(user_config):
#     return OsmNetworkHandler(osm_pbf_file=user_config.osm_network.osm_pbf_file_path)


# @pytest.fixture
# def osm_network_gdf(user_config):
#     return process_osm_network(user_config)


# what is this?
# @pytest.fixture
# def cli_runner():
#     return CliRunner()
