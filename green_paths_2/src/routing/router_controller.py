""" Controller for routing module. """

import pandas as pd
from r5py import CustomCostTransportNetwork, TransportMode
import geopandas as gpd

from ...src.config import (
    CHUNKING_TRESHOLD_KEY,
    DEFAULT_R5_TRAVEL_SPEED_CYCLING,
    DEFAULT_R5_TRAVEL_SPEED_WALKING,
    OSM_IDS_KEY,
    ROUTING_CHUNKING_THRESHOLD,
    ROUTING_KEY,
    TRANSPORT_MODE_KEY,
    TRAVEL_SPEED_KEY,
)

from ...src.routing.routing_utilities import (
    apply_parallel_threading,
    process_chunk,
    to_list_if_iterable,
)
from ...src.timer import time_logger
from ..green_paths_exceptions import R5pyError
from ..preprocessing.data_types import (
    TravelModes,
)
from ..preprocessing.user_config_parser import UserConfig
from ..routing.r5py_router import (
    build_custom_cost_network,
    init_travel_time_matrix_computer,
    route_travel_time_matrix_computer,
)


from ..logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.BLUE.value)


@time_logger
def _get_actual_travel_times(custom_cost_transport_network: CustomCostTransportNetwork):
    """
    Get actual travel times from the custom cost transport network.

    Parameters
    ----------
    custom_cost_transport_network : CustomCostTransportNetwork
        Custom cost transport network.

    Returns
    -------
    dict
        Actual travel times.
    """
    return custom_cost_transport_network.get_base_travel_times()


@time_logger
def format_routing_results(
    routing_results: pd.DataFrame, chunking_treshold: int
) -> pd.DataFrame:
    """
    Format routing results. Use threding for large dataframes.

    Parameters
    ----------
    routing_results : pd.DataFrame
        Routing results.

    Returns
    -------
    pd.DataFrame
        Formatted routing results.
    """
    if routing_results.shape[0] > chunking_treshold:
        # threading for large dataframes
        routing_results = apply_parallel_threading(routing_results, process_chunk)
    else:
        # simple apply for small dataframes
        routing_results[OSM_IDS_KEY] = routing_results[OSM_IDS_KEY].apply(
            to_list_if_iterable
        )
    return routing_results


@time_logger
def _init_travel_metadata(user_config: UserConfig):
    """
    Initialize travel metadata from user configuration.

    Parameters
    ----------
    user_config : UserConfig
        User configuration.

    Returns
    -------
    list
        Transport mode.
    int
        Travel speed.

    """
    travel_speed = user_config.get_nested_attribute([ROUTING_KEY, TRAVEL_SPEED_KEY])
    transport_config_mode = user_config.get_nested_attribute(
        [ROUTING_KEY, TRANSPORT_MODE_KEY]
    )

    # set travel mode and travel speed configurations
    if transport_config_mode == TravelModes.Walking.value:
        transport_mode = [TransportMode.WALK]
        if travel_speed is None:
            travel_speed = DEFAULT_R5_TRAVEL_SPEED_WALKING

    elif transport_config_mode == TravelModes.Cycling.value:
        transport_mode = [TransportMode.BICYCLE]
        if travel_speed is None:
            travel_speed = DEFAULT_R5_TRAVEL_SPEED_CYCLING

    return transport_mode, travel_speed


@time_logger
def route_green_paths_2_paths(
    osm_segmented_network_path: str,
    exposure_dict: dict,
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    user_config: UserConfig,
) -> gpd.GeoDataFrame:
    """
    Route Green Paths 2 paths using R5py (R5 routing engine).

    Parameters
    ----------
    normalized_data_source_names : list[str]
        List of normalized data source names.
    user_config : dict
        User configuration.
    osm_segmented_network_path : str
        Path to the OSM segmented network.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with the routing results.

    Raises
    ------
    ValueError
        If the value for computer in routing_config is invalid.
    """
    try:
        custom_cost_transport_network = build_custom_cost_network(
            osm_segmented_network_path, exposure_dict, user_config
        )

        transport_mode, travel_speed = _init_travel_metadata(user_config)

        # init TravelTimeMatrixComputer
        # currently using just a single transport mode
        # so the travel_speed can be set to both modes
        # this should be refactored, if supporting multiple transport modes
        matrix_computer = init_travel_time_matrix_computer(
            custom_cost_transport_network,
            origins,
            destinations,
            transport_mode,
            speed_walking=travel_speed,
            speed_cycling=travel_speed,
        )

        routing_results = route_travel_time_matrix_computer(matrix_computer)

        # we did not find any routes (no osm_ids in the routing results)
        if OSM_IDS_KEY not in routing_results.columns:
            LOG.error(
                "Routing results do not have osm_ids so no routes found. Check street network and ODS CRS's"
            )
            raise ValueError(
                "Routing results do not have osm_ids so no routes found. Check street network and ODS CRS's"
            )

    except R5pyError as e:
        LOG.error(f"Failed to route Green Paths 2 paths. Error: {e}")
        return None

    # format java lists to python lists
    chunking_treshold = user_config.get_nested_attribute(
        [ROUTING_KEY, CHUNKING_TRESHOLD_KEY], default=ROUTING_CHUNKING_THRESHOLD
    )
    routing_results = format_routing_results(routing_results, chunking_treshold)
    # get actual travel time seconds
    actual_travel_times = _get_actual_travel_times(custom_cost_transport_network)
    return routing_results, actual_travel_times
