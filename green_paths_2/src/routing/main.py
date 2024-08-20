""" Routing pipeline for Green Paths 2. """

# WE NEED TO RUN _set_environment_and_import_r5py()
# WHICH SETS ENVIRONMENT VARIABLES AND IMPORTS GREEN PATHS 2 PATCH VERSION OF R5PY
# LIKE THIS BEFORE OTHER IMPORTS DUE TO NEED FOR --r5-classpath ARGUMENT BEFORE R5PY IMPORTS
# IT IS DIRTY, AND THERE MIGHT BE A BETTER WAY TO DO THIS


import numpy as np
from ...src.database_controller import DatabaseController
from ...src.routing.routing_db_controller import (
    format_routing_results,
    format_travel_times,
    get_normalized_exposures_from_db,
)
from ..config import (
    CHUNK_SIZE_FOR_ROUTING_RESULTS,
    DB_ROUTING_RESULTS_COLUMNS,
    DB_TRAVEL_TIMES_COLUMNS,
    ROUTING_CHUNKING_THRESHOLD,
    ROUTING_RESULTS_TABLE,
    TRAVEL_TIMES_TABLE,
)

from ..routing.routing_utilities import (
    init_origin_destinations_from_files,
    set_environment_and_import_r5py,
)

# this code is ran before any other codes in routing module
if not set_environment_and_import_r5py():
    raise R5pyError(
        "Failed to set environment variables and import r5py. Exiting routing!"
    )


from ..green_paths_exceptions import PipeLineRuntimeError, R5pyError
from ..logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.GREEN.value)
from ..timer import time_logger

from ..data_utilities import (
    convert_gdf_to_dict,
)
from ..preprocessing.user_config_parser import UserConfig
from ..preprocessing.user_data_handler import UserDataHandler
from ..routing.router_controller import route_green_paths_2_paths
from ..routing.routing_utilities import (
    get_normalized_data_source_names,
    validate_segmented_osm_network_path,
)


def chunk_data(data, chunk_size):
    num_chunks = len(data) // chunk_size + (1 if len(data) % chunk_size > 0 else 0)
    chunks = np.array_split(data, num_chunks)
    print(f"Created {len(chunks)} chunks.")
    return chunks


def process_and_store_results(db_handler, route_data=None, travel_times=None):
    """Convert, format, and store routing results and travel times in the database."""
    if route_data is not None:
        route_data_dict = convert_gdf_to_dict(route_data, orient="records")
        formatted_routing_results = format_routing_results(route_data_dict)
        db_handler.add_many_dict(ROUTING_RESULTS_TABLE, formatted_routing_results)
    if travel_times is not None:
        formatted_travel_times = format_travel_times(travel_times)
        db_handler.add_many_dict(TRAVEL_TIMES_TABLE, formatted_travel_times)


@time_logger
def routing_pipeline(
    data_handler: UserDataHandler,
    user_config: UserConfig,
):
    """
    Run the routing pipeline.

    Parameters:
    ----------
    data_handler : UserDataHandler
        The UserDataHandler object.
    user_config : UserConfig
        The UserConfig object.

    Returns:
    ----------
    gpd.GeoDataFrame
        The routing results as a GeoDataFrame.
    dict
        The actual travel times as a dictionary.

    Raises:
    ----------
    PipeLineRuntimeError
        If the routing pipeline fails.
    """

    LOG.info("\n\n\nStarting routing pipeline\n\n\n")
    try:
        # validate segmented osm network path
        osm_segmented_network_path = validate_segmented_osm_network_path(
            user_config.osm_network.osm_pbf_file_path
        )

        # get data source names and create normalized data source names
        data_source_names = data_handler.get_data_source_names()
        normalized_data_source_names = get_normalized_data_source_names(
            data_source_names
        )

        db_handler = DatabaseController()

        # get normalized exposure values from db
        normalized_exposures_dict = get_normalized_exposures_from_db(
            db_handler=db_handler,
            normalized_data_source_names=normalized_data_source_names,
        )

        # handle OD pairs
        origins, destinations = init_origin_destinations_from_files(
            user_config.routing, user_config.project.project_crs
        )

        # use r5py to route
        # TODO: split network creation and routing and create functions for API
        green_paths_route_results, actual_travel_times = route_green_paths_2_paths(
            osm_segmented_network_path,
            normalized_exposures_dict,
            origins,
            destinations,
            user_config,
        )

        db_handler.create_table_from_params(
            ROUTING_RESULTS_TABLE, DB_ROUTING_RESULTS_COLUMNS
        )
        db_handler.create_table_from_params(TRAVEL_TIMES_TABLE, DB_TRAVEL_TIMES_COLUMNS)

        # get route rows count from routing results
        route_rows_count = green_paths_route_results.shape[0]

        # chunk routing data if route_rows_count is greater than threshold
        if route_rows_count > ROUTING_CHUNKING_THRESHOLD:
            route_result_chunks = chunk_data(
                green_paths_route_results, CHUNK_SIZE_FOR_ROUTING_RESULTS
            )
            for route_chunk in route_result_chunks:
                process_and_store_results(db_handler, route_chunk, None)

            process_and_store_results(db_handler, None, actual_travel_times)
        else:
            process_and_store_results(
                db_handler, green_paths_route_results, actual_travel_times
            )

        LOG.info("Green Paths 2 routing pipeline completed.")
    except PipeLineRuntimeError as e:
        LOG.error(f"Routing pipeline failed with error: {e}")
        raise e
