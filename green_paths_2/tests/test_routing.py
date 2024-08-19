import os

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


def test_routing(conn, config_dir, valid_user_config):
    config_path = os.path.join(config_dir, valid_user_config)

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
    assert check_row_count(conn, ROUTING_RESULTS_TABLE, 40_000)

    # get all with non empty osm_ids
    routing_results_with_osmids = execute_query(
        conn,
        query="select count(*) from routing_results where osm_ids IS NOT NULL AND osm_ids != '[NaN]' AND osm_ids != '[]';",
    )
    # result is a list of tuples so first element of the first tuple is the count
    assert routing_results_with_osmids[0][0] == 6905

    # get specific row and assert osm_ids

    specific_routing_result_row = execute_query(
        conn,
        query="select * from routing_results where from_id == 247.0 and to_id == 287.0;",
    )

    osm_ids_from_specific_row = specific_routing_result_row[0][2]

    osm_ids_from_specific_row_list = osm_ids_from_specific_row.split(",")

    assert len(osm_ids_from_specific_row_list) == 28

    assert "-1000000091414" in osm_ids_from_specific_row
    assert "-1000000103298" in osm_ids_from_specific_row
    assert "-1000000160963" in osm_ids_from_specific_row
    assert "-1000000165357" not in osm_ids_from_specific_row

    # TRAVEL_TIMES_TABLE

    columns_to_check = [("osm_id", int), ("travel_time", float)]

    for column, expected_type in columns_to_check:
        assert check_data_types(conn, TRAVEL_TIMES_TABLE, column, expected_type)

    # check random osm_id 1 travel time is correct type and value
    random_osm_id_1 = -1000000166683
    travel_time_random_1 = get_column_value_by_osm_id(
        conn, TRAVEL_TIMES_TABLE, random_osm_id_1, "travel_time"
    )
    assert isinstance(travel_time_random_1, float) and travel_time_random_1 == 5.0

    # check random osm_id 2 travel time is correct type and value
    random_osm_id_2 = -1000000166675
    travel_time_random_2 = get_column_value_by_osm_id(
        conn, TRAVEL_TIMES_TABLE, random_osm_id_2, "travel_time"
    )
    assert isinstance(travel_time_random_2, float) and travel_time_random_2 == 59.0
