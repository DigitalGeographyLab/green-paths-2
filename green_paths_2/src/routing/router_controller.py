""" Controller for routing module. """

from r5py import TransportMode
import geopandas as gpd
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


def route_green_paths_2_paths(
    osm_segmented_network_path: str,
    exposure_dict: dict,
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    routing_config: UserConfig,
) -> gpd.GeoDataFrame:
    """
    Route Green Paths 2 paths using R5py (R5 routing engine).


    Parameters
    ----------
    normalized_data_source_names : list[str]
        List of normalized data source names.
    routing_config : dict
        Routing configuration.
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
            osm_segmented_network_path, exposure_dict, routing_config
        )

        transport_config_mode = routing_config.transport_mode

        if transport_config_mode == TravelModes.Walking.value:
            transport_mode = [TransportMode.WALK]
        elif transport_config_mode == TravelModes.Cycling.value:
            transport_mode = [TransportMode.BICYCLE]

        matrix_computer = init_travel_time_matrix_computer(
            custom_cost_transport_network, origins, destinations, transport_mode
        )
        routing_results = route_travel_time_matrix_computer(matrix_computer)
    except R5pyError as e:
        LOG.error(f"Failed to route Green Paths 2 paths. Error: {e}")
        return None

    # get actual travel time seconds from the custom cost transport network
    # just get all because filtering with osm_id would take too long
    actual_travel_times = custom_cost_transport_network.get_base_travel_times()

    return routing_results, actual_travel_times
