""" """
import os
import geopandas as gpd
from src.config import (
    NETWORK_GPKG_CACHE_PATH,
    NETWORK_COLUMNS_TO_KEEP,
)
from src.logging import setup_logger, LoggerColors
from src.preprocessing.osm_network_handler import OsmNetworkHandler
from src.preprocessing.user_config_parser import UserConfig

LOG = setup_logger(__name__, LoggerColors.GREEN.value)

# TODO: do better dev flag
ROOPE_DEVELOPMENT = True


def process_osm_network(
    use_network_cache: bool = False, user_config: UserConfig = None
):
    """
    Process OSM network.
    Use cached network if available, otherwise build new and save to cache.


    :param use_network_cache: Use cached network if available.
    :param user_config: User configurations.
    :return: Processed OSM network.
    """

    if use_network_cache and os.path.exists(NETWORK_GPKG_CACHE_PATH):
        LOG.info("Loading buffered network from cache")
        network = OsmNetworkHandler()
        cached_gpd = gpd.read_file(NETWORK_GPKG_CACHE_PATH)
        network.set_network_gdf(cached_gpd)
    else:
        LOG.info(
            "Buffered network not found in cache, building new and saving to cache"
        )

        network = OsmNetworkHandler(
            osm_pbf_file=user_config.osm_network.osm_pbf_file_path
        )
        network.convert_network_to_gdf()

        # TODO: do better dev flag
        if ROOPE_DEVELOPMENT:
            dev_gdf = network.get_network_gdf().iloc[:5]
            network.set_network_gdf(dev_gdf)

        network.handle_crs(user_config)
        network.handle_invalid_geometries()
        network.network_filter_by_columns(NETWORK_COLUMNS_TO_KEEP)
        # also check the buffer geoms for invalid geometries
        network.handle_invalid_geometries()
        network.rename_column("id", "osm_id")
        network_gdf = network.get_network_gdf()
        network_gdf.to_file(NETWORK_GPKG_CACHE_PATH, driver="GPKG")

    return network
