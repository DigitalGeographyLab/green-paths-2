""" TODO """

import geopandas as gpd
from green_paths_2.src.preprocessing.osm_network_handler import OsmNetworkHandler
from green_paths_2.src.preprocessing.osm_segmenter import (
    segment_or_use_cache_osm_network,
)
from green_paths_2.src.preprocessing.user_config_parser import UserConfig


def handle_osm_network_process(user_config: UserConfig) -> gpd.GeoDataFrame:
    """
    Handle the OSM network process.

    Parameters
    ----------
    user_config : UserConfig
        User configuration object.

    Returns
    -------
    gpd.GeoDataFrame
        The OSM network GeoDataFrame.
    """
    osm_network_pbf_file_path = segment_or_use_cache_osm_network(
        user_config.osm_network.osm_pbf_file_path
    )

    network = OsmNetworkHandler(osm_pbf_file=osm_network_pbf_file_path)

    network.process_osm_network(
        project_crs=user_config.project_crs,
        original_crs=user_config.osm_network.original_crs,
        segment_sampling_points_amount=user_config.osm_network.segment_sampling_points_amount,
    )
    osm_network_gdf: gpd.GeoDataFrame = network.get_network_gdf()
    return osm_network_gdf
