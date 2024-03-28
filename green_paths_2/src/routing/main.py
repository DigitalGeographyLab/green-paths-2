""" Routing pipeline for Green Paths 2. """

# setting JAVA_HOME environment variable, important!
import os
from green_paths_2.src.cache_cleaner import clear_cache_dirs
from green_paths_2.src.config import (
    JAVA_PATH,
    OSM_ID_DEFAULT_KEY,
    ROUTING_CACHE_DIR_NAME,
    ROUTING_RESULTS_CSV_CACHE_PATH,
    ROUTING_RESULTS_GDF_CACHE_PATH,
    SEGMENT_STORE_GDF_CACHE_PATH,
    TRAVEL_TIMES_CSV_CACHE_PATH,
)
from green_paths_2.src.preprocessing.data_types import RoutingComputers

os.environ["JAVA_HOME"] = JAVA_PATH

import geopandas as gpd
from green_paths_2.src.data_utilities import (
    convert_travel_times_dicts_to_gdf,
    filter_gdf_by_columns_if_found,
    get_and_convert_gdf_to_dict,
    prepare_gdf_for_saving,
    save_gdf_to_cache_as_gpkg,
)
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.preprocessing.user_data_handler import UserDataHandler
from green_paths_2.src.routing.router_controller import route_green_paths_2_paths
from green_paths_2.src.routing.routing_utilities import (
    get_normalized_data_source_names,
    set_environment_and_import_r5py,
    test_2_init_single_hki_od_points,
    test_init_ods,
    validate_segmented_osm_network_path,
)
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.GREEN.value)

set_environment_and_import_r5py()


# def set_environment_and_import_r5py() -> bool:
#     """Set environment variables and import Green Paths 2 patch version of r5py."""
#     try:
#         import os, sys

#         # Set environment variables
#         os.environ["JAVA_HOME"] = JAVA_PATH
#         # Correctly use extend to add R5 classpath argument
#         sys.argv.extend(["--r5-classpath", R5_JAR_FILE_PATH])

#         # Now, dynamically import r5py and make it global
#         global r5py, CustomCostTransportNetwork, TravelTimeMatrixComputer, DetailedItinerariesComputer
#         import r5py
#         from r5py import CustomCostTransportNetwork
#         from r5py.r5.detailed_itineraries_computer import DetailedItinerariesComputer
#         from r5py.r5.travel_time_matrix_computer import TravelTimeMatrixComputer

#         return True
#     except Exception as e:
#         LOG.error(
#             f"Failed to set environment variables or import Green Paths 2 patch version of r5py. Error: {e}"
#         )
#         return False


@time_logger
def routing_pipeline(data_handler: UserDataHandler, user_config: UserConfig):
    """Run the routing pipeline."""
    LOG.info("\n\n\nStarting routing pipeline\n\n\n")
    try:

        # clear routing cache
        clear_cache_dirs([ROUTING_CACHE_DIR_NAME])

        # import r5py and set environment variables dynamically
        if not set_environment_and_import_r5py():
            raise Exception(
                "Failed to set environment variables and import r5py. Exiting routing!"
            )

        osm_segmented_network_path = validate_segmented_osm_network_path(
            user_config.osm_network.osm_pbf_file_path
        )

        data_source_names = data_handler.get_data_source_names()
        normalized_data_source_names = get_normalized_data_source_names(
            data_source_names
        )

        exposure_dict = get_and_convert_gdf_to_dict(
            SEGMENT_STORE_GDF_CACHE_PATH,
            OSM_ID_DEFAULT_KEY,
            normalized_data_source_names,
        )

        # origins, destinations = test_init_ods()
        origins, destinations = test_2_init_single_hki_od_points()

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

        # print("sideshoooow")
        # print(actual_travel_times)
        # print(type(actual_travel_times))

        travel_times_gdf = convert_travel_times_dicts_to_gdf(actual_travel_times)

        saveable_route_results = prepare_gdf_for_saving(
            green_paths_route_results, user_config.routing.computer
        )

        if user_config.routing.computer == RoutingComputers.Matrix.value:
            cache_file_path = ROUTING_RESULTS_CSV_CACHE_PATH
        elif user_config.routing.computer == RoutingComputers.Detailed.value:
            cache_file_path = ROUTING_RESULTS_GDF_CACHE_PATH

        save_gdf_to_cache_as_gpkg(saveable_route_results, cache_file_path)

        save_gdf_to_cache_as_gpkg(travel_times_gdf, TRAVEL_TIMES_CSV_CACHE_PATH)

        LOG.info("Green Paths 2 routing pipeline completed.")
    except Exception as e:
        LOG.error(f"Routing pipeline failed with error: {e}")
        raise e
