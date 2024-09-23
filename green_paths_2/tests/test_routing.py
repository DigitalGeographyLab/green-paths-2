import os
import pytest

from ..src.config import (
    ROUTING_PIPELINE_NAME,
    ROUTING_RESULTS_TABLE,
    TRAVEL_TIMES_TABLE,
)
from ..src.pipeline_controller import handle_pipelines
from ..tests.db_checker_helper import (
    check_data_types,
    check_row_count,
    execute_query,
    get_column_value_by_osm_id,
)


# the one with chunking treshold will trigger chunking & threading
# and the other one will not
# so test both
@pytest.mark.parametrize(
    "user_config",
    [
        "aqi_green_mtm_precalc_nogeom_test_config_with_chunking.yml",
        "aqi_green_mtm_precalc_nogeom_test_config.yml",
    ],
)
def test_routing(conn, config_dir, user_config):

    config_path = os.path.join(config_dir, user_config)

    # run the preprocessing pipeline
    handle_pipelines(
        pipeline_name=ROUTING_PIPELINE_NAME,
        config_path=config_path,
    )

    # ROUTING_RESULTS_TABLE

    columns_to_check = [
        ("from_id", str),
        ("to_id", str),
        ("osm_ids", str),
    ]

    for column, expected_type in columns_to_check:
        assert check_data_types(conn, ROUTING_RESULTS_TABLE, column, expected_type)

    # get all rows and expect 40k because of the test config
    assert 40_000 == check_row_count(conn, ROUTING_RESULTS_TABLE)

    # get all with non empty osm_ids
    routing_results_with_osmids = execute_query(
        conn,
        query="select count(*) from routing_results where osm_ids IS NOT NULL AND osm_ids != '[NaN]' AND osm_ids != '[]' AND osm_ids != 'NaN';",
    )
    # result is a list of tuples so first element of the first tuple is the count
    assert routing_results_with_osmids[0][0] == 6905

    # get specific row and assert osm_ids

    specific_routing_result_row = execute_query(
        conn,
        query="select * from routing_results where from_id == 247.0 and to_id == 287.0;",
    )

    osm_ids_from_specific_row = specific_routing_result_row[0][3]

    osm_ids_from_specific_row_list = osm_ids_from_specific_row.split(",")

    white_spaces_removed_list = [
        element.replace(" ", "") for element in osm_ids_from_specific_row_list
    ]

    assert len(osm_ids_from_specific_row_list) == 28

    assert "-91414" in white_spaces_removed_list
    assert "-2389" in white_spaces_removed_list
    assert "-14704" in white_spaces_removed_list

    # TRAVEL_TIMES_TABLE

    columns_to_check = [("osm_id", int), ("travel_time", float)]

    for column, expected_type in columns_to_check:
        assert check_data_types(conn, TRAVEL_TIMES_TABLE, column, expected_type)

    # check random osm_id 1 travel time is correct type and value
    random_osm_id_1 = "-160964"
    travel_time_random_1 = get_column_value_by_osm_id(
        conn, TRAVEL_TIMES_TABLE, random_osm_id_1, "travel_time"
    )
    assert isinstance(travel_time_random_1, float) and travel_time_random_1 == 14.0

    # check random osm_id 2 travel time is correct type and value
    random_osm_id_2 = "-2389"
    travel_time_random_2 = get_column_value_by_osm_id(
        conn, TRAVEL_TIMES_TABLE, random_osm_id_2, "travel_time"
    )
    assert isinstance(travel_time_random_2, float) and travel_time_random_2 == 20.0
