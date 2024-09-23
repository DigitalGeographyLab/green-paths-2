""" conftest.py is a file that is used to configure the pytest test runner. """

import os
from pathlib import Path
import pytest
import logging
import pytest
import sqlite3
import logging

from ..src.config import GP2_DB_TEST_PATH, TEST_OUTPUT_RESULTS_DIR_PATH


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
    return "test_invalid_user_config.yml"


# @pytest.fixture(scope="session")
# def setup_test_db():
#     # Define the path for the test database
#     db_path = GP2_DB_TEST_PATH

#     # Create the database before tests
#     if os.path.exists(db_path):
#         os.remove(db_path)  # Remove if it already exists
#     conn = sqlite3.connect(db_path)
#     conn.execute("VACUUM;")  # Initialize the database
#     conn.close()


@pytest.fixture(scope="session", autouse=True)
def cleanup_db_before_and_after_tests():
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

    cursor.close()
    conn.close()

    # The yield statement marks the point where pytest will run the tests
    yield

    conn = sqlite3.connect(GP2_DB_TEST_PATH)
    cursor = conn.cursor()

    # # Delete all data from each table after all tests
    # for table in tables:
    #     cursor.execute(f"DELETE FROM {table[0]};")
    #     conn.commit()

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
