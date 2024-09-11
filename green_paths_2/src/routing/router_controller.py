""" Controller for routing module. """

import numpy as np
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
    TRAVEL_SPEED_CYCLING_KEY,
    TRAVEL_SPEED_KEY,
    TRAVEL_SPEED_WALKING_KEY,
)

from ...src.timer import time_logger
from ..green_paths_exceptions import R5pyError
from ..preprocessing.data_types import (
    TravelModes,
)
from ..preprocessing.user_config_parser import UserConfig
from .r5py_router import (
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
def _init_travel_mode_and_speed(user_config: UserConfig, transport_mode_param=None):
    """
    Initialize travel metadata from user configuration.

    Note: If transport_mode_param is given, it will override the transport mode
    this is used for the API

    speed walking and cycling are used for the API and they override the travel speed

    Parameters
    ----------
    user_config : UserConfig
        User configuration.
    transport_mode_param : str, optional
        Transport mode parameter for API, by default None

    Returns
    -------
    list
        Transport mode.
    int
        Travel speed.

    """
    # use the travel speed from the user config as default
    general_override_travel_speed = user_config.get_nested_attribute(
        [ROUTING_KEY, TRAVEL_SPEED_KEY], default=None
    )

    # override travel speed if walking or cycling speeds are given
    speed_walking = user_config.get_nested_attribute(
        [ROUTING_KEY, TRAVEL_SPEED_WALKING_KEY], default=DEFAULT_R5_TRAVEL_SPEED_WALKING
    )

    speed_cycling = user_config.get_nested_attribute(
        [ROUTING_KEY, TRAVEL_SPEED_CYCLING_KEY], default=DEFAULT_R5_TRAVEL_SPEED_CYCLING
    )

    # see if transport mode is given as parameter and if it is valid
    # override the config value
    if (
        transport_mode_param
        and transport_mode_param == TravelModes.Walking.value
        or transport_mode_param == TravelModes.Cycling.value
    ):
        transport_config_mode = transport_mode_param
    else:
        # otherwise get it from the user config
        transport_config_mode = user_config.get_nested_attribute(
            [ROUTING_KEY, TRANSPORT_MODE_KEY]
        )

    # set travel mode and travel speed configurations
    if transport_config_mode == TravelModes.Walking.value:
        transport_mode = [TransportMode.WALK]
        if general_override_travel_speed:
            # use travel speed from the config
            speed_walking = general_override_travel_speed

    elif transport_config_mode == TravelModes.Cycling.value:
        transport_mode = [TransportMode.BICYCLE]
        if general_override_travel_speed:
            speed_cycling = general_override_travel_speed

    return transport_mode, speed_walking, speed_cycling


@time_logger
def route_green_paths_2_paths(
    custom_cost_transport_network: CustomCostTransportNetwork,
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    user_config: UserConfig,
    no_travel_times: bool = False,
    transport_mode_param=None,
) -> gpd.GeoDataFrame:
    """
    Route Green Paths 2 paths using R5py (R5 routing engine).

    Parameters
    ----------
    custom_cost_transport_network : CustomCostTransportNetwork
        Custom cost transport network.
    origins : gpd.GeoDataFrame
        GeoDataFrame with the origins.
    destinations : gpd.GeoDataFrame
        GeoDataFrame with the destinations.
    user_config : dict
        User configuration.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with the routing results
    dict
        Dictionary with the actual travel times

    Raises
    ------
    ValueError
        If the value for computer in routing_config is invalid.
    """
    try:
        transport_mode, speed_walking, speed_cycling = _init_travel_mode_and_speed(
            user_config, transport_mode_param
        )

        # init TravelTimeMatrixComputer
        # currently using just a single transport mode
        # so the travel_speed can be set to both modes
        # this should be refactored, if supporting multiple transport modes
        matrix_computer = init_travel_time_matrix_computer(
            custom_cost_transport_network,
            origins,
            destinations,
            transport_mode,
            speed_walking=speed_walking,
            speed_cycling=speed_cycling,
        )

        routing_results = route_travel_time_matrix_computer(matrix_computer)
        LOG.info("Finished routing test log")

    except R5pyError as e:
        LOG.error(f"Failed to route Green Paths 2 paths. Error: {e}")
        return None

    LOG.info("finished routing, checking that has osm_ids in columns")
    # we did not find any routes (no osm_ids in the routing results)s
    if routing_results.empty:
        LOG.error("No routes found")

    if OSM_IDS_KEY not in routing_results.columns:
        # print first rows to see what is in the routing results
        LOG.error(routing_results.head())
        LOG.error(
            "Routing results do not have osm_ids so no routes found. Check street network and ODS CRS's"
        )
        raise ValueError(
            "Routing results do not have osm_ids so no routes found. Check street network and ODS CRS's"
        )

    # get actual travel time seconds from the custom cost transport network
    # just get all because filtering with osm_id would take too long
    if no_travel_times:
        return routing_results, None
    else:
        actual_travel_times = _get_actual_travel_times(custom_cost_transport_network)
        return routing_results, actual_travel_times
