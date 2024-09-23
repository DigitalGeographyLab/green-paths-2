# Use name "z" for ordering to last test

import os
from .db_checker_helper import check_row_count, empty_table

from ..src.config import (
    ALL_PIPELINE_NAME,
    OUTPUT_RESULTS_TABLE,
    ROUTING_RESULTS_TABLE,
    SEGMENT_STORE_TABLE,
    TEST_OUTPUT_RESULTS_DIR_PATH,
    TRAVEL_TIMES_TABLE,
)
from ..src.pipeline_controller import handle_pipelines


def test_all_pipeline_no_geom(conn, config_dir):

    CONFIG_FILE = "aqi_green_mtm_precalc_nogeom_test_config.yml"

    # empty previous datas from db
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

    assert 49_692 == check_row_count(conn, SEGMENT_STORE_TABLE)
    assert 40_000 == check_row_count(conn, ROUTING_RESULTS_TABLE)
    assert 49_484 == check_row_count(conn, TRAVEL_TIMES_TABLE)
    assert 29_505 == check_row_count(conn, OUTPUT_RESULTS_TABLE)

    files_in_output_dir = os.listdir(TEST_OUTPUT_RESULTS_DIR_PATH)
    assert any(
        f.endswith(".csv") and "test_aqi_green_mtm_precalc_nogeom" in f
        for f in files_in_output_dir
    ), f"No csv file found in {TEST_OUTPUT_RESULTS_DIR_PATH}"


# TEST WITH GEOM TRUE AND PRECALC FALSE


def test_all_pipeline_with_geom(conn, config_dir):

    CONFIG_FILE = "green_mtm_noprecalc_has_geom_test_config.yml"

    # empty previous datas from db
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

    assert 49_692 == check_row_count(conn, SEGMENT_STORE_TABLE)
    assert 121 == check_row_count(conn, ROUTING_RESULTS_TABLE)
    assert 121 == check_row_count(conn, OUTPUT_RESULTS_TABLE)

    files_in_output_dir = os.listdir(TEST_OUTPUT_RESULTS_DIR_PATH)
    assert any(
        f.endswith(".gpkg") and "test_green_mtm_noprecalc_has_geom" in f
        for f in files_in_output_dir
    ), f"No gpkg file found in {TEST_OUTPUT_RESULTS_DIR_PATH}"
