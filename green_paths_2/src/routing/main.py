""" Routing pipeline for Green Paths 2. """

# DISCLAIMER:
# WE NEED TO RUN _set_environment_and_import_r5py()
# WHICH SETS ENVIRONMENT VARIABLES AND IMPORTS GREEN PATHS 2 PATCH VERSION OF R5PY
# LIKE THIS BEFORE OTHER IMPORTS DUE TO NEED FOR --r5-classpath ARGUMENT BEFORE R5PY IMPORTS
# IT IS DIRTY, AND THERE MIGHT BE A BETTER WAY TO DO THIS

from green_paths_2.src.config import (
    OSM_ID_KEY,
    ROUTING_CACHE_DIR_NAME,
    ROUTING_RESULTS_CSV_CACHE_PATH,
    SAVE_TO_CACHE_KEY,
    SEGMENT_STORE_GDF_CACHE_PATH,
    TRAVEL_TIMES_CSV_CACHE_PATH,
)

from green_paths_2.src.routing.routing_utilities import (
    init_origin_destinations_from_files,
    set_environment_and_import_r5py,
)

# this code is ran before any other codes in routing module
if not set_environment_and_import_r5py():
    raise R5pyError(
        "Failed to set environment variables and import r5py. Exiting routing!"
    )


from green_paths_2.src.green_paths_exceptions import PipeLineRuntimeError, R5pyError
from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


import geopandas as gpd
from green_paths_2.src.timer import time_logger
from green_paths_2.src.cache_cleaner import clear_cache_dirs

from green_paths_2.src.data_utilities import (
    convert_gdf_to_dict,
    convert_travel_times_dicts_to_gdf,
    get_and_convert_gdf_to_dict,
    save_gdf_to_cache,
)
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.preprocessing.user_data_handler import UserDataHandler
from green_paths_2.src.routing.router_controller import route_green_paths_2_paths
from green_paths_2.src.routing.routing_utilities import (
    get_normalized_data_source_names,
    test_2_init_single_hki_od_points,
    test_init_ods,
    validate_segmented_osm_network_path,
)


@time_logger
def routing_pipeline(
    data_handler: UserDataHandler,
    user_config: UserConfig,
    exposure_gdf: gpd.GeoDataFrame = None,
):
    """
    Run the routing pipeline.

    Parameters:
    ----------
    data_handler : UserDataHandler
        The UserDataHandler object.
    user_config : UserConfig
        The UserConfig object.
    exposure_gdf : gpd.GeoDataFrame, optional
        The exposure data as a GeoDataFrame. Defaults to None.

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

        # clear routing cache
        clear_cache_dirs([ROUTING_CACHE_DIR_NAME])

        osm_segmented_network_path = validate_segmented_osm_network_path(
            user_config.osm_network.osm_pbf_file_path
        )

        data_source_names = data_handler.get_data_source_names()
        normalized_data_source_names = get_normalized_data_source_names(
            data_source_names
        )

        # get exposure data, from parameter or cache if in parameters
        if exposure_gdf is not None:
            LOG.info("Using parameter exposure data for routing.")
            exposure_dict = convert_gdf_to_dict(exposure_gdf)
        else:
            LOG.info("Loading data from cache for routing pipeline")
            exposure_dict = get_and_convert_gdf_to_dict(
                SEGMENT_STORE_GDF_CACHE_PATH,
                OSM_ID_KEY,
                normalized_data_source_names,
            )

        if not exposure_dict:
            raise ValueError(
                "Exposure data not found for routing pipeline. Not as parameter nor from cache."
            )

        # origins, destinations = test_init_ods()
        origins, destinations = init_origin_destinations_from_files(
            user_config.routing, user_config.project_crs
        )

        print("origin is: ")
        print(origins)
        print("destination is: ")
        print(destinations)

        green_paths_route_results, actual_travel_times = route_green_paths_2_paths(
            osm_segmented_network_path,
            exposure_dict,
            origins,
            destinations,
            user_config.routing,
        )

        travel_times_gdf = convert_travel_times_dicts_to_gdf(actual_travel_times)

        # TODO: do we need / are we using travel_times_gdf?

        has_save_to_cache = hasattr(user_config, SAVE_TO_CACHE_KEY)

        if has_save_to_cache and user_config.save_to_cache:
            save_gdf_to_cache(green_paths_route_results, ROUTING_RESULTS_CSV_CACHE_PATH)
            save_gdf_to_cache(travel_times_gdf, TRAVEL_TIMES_CSV_CACHE_PATH)

        LOG.info("Green Paths 2 routing pipeline completed.")
        return green_paths_route_results, actual_travel_times
    except PipeLineRuntimeError as e:
        LOG.error(f"Routing pipeline failed with error: {e}")
        raise e
