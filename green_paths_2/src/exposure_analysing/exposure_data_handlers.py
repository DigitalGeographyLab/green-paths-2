""" """

from green_paths_2.src.config import (
    OSM_ID_DEFAULT_KEY,
    OSM_NETWORK_GDF_CACHE_PATH,
    ROUTING_RESULTS_CSV_CACHE_PATH,
    ROUTING_RESULTS_GDF_CACHE_PATH,
    SEGMENT_STORE_GDF_CACHE_PATH,
)
from green_paths_2.src.data_utilities import get_and_convert_gdf_to_dict
from green_paths_2.src.preprocessing.data_types import RoutingComputers

from shapely.geometry import MultiLineString, LineString
from shapely.ops import linemerge, unary_union
from typing import List


def load_datas_from_cache(routing_computer: str):
    """
    Load routing results and exposure store from cache.

    Parameters
    ----------
    user_config : UserConfig
        User configuration.

    Returns
    -------
    tuple
        Tuple containing routing results and exposure store.
    """

    # TODO: säädä traveltimes...

    # travel_times_store = get_and_convert_gdf_to_dict(
    #     TRAVEL_TIMES_CSV_CACHE_PATH, OSM_ID_DEFAULT_KEY
    # )

    if routing_computer == RoutingComputers.Matrix.value:
        routing_results_path = ROUTING_RESULTS_CSV_CACHE_PATH
    elif routing_computer == RoutingComputers.Detailed.value:
        routing_results_path = ROUTING_RESULTS_GDF_CACHE_PATH

    routing_results = get_and_convert_gdf_to_dict(
        routing_results_path, OSM_ID_DEFAULT_KEY, orient="records"
    )
    segment_exposure_store = get_and_convert_gdf_to_dict(
        SEGMENT_STORE_GDF_CACHE_PATH, OSM_ID_DEFAULT_KEY
    )

    osm_network_store = get_and_convert_gdf_to_dict(
        OSM_NETWORK_GDF_CACHE_PATH, OSM_ID_DEFAULT_KEY
    )

    return routing_results, segment_exposure_store, osm_network_store


def combine_multilinestrings_to_single_linestring(
    multilinestrings: List[MultiLineString],
) -> LineString:
    """
    Combine multiple MultiLineString objects into a single LineString.

    Parameters:
    - multilinestrings: a list of MultiLineString objects to be combined.

    Returns:
    - A single LineString object if the line segments can be merged,
      otherwise returns None.
    """
    try:
        # Use unary_union to handle both LineString and MultiLineString objects,
        # and to ensure all geometries are considered for merging.
        combined_line_geometries = unary_union(multilinestrings)
        # merge multiple LineString objects into a single LineString
        merged_line = linemerge(combined_line_geometries)

        if isinstance(merged_line, LineString):
            return merged_line
        else:
            print(
                "Warning: The geometries could not be merged into a single LineString."
            )
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
