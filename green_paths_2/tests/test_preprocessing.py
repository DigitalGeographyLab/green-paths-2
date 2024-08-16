# NOTE - all test should be made better!!! excuse: time
# NOTE - main goal for this test is to run preprocessing pipeline and check that the correct values are passed to db table segment_store

import os

import pytest

from ..tests.db_checker_helper import (
    check_data_types,
    check_geospatial_data,
    check_row_count,
    get_column_value_by_osm_id,
)
from ..src.config import GEOMETRY_KEY, PREPROCESSING_PIPELINE_NAME, SEGMENT_STORE_TABLE

from ..src.pipeline_controller import (
    handle_pipelines,
)


# skip test
# @pytest.mark.skip(reason="testing  so skipping")
def test_preprocessing(conn, config_dir, valid_user_config):

    config_path = os.path.join(config_dir, valid_user_config)

    # run the preprocessing pipeline
    handle_pipelines(
        pipeline_name=PREPROCESSING_PIPELINE_NAME,
        config_path=config_path,
    )

    columns_to_check = [
        ("gvi", float),
        ("aqi", float),
        ("gvi_normalized", float),
        ("aqi_normalized", float),
        ("osm_id", int),
        ("length", float),
    ]

    for column, expected_type in columns_to_check:
        assert check_data_types(conn, SEGMENT_STORE_TABLE, column, expected_type)

    # osm_id of the first row of select *
    first_row_osm_id = -1000000166683
    aqi = get_column_value_by_osm_id(conn, SEGMENT_STORE_TABLE, first_row_osm_id, "aqi")
    aqi_normalized = get_column_value_by_osm_id(
        conn, SEGMENT_STORE_TABLE, first_row_osm_id, "aqi_normalized"
    )

    # osm_id from second row
    second_row_osm_id = -1000000166679

    gvi = get_column_value_by_osm_id(
        conn, SEGMENT_STORE_TABLE, second_row_osm_id, "gvi"
    )
    gvi_normalized = get_column_value_by_osm_id(
        conn, SEGMENT_STORE_TABLE, second_row_osm_id, "gvi_normalized"
    )

    # check aqi from first row
    assert aqi_normalized > 0 and aqi_normalized < 1
    assert aqi > aqi_normalized
    assert aqi > 1
    assert aqi == 2.094
    assert aqi_normalized == 0.273
    # no gvi in first row, check that
    no_gvi_in_first_row = get_column_value_by_osm_id(
        conn, SEGMENT_STORE_TABLE, first_row_osm_id, "gvi"
    )
    assert no_gvi_in_first_row == None

    # check gvi from second row
    assert gvi > gvi_normalized
    assert gvi_normalized > -1 and gvi_normalized < 0
    assert gvi == 0.453
    # good exposure so should be negative normalized value
    assert gvi_normalized < 0
    assert gvi_normalized == -0.005

    assert check_geospatial_data(conn, SEGMENT_STORE_TABLE, GEOMETRY_KEY)

    assert check_row_count(conn, SEGMENT_STORE_TABLE, expected_count=49676)
