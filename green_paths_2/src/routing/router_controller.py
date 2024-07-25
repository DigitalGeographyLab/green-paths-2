""" Controller for routing module. """

from r5py import TransportMode
import geopandas as gpd
import numpy as np

from green_paths_2.src.config import (
    DEFAULT_R5_TRAVEL_SPEED_CYCLING,
    DEFAULT_R5_TRAVEL_SPEED_WALKING,
    OSM_IDS_KEY,
    ROUTING_KEY,
    TRANSPORT_MODE_KEY,
    TRAVEL_SPEED_KEY,
)

from green_paths_2.src.routing.routing_utilities import to_list_if_iterable
from green_paths_2.src.timer import time_logger
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

    except R5pyError as e:
        LOG.error(f"Failed to route Green Paths 2 paths. Error: {e}")
        return None

    # get actual travel time seconds from the custom cost transport network
    # just get all because filtering with osm_id would take too long
    actual_travel_times = custom_cost_transport_network.get_base_travel_times()

    osm_ids_np = routing_results[OSM_IDS_KEY].values
    vectorized_conversion = np.vectorize(to_list_if_iterable, otypes=[object])
    routing_results[OSM_IDS_KEY] = vectorized_conversion(osm_ids_np)

    return routing_results, actual_travel_times
