""" conftest.py is a file that is used to configure the pytest test runner. """

# simple tests are in place, should do more comprehensive testing!

# Testing TODO:
# - test one-to-one -> with geometries
# - many-to-many
# see output files


import os
from pathlib import Path
import sys
import pytest
import logging
import pytest
import sqlite3
import logging

from ..src.config import GP2_DB_TEST_PATH, TEST_OUTPUT_RESULTS_DIR_PATH


# # # cleanup the database before and after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_db_before_and_after_tests():

    # TODO ROOPE TODO - remove comments after the tests are done
    # Connect to the database
    conn = sqlite3.connect(GP2_DB_TEST_PATH)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Delete all data from each table before the first test
    for table in tables:
        cursor.execute(f"DELETE FROM {table[0]};")
        conn.commit()

    # The yield statement marks the point where pytest will run the tests
    yield

    # TODO ROOPE TODO - remove comments after the tests are done
    # Delete all data from each table after all tests
    for table in tables:
        cursor.execute(f"DELETE FROM {table[0]};")
        conn.commit()

    # Close the connection
    cursor.close()
    conn.close()


# delete all test output files after tests
@pytest.fixture(scope="function", autouse=True)
def delete_output_files():
    yield
    test_output_dir = Path(TEST_OUTPUT_RESULTS_DIR_PATH)

    # Check if the directory exists
    if test_output_dir.exists() and test_output_dir.is_dir():
        for file in test_output_dir.iterdir():
            try:
                if file.is_file() and file.name != ".gitkeep":
                    file.unlink()
            except Exception as e:
                print(
                    f"Failed to delete {file}: {e} in the delete_output_files fixture"
                )


@pytest.fixture(autouse=True)
def disable_logging():
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def conn():
    yield sqlite3.connect(GP2_DB_TEST_PATH)


@pytest.fixture(scope="session", autouse=True)
def set_test_env_var():
    os.environ["ENV"] = "TEST"
    yield
    del os.environ["ENV"]


@pytest.fixture(autouse=True)
def configure_logging():
    logging.basicConfig(level=logging.DEBUG)
    LOG = logging.getLogger(__name__)


@pytest.fixture
def config_dir():
    return "green_paths_2/tests/configs"


@pytest.fixture
def valid_user_config():
    return "aqi_green_mtm_precalc_nogeom_test_config.yml"


@pytest.fixture
def invalid_user_config():
    return "test_invalid_user_config.yaml"


# from ..src.preprocessing.user_config_parser import UserConfig
# from ..src.logging import setup_logger, LoggerColors
# from ..src.preprocessing.osm_network_handler import OsmNetworkHandler
# from ..src.green_paths_exceptions import ConfigDataError

# LOG = setup_logger(__name__, LoggerColors.YELLOW.value)


# TEST_CONFIG_PATH = "tests/data/test_valid_user_config.yaml"
# TEST_INVALID_CONFIG_PATH = "tests/data/test_invalid_user_config.yaml"


# @pytest.fixture
# def user_config_path():
#     yield UserConfig()._load_config(TEST_CONFIG_PATH)


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
