""" This module contains the OSM network controller. """

import geopandas as gpd
from .preprocessing.osm_network_handler import OsmNetworkHandler
from .preprocessing.osm_segmenter import (
    segment_or_use_cache_osm_network,
)
from .preprocessing.user_config_parser import UserConfig


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

    if hasattr(user_config.osm_network, "segment_sampling_points_amount"):
        force_sampling_points_amount = (
            user_config.osm_network.segment_sampling_points_amount
        )
    else:
        force_sampling_points_amount = None

    network.process_osm_network(
        project_crs=user_config.project.project_crs,
        original_crs=user_config.osm_network.original_crs,
        data_sources=user_config.data_sources,
        force_sampling_points_amount=force_sampling_points_amount,
    )
    osm_network_gdf: gpd.GeoDataFrame = network.get_network_gdf()
    return osm_network_gdf
