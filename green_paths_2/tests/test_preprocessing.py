import pytest
from invoke import Context
import os
import sqlite3

CONFIG_DIR = "green_paths_2/tests/configs"
CONFIG_FILE = "aqi_green_mtm_precalc_nogeom_test_config.yml"
TEST_DB_PATH = "green_paths_2/tests/database/gp2_testing.db"

# TODO: test ->
# - test one-to-one -> with geometries
# - many-to-many
# see db results
# see output files


def test_preprocessing():
    # Initialize an Invoke context
    ctx = Context()

    # Define the full path to the config file
    config_path = os.path.join(CONFIG_DIR, CONFIG_FILE)

    # Run the preprocessing command with the test config
    result = ctx.run(f"inv gp2 -a '-c {config_path} preprocessing'")

    # Assert the result or validate the output
    assert result.ok

    # Verify the results in the SQLite database
    # conn = sqlite3.connect(TEST_DB_PATH)
    # cursor = conn.cursor()
    # cursor.execute("SELECT COUNT(*) FROM preprocessed_data")
    # count = cursor.fetchone()[0]
    # assert count > 0  # Adjust this assertion based on expected data
    # conn.close()
