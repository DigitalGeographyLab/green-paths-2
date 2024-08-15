""" Module for routing with R5py. """

import datetime
from functools import wraps
from ..config import (
    ALLOW_MISSING_DATA_DEFAULT,
    EXPOSURE_PARAMETERS_KEY,
    NORMALIZED_DATA_SUFFIX,
    PRECALCULATE_KEY,
    ROUTING_KEY,
    TRAVEL_SPEED_KEY,
)

import geopandas as gpd

from ..preprocessing.data_types import DataSourceModel, TravelModes
from ..preprocessing.user_config_parser import UserConfig
from ..routing.routing_utilities import set_environment_and_import_r5py
from ..timer import time_logger, with_funny_process_reporter

from ..logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.BLUE.value)

set_environment_and_import_r5py()

# import r5py
from r5py import (
    CustomCostTransportNetwork,
    TravelTimeMatrixComputer,
)


@time_logger
def init_travel_time_matrix_computer(
    custom_cost_transport_network: CustomCostTransportNetwork,
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    transport_mode: list[TravelModes],
    speed_walking: float,
    speed_cycling: float,
):
    """Route with TravelTimeMatrixComputer."""
    LOG.info("Initing TravelTimeMatrixComputer")

    # max_time is set to a large value to ensure that all routes are computed
    # if the max_time is met, the route is not finished
    # the travel times are not actual times, but rather the cost of the route

    # Maximum allowable seconds for a C int
    max_c_int_seconds = 2147483647
    # just to be sure that the custom costs route planning wont fail because max_time is too short
    # Set a very large number of seconds directly

    # Set the max_time using the maximum C int value
    max_time = datetime.timedelta(seconds=max_c_int_seconds)

    travel_time_matrix_computer_custom_cost = TravelTimeMatrixComputer(
        custom_cost_transport_network,
        origins=origins,
        destinations=destinations,
        transport_modes=transport_mode,
        speed_walking=speed_walking,
        speed_cycling=speed_cycling,
        max_time=max_time,
    )

    LOG.info("Finished initing TravelTimeMatrixComputer")
    return travel_time_matrix_computer_custom_cost


@with_funny_process_reporter
@time_logger
def route_travel_time_matrix_computer(travel_time_matrix_computer):
    LOG.info("Computing traveltimes with TravelTimeMatrixComputer")
    travel_time_matrix_computer_results = (
        travel_time_matrix_computer.compute_travel_times()
    )
    LOG.info("Finished routing with TravelTimeMatrixComputer")

    return travel_time_matrix_computer_results


def _build_custom_cost_networks_params(
    exposure_dict: dict, user_config: UserConfig
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

    exposure_parameters = user_config.get_nested_attribute(
        [ROUTING_KEY, EXPOSURE_PARAMETERS_KEY]
    )

    for exposure_confs in exposure_parameters:
        exposure_name = exposure_confs.get(DataSourceModel.Name.value)
        exposure_name_normalized = f"{exposure_name}{NORMALIZED_DATA_SUFFIX}"
        names.append(exposure_name)
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


@time_logger
def build_custom_cost_network(
    osm_segmented_network_path: str, exposure_dict: dict, user_config: UserConfig
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
        _build_custom_cost_networks_params(exposure_dict, user_config)
    )

    LOG.info(
        f"Data names: {names}. Using sensitivities: {sensitivities}. Using allow_missing_data: {allow_missing_data}"
    )

    # convert all keys in custom_cost_segment_weight_factors list to str
    custom_cost_segment_weight_factors = [
        {str(k): v for k, v in d.items()} for d in custom_cost_segment_weight_factors
    ]

    precalculate = user_config.get_nested_attribute(
        [ROUTING_KEY, PRECALCULATE_KEY], default=True
    )

    travel_speed = user_config.get_nested_attribute(
        [ROUTING_KEY, TRAVEL_SPEED_KEY], default=0
    )

    custom_cost_transport_network = CustomCostTransportNetwork(
        osm_pbf=osm_segmented_network_path,
        names=names,
        sensitivities=sensitivities,
        custom_cost_segment_weight_factors=custom_cost_segment_weight_factors,
        allow_missing_osmids=allow_missing_data,
        precalculate=precalculate,
        speed_walking=travel_speed,
        speed_cycling=travel_speed,
    )
    LOG.info("Finished building network")

    return custom_cost_transport_network
