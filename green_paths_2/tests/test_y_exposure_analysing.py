import os
from ..src.config import (
    ANALYSING_PIPELINE_NAME,
    OUTPUT_RESULTS_TABLE,
    TEST_OUTPUT_RESULTS_DIR_PATH,
)
from ..src.pipeline_controller import handle_pipelines
from .db_checker_helper import check_data_types, execute_query


CONFIG_FILE = "aqi_green_mtm_precalc_nogeom_test_config.yml"


def test_routing(conn, config_dir):
    config_path = os.path.join(config_dir, CONFIG_FILE)

    # run the analysing pipeline
    handle_pipelines(
        pipeline_name=ANALYSING_PIPELINE_NAME,
        config_path=config_path,
    )

    columns_to_check = [
        ("from_id", int),
        ("gvi_time_weighted_path_exposure_avg", str),
        ("length", str),
        ("aqi_time_weighted_path_exposure_avg", str),
        ("aqi_time_weighted_path_exposure_sum", str),
        ("to_id", int),
        ("gvi_min_exposure", str),
        ("aqi_max_exposure", str),
        ("gvi_time_weighted_path_exposure_sum", str),
        ("aqi_min_exposure", str),
        ("gvi_max_exposure", str),
        ("travel_time", str),
    ]

    for column, expected_type in columns_to_check:
        assert check_data_types(conn, OUTPUT_RESULTS_TABLE, column, expected_type)

    results_with_gvi_max_exposure = execute_query(
        conn,
        query="select count(*) from output_results where gvi_max_exposure is not null;",
    )

    assert results_with_gvi_max_exposure[0][0] == 6665

    results_with_aqi_avg_exposure = execute_query(
        conn,
        query="select count(*) from output_results where aqi_time_weighted_path_exposure_avg is not null;",
    )

    assert results_with_aqi_avg_exposure[0][0] == 6905

    selected_result_path_values = execute_query(
        conn,
        query="select length, aqi_time_weighted_path_exposure_avg, gvi_time_weighted_path_exposure_avg, travel_time from output_results where aqi_time_weighted_path_exposure_sum and to_id = 285.0 and from_id = 247.0;",
    )

    # length
    assert selected_result_path_values[0][0] == "16.54"

    # aqi_time_weighted_path_exposure_avg
    assert selected_result_path_values[0][1] == "2.22"

    # gvi_time_weighted_path_exposure_avg
    # this row has no gvi so it should be null
    assert not selected_result_path_values[0][2]

    # travel_time
    assert selected_result_path_values[0][3] == "11.0"

    # assrt that output file is created to path: green_paths_2/tests/outputs has a csv file in it
    files_in_output_dir = os.listdir(TEST_OUTPUT_RESULTS_DIR_PATH)
    assert any(
        f.endswith(".csv") and "test_aqi_green_mtm_precalc_nogeom" in f
        for f in files_in_output_dir
    ), f"No csv file found in {TEST_OUTPUT_RESULTS_DIR_PATH}"
