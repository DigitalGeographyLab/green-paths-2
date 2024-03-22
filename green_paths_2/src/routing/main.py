""" Routing pipeline for Green Paths 2. """

import os
import sys

from green_paths_2.src.config import (
    JAVA_PATH,
    NORMALIZED_DATA_SUFFIX,
    R5_JAR_FILE_PATH,
)
from green_paths_2.src.data_utilities import (
    construct_osm_segmented_network_name,
    get_exposure_data_dict,
)
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.preprocessing.user_data_handler import UserDataHandler
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def _set_environment_and_import_r5py() -> bool:
    """Set environment variables and import Green Paths 2 patch version of r5py."""
    try:
        import os, sys

        # Set environment variables
        os.environ["JAVA_HOME"] = JAVA_PATH
        # Correctly use extend to add R5 classpath argument
        sys.argv.extend(["--r5-classpath", R5_JAR_FILE_PATH])

        # Now, dynamically import r5py and make it global
        global r5py, CustomCostTransportNetwork, TravelTimeMatrixComputer, DetailedItinerariesComputer
        import r5py
        from r5py import CustomCostTransportNetwork
        from r5py.r5.detailed_itineraries_computer import DetailedItinerariesComputer
        from r5py.r5.travel_time_matrix_computer import TravelTimeMatrixComputer

        return True
    except Exception as e:
        LOG.error(
            f"Failed to set environment variables or import Green Paths 2 patch version of r5py. Error: {e}"
        )
        return False


# def _parse_exposure_dict_data_keys(exposure_dict: dict) -> list:
#     """
#     Filter out the keys.

#     Parameters
#     ----------
#     exposure_dict : dict
#         The exposure dictionary.

#     Returns
#     -------
#     list
#         The filtered keys.
#     """

#     # loop through list of dicts, get their all keys, and filter out the ones that are not osm_id or _normalized
#     data_keys = []
#     for exposure in exposure_dict:
#         for key in exposure.keys():
#             if key not in [f"{key}_normalized" or "osm_id" for key in data_keys]:
#                 data_keys.append(key)
#     return data_keys


# def _parse_exposure_dict_with_data_names(
#     data_keys: list[str], exposure_dicts_list: list[dict]
# ) -> dict:
#     """TODO"""
#     exposure_dicts = []
#     parsed_exposure_dict = {}
#     for data_key in data_keys:
#         for exposure_dict in exposure_dicts_list:
#             normalized_key = f"{data_key}{NORMALIZED_DATA_SUFFIX}"
#             parsed_exposure_dict[data_key] = {
#                 exposure_dict["osm_id"]: exposure_dict[normalized_key]
#             }
#         exposure_dicts.append(parsed_exposure_dict)
#     return exposure_dicts


def _test_init_ods():

    # TODO: remove this...

    import os
    import geopandas

    population_grid = geopandas.read_file(
        os.path.join(
            "/Users/hcroope/omat_playground/r5py/docs/_static/data/Helsinki/population_grid_2020.gpkg"
        )
    )
    import shapely

    RAILWAY_STATION = shapely.Point(24.941521, 60.170666)
    origins = population_grid.copy()
    # origins = origins.iloc[:100]
    origins.geometry = origins.geometry.centroid

    destinations = geopandas.GeoDataFrame(
        {"id": [1], "geometry": [RAILWAY_STATION]},
        crs="EPSG:4326",
    )
    return origins, destinations


def _get_data_metadata_with_data_name(name: str, routing_config: UserConfig) -> float:
    for routing_config_item in routing_config:
        # Check if the name is in your dictionary
        if routing_config_item["name"] in name:
            sensitivity = routing_config_item.get("sensitivity")
            # Check if the sensitivity is provided in user_config
            # If not, return the default value True for allowing missing values
            allow_missing_data = routing_config_item.get("allow_missing_data", True)
    return sensitivity, allow_missing_data


def _build_custom_cost_networks_params(
    exposure_dict: dict, routing_config: dict
) -> tuple:
    """
    Populate the parameters for building custom cost networks.

    Parameters
    ----------
    routing_config : dict
        The routing configuration.

    Returns
    -------
    tuple
        The names, sensitivities, cost data and allow_missing_data dictionaries.
    """
    names = []
    sensitivities = []
    custom_cost_segment_weight_factors = []
    allow_missing_datas = []

    for data_key, exposure_dict in exposure_dict.items():
        names.append(data_key)
        sensitivity, allow_missing = _get_data_metadata_with_data_name(
            data_key, routing_config
        )
        sensitivities.append(sensitivity)
        custom_cost_segment_weight_factors.append(exposure_dict)
        allow_missing_datas.append(allow_missing)

    return names, sensitivities, custom_cost_segment_weight_factors, allow_missing_datas


