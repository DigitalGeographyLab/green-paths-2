""" Main module for preprocessing. """

import os
import gc
import geopandas as gpd

from src.preprocessing.vector_processor import process_vector_data
from src.preprocessing.user_data_handler import UserDataHandler
from src.preprocessing.raster_processor import get_raster_stats
from src.logging import setup_logger, LoggerColors
from src.config import (
    BUFFERED_NETWORK_GPKG_CACHE_PATH,
    DEFAULT_OSM_NETWORK_BUFFER_NAME,
    NETWORK_COLUMNS_TO_KEEP,
    USER_CONFIG_PATH,
)
from src.preprocessing.data_types import DataTypes
from src.preprocessing.osm_network_handler import OsmNetworkHandler
from src.preprocessing.preprocessing_exceptions import ConfigDataError
from src.preprocessing.user_config_parser import UserConfig

LOG = setup_logger(__name__, LoggerColors.GREEN.value)

# todo -> Dask this, or some parts that are similar e.g. the whole DS processing!!! ??


# TODO: -> poista testi kun haluut testaa kaikella

ROOPE_DEVELOPMENT = True

# TODO: -> move all these methods to a better place!!!


def parse_config(config_path: str) -> UserConfig:
    """
    Get and parse user configuration file.

    :param config_path: Path to the configuration file.
    :return: User configurations.
    """
    user_config = UserConfig()
    user_config.parse_config(config_path)
    return user_config


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

    if use_network_cache and os.path.exists(BUFFERED_NETWORK_GPKG_CACHE_PATH):
        # roope -> pitää muokata et on vaan se 1 geometry!!!
        LOG.info("Loading buffered network from cache")
        network = OsmNetworkHandler()
        cached_gpd = gpd.read_file(BUFFERED_NETWORK_GPKG_CACHE_PATH)
        network.set_network_gdf(cached_gpd)
    else:
        LOG.info(
            "Buffered network not found in cache, building new and saving to cache"
        )

        network = OsmNetworkHandler(
            osm_pbf_file=user_config.osm_network.osm_pbf_file_path
        )
        network.convert_network_to_gdf()

        if ROOPE_DEVELOPMENT:
            # ota sata ekeaa rivii vaan
            dev_gdf = network.get_network_gdf().iloc[:10]
            network.set_network_gdf(dev_gdf)

        network.handle_crs(user_config)
        network.handle_invalid_geometries()

        # TODO: -> siirrä nää netrokiin eri metodeihin

        # TODO: -> onko hyvä et on tällee katotaan pitääkö buffer?
        if user_config.osm_network.network_buffer > 0:
            network.create_buffer_for_geometries(user_config.osm_network.network_buffer)

        # Convert 'geometry' column to WKT

        # TODO: -> transfer gdf geom to" new column name
        # this is obsolete if not needing to save to a gpkg
        # wkt_geometry_column_name = network.convert_gdf_geometry_to_wkt(
        #     current_column_name="geometry",
        #     target_column_name="original_geometry_wkt",
        # )

        # TODO: -> mieti tän logiikka onks järkevä noin vaa plussailla?
        network.network_filter_by_columns(NETWORK_COLUMNS_TO_KEEP)

        # Set 'buffer' as the active geometry column
        # TODO: -> mieti toi bufferin hakeminen ja mitä käytetään jne...
        # vai voiko tässä vaa olla tää buffer_column_names[0]?
        network.set_geometry_column(DEFAULT_OSM_NETWORK_BUFFER_NAME)
        # also check the buffer geoms for invalid geometries
        network.handle_invalid_geometries()
        network.rename_column("id", "osm_id")

        network_gdf = network.get_network_gdf()

        LOG.info(network_gdf)
        LOG.info(network_gdf.columns)

        network_gdf = network_gdf.drop("geometry", axis=1)
        network_gdf.to_file(BUFFERED_NETWORK_GPKG_CACHE_PATH, driver="GPKG")

    return network


# TODO:, rename
def main(use_network_cache: bool = False):
    try:
        LOG.info("Starting preprocessing")
        # parse and validate user configurations
        user_config = parse_config(USER_CONFIG_PATH)
        network = process_osm_network(use_network_cache, user_config)

        # use the same network for all data sources

        data_handler = UserDataHandler()
        data_handler.populate_data_sources(data_sources=user_config.data_sources)
        osm_network_gdf: gpd.GeoDataFrame = network.get_network_gdf()

        # kaikki tää tulis lopuks siirtää esim vector handlerii? -> tms jonnekki muualle!
        # mainissa tulis olla vaan kutsuja luokkiin ja metodeihin ei itsessään mitään logiikkaa
        # !!!

        for data_name, data_source in data_handler.data_sources.items():
            LOG.info(f"processing datasource: {data_name} ({data_source.data_type})")

            if data_source.data_type == DataTypes.Vector.value:
                LOG.info(f"found vector data source")
                # TODO: -> laita flagi käytetäänkö buffer vai ei?
                process_vector_data(
                    data_name, data_source, osm_network_gdf, user_config
                )
                # result_dask_gdf = DaskGenerator.dask_operation_generator(
                #     main_gdf,
                #     lambda df: SpatialAnalysis.overlay_analysis(
                #         network_gdf_buffered, "data?"
                #     ),
                # )

                # TODO: -> täs pitää varmaa kattoo confeista onko piste, viiva vai polygon?
                # nyt mee vaa polygon...
                # if point jne...

                # mean_values = df.groupby('osm_id')['your_column_name'].mean()

            elif data_source.data_type == DataTypes.Raster.value:
                # TODO: -> tähän tää raster versio miten lasketaan juttuja...
                # result_dask_gdf = DaskGenerator.dask_operation_generator(
                #     main_gdf,
                #     lambda df: SpatialAnalysis.overlay_analysis(
                #         network_gdf_buffered, "data?"
                #     ),
                # )

                get_raster_stats(osm_network_gdf, data_source.filepath)

                # Merge these new values into the main GeoDataFrame
                # This assumes computed_new_values has an 'OSM_ID' column for merging
                pass
            else:
                raise ConfigDataError(
                    f"Unsupported data type provided in config: {data_source.data_type}"
                )

            print(data_source)
            LOG.info("Preprocessing working so far roope")
            # delete current data and free memory
            del data_source
            gc.collect()

    except ConfigDataError as e:
        LOG.error(f"Config error occurred: {e}")
