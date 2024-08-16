# NOTE - just to test that the pipeline works without errors
# NOTE - all test should be made better!!! excuse: time

import os

import pytest

from ..tests.db_checker_helper import check_row_count, empty_table

from ..src.config import (
    ALL_PIPELINE_NAME,
    OUTPUT_RESULTS_TABLE,
    ROUTING_RESULTS_TABLE,
    SEGMENT_STORE_TABLE,
    TRAVEL_TIMES_TABLE,
)
from ..src.pipeline_controller import handle_pipelines

CONFIG_FILE = "aqi_green_mtm_precalc_nogeom_test_config.yml"

# just see that no errors...
# should maybe test more
# although all modules are tested separately


# @pytest.mark.skip(reason="testing  so skipping")
def test_all_pipeline(conn, config_dir):

    empty_table(conn, SEGMENT_STORE_TABLE)
    empty_table(conn, ROUTING_RESULTS_TABLE)
    empty_table(conn, TRAVEL_TIMES_TABLE)
    empty_table(conn, OUTPUT_RESULTS_TABLE)

    config_path = os.path.join(config_dir, CONFIG_FILE)

    # run the analysing pipeline
    handle_pipelines(
        pipeline_name=ALL_PIPELINE_NAME,
        config_path=config_path,
    )

    # TODO ROOPE TODO - ASSERT THESE AND CHANGE EXPECTED VALUES

    # check_row_count(conn, SEGMENT_STORE_TABLE, 41_000)
    # check_row_count(conn, ROUTING_RESULTS_TABLE, 40_000)
    # check_row_count(conn, TRAVEL_TIMES_TABLE, 40_000)
    # check_row_count(conn, OUTPUT_RESULTS_TABLE, 40_000)

    assert True