def build_custom_cost_network(
    osm_segmented_network_path: str, exposure_dict: dict, user_config: dict
):
    """
    Build custom cost network.

    Parameters
    ----------
    osm_segmented_network_path : str
        The path to the segmented OSM network.
    exposure_dict : dict
        The exposure dictionary.
    user_config : dict
        The user configuration.

    Returns
    -------
    CustomCostTransportNetwork
        The custom cost transport network.
    """
    LOG.info("Building custom cost networks")

    names, sensitivities, custom_cost_segment_weight_factors, allow_missing_data = (
        _build_custom_cost_networks_params(exposure_dict, user_config.routing)
    )

    LOG.info(
        f"Data names: {names}. Using sensitivities: {sensitivities}, and allow_missing_data: {allow_missing_data}"
    )

    # convert all keys in custom_cost_segment_weight_factors list to str
    custom_cost_segment_weight_factors = [
        {str(k): v for k, v in d.items()} for d in custom_cost_segment_weight_factors
    ]

    custom_cost_transport_network = CustomCostTransportNetwork(
        osm_pbf=osm_segmented_network_path,
        names=names,
        sensitivities=sensitivities,
        custom_cost_segment_weight_factors=custom_cost_segment_weight_factors,
        allow_missing_osmids=allow_missing_data,
    )

    return custom_cost_transport_network


@time_logger
def _build_and_route_with_travel_time_matrix_computer(
    custom_cost_transport_network, origins, destinations, travel_mode=None
):
    """Route with TravelTimeMatrixComputer."""
    import r5py

    travel_time_matrix_computer_custom_cost = TravelTimeMatrixComputer(
        custom_cost_transport_network,
        origins=origins,
        destinations=destinations,
        transport_modes=[
            r5py.TransportMode.WALK,
            r5py.TransportMode.BICYCLE,
        ],
    )
    routing_results = travel_time_matrix_computer_custom_cost.compute_travel_times()
    return routing_results


@time_logger
def _build_and_route_with_detailed_itineraries_computer(
    custom_cost_transport_network, origins, destinations, travel_mode=None
):
    """Route with DetailedItinerariesComputer."""
    import r5py

    detailed_computer_custom_cost = DetailedItinerariesComputer(
        custom_cost_transport_network,
        origins=origins,
        destinations=destinations,
        transport_modes=[
            r5py.TransportMode.BICYCLE,
        ],
    )
    detailed_itineraries_routing_results = (
        detailed_computer_custom_cost.compute_travel_details()
    )
    return detailed_itineraries_routing_results


@time_logger
def routing_pipeline(data_handler: UserDataHandler, user_config: UserConfig):
    """TODO"""
    LOG.info("\n\n\nStarting routing pipeline\n\n\n")

    # TODO: check that segmented network exists

    osm_segmented_network_path = construct_osm_segmented_network_name(
        user_config.osm_network.osm_pbf_file_path
    )

    if not os.path.exists(osm_segmented_network_path):
        raise FileNotFoundError(
            f"Segmented OSM network not found from path: {osm_segmented_network_path}. Please run preprocessing pipeline or segmenter first."
        )

    if not _set_environment_and_import_r5py():
        raise Exception(
            "Failed to set environment variables and import r5py. Exiting routing!"
        )

    data_source_names = data_handler.get_data_source_names()
    normalized_data_source_names = [
        f"{data_source_name}{NORMALIZED_DATA_SUFFIX}"
        for data_source_name in data_source_names
    ]
    exposure_dict = get_exposure_data_dict(normalized_data_source_names)

    custom_cost_transport_network = build_custom_cost_network(
        osm_segmented_network_path, exposure_dict, user_config
    )

    origins, destinations = _test_init_ods()

    travel_time_matrix_results = _build_and_route_with_travel_time_matrix_computer(
        custom_cost_transport_network, origins, destinations
    )

    print(travel_time_matrix_results)

    detailed_itineraries_retults = _build_and_route_with_detailed_itineraries_computer(
        custom_cost_transport_network, origins, destinations
    )
    # TODO: add travel mode
    # TODO: figure out how to import r5py properly

    print(detailed_itineraries_retults)
