""" Module for routing with R5py. """

import os
from green_paths_2.src.config import (
    ALLOW_MISSING_DATA_DEFAULT,
    JAVA_PATH,
    NORMALIZED_DATA_SUFFIX,
)

import geopandas as gpd

# Set JAVA_HOME
# for some reasons this needs to be set here alos
# os.environ["JAVA_HOME"] = JAVA_PATH


from green_paths_2.src.preprocessing.data_types import DataSourceModel, TravelModes
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.routing.routing_utilities import set_environment_and_import_r5py
from green_paths_2.src.timer import time_logger

from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.BLUE.value)


# set_environment_and_import_r5py()
import r5py
from r5py import (
    CustomCostTransportNetwork,
    DetailedItinerariesComputer,
    TravelTimeMatrixComputer,
)


@time_logger
def init_travel_time_matrix_computer(
    custom_cost_transport_network: CustomCostTransportNetwork,
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    transport_mode: list[TravelModes],
):
    """Route with TravelTimeMatrixComputer."""
    LOG.info("Initing TravelTimeMatrixComputer")

    travel_time_matrix_computer_custom_cost = TravelTimeMatrixComputer(
        custom_cost_transport_network,
        origins=origins,
        destinations=destinations,
        transport_modes=transport_mode,
    )

    LOG.info("Finished initing TravelTimeMatrixComputer")
    return travel_time_matrix_computer_custom_cost


@time_logger
def route_travel_time_matrix_computer(
    travel_time_matrix_computer,
):
    LOG.info("Initing TravelTimeMatrixComputer")
    travel_time_matrix_computer_results = (
        travel_time_matrix_computer.compute_travel_times()
    )
    LOG.info("Finished routing with TravelTimeMatrixComputer")

    return travel_time_matrix_computer_results


@time_logger
def init_detailed_itineraries_computer(
    custom_cost_transport_network, origins, destinations, transport_mode
):
    """Initialize DetailedItinerariesComputer."""
    LOG.info("Initing DetailedItinerariesComputer")

    detailed_computer_custom_cost = DetailedItinerariesComputer(
        custom_cost_transport_network,
        origins=origins,
        destinations=destinations,
        transport_modes=transport_mode,
    )
    LOG.info("Finished initing DetailedItinerariesComputer")

    return detailed_computer_custom_cost


@time_logger
def route_detailed_itineraries_computer(
    detailed_itineraries_computer,
):
    """Route with DetailedItinerariesComputer."""
    LOG.info("Routing with DetailedItinerariesComputer")

    detailed_itineraries_routing_results = (
        detailed_itineraries_computer.compute_travel_details()
    )
    LOG.info("Finished routing with DetailedItinerariesComputer")

    return detailed_itineraries_routing_results


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

    for exposure_confs in routing_config.exposure_parameters:
        exposure_name = exposure_confs.get(DataSourceModel.Name.value)
        exposure_name_normalized = f"{exposure_name}{NORMALIZED_DATA_SUFFIX}"
        names.append(exposure_name)
        # sensitivity, allow_missing = _get_data_metadata_with_data_name(
        #     data_key, routing_config
        # )
        sensitivities.append(exposure_confs.get(DataSourceModel.Sensitivity.value))
        custom_cost_segment_weight_factors.append(
            exposure_dict.get(exposure_name_normalized)
        )
        allow_missing_datas.append(
            exposure_confs.get(
                DataSourceModel.AllowMissingData.value, ALLOW_MISSING_DATA_DEFAULT
            )
        )

    return names, sensitivities, custom_cost_segment_weight_factors, allow_missing_datas


# # TODO: remove???
# def _get_data_metadata_with_data_name(name: str, routing_config: UserConfig) -> float:
#     for routing_config_item in routing_config:
#         # Check if the name is in your dictionary
#         if routing_config_item["name"] in name:
#             sensitivity = routing_config_item.get("sensitivity")
#             # Check if the sensitivity is provided in user_config
#             # If not, return the default value True for allowing missing values
#             allow_missing_data = routing_config_item.get("allow_missing_data", True)
#     return sensitivity, allow_missing_data


@time_logger
def build_custom_cost_network(
    osm_segmented_network_path: str, exposure_dict: dict, routing_config: dict
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
        _build_custom_cost_networks_params(exposure_dict, routing_config)
    )

    LOG.info(
        f"Data names: {names}. Using sensitivities: {sensitivities}. Using allow_missing_data: {allow_missing_data}"
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
    LOG.info("Finished building network")

    return custom_cost_transport_network
