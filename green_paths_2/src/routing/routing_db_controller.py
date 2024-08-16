import json

from ...src.timer import time_logger
from ..config import (
    FROM_ID_KEY,
    OSM_ID_KEY,
    OSM_IDS_KEY,
    TO_ID_KEY,
    TRAVEL_TIME_KEY,
)

from ...src.database_controller import DatabaseController


def get_normalized_exposures_from_db(
    db_handler: DatabaseController, normalized_data_source_names: list[str]
) -> dict:
    normalized_exposures_dict = {}
    for normalized_column_name in normalized_data_source_names:
        # dict of osmid: normalized_value
        # get from db
        normalized_values = (
            db_handler.get_normalized_exposures_by_column_from_segment_table(
                normalized_column_name
            )
        )
        normalized_exposures_dict[normalized_column_name] = normalized_values

    # check if exposure data is found
    if not normalized_exposures_dict:
        raise ValueError(
            "Normalized exposure data not found from db for routing pipeline."
        )

    return normalized_exposures_dict


@time_logger
def format_routing_results(green_paths_route_results: list[dict]) -> dict:
    """
    Format routing results to be stored in the database.

    Parameters
    ----------
    green_paths_route_results : list[dict]
        List of routing results.

    Returns
    -------
    dict
        Formatted routing results.
    """
    return {
        f"{entry[FROM_ID_KEY]}_{entry[TO_ID_KEY]}": {
            FROM_ID_KEY: entry[FROM_ID_KEY],
            TO_ID_KEY: entry[TO_ID_KEY],
            # Convert list to JSON string
            OSM_IDS_KEY: json.dumps(entry[OSM_IDS_KEY]),
        }
        for entry in green_paths_route_results
    }


def format_travel_times(travel_times: dict) -> dict:
    """
    Format travel times to be stored in the database.

    Parameters
    ----------
    travel_times : dict
        Travel times.

    Returns
    -------
    dict
        Formatted travel times.
    """
    return {
        k: {OSM_ID_KEY: int(k), TRAVEL_TIME_KEY: v}
        for k, v in travel_times[0][1].items()
    }
