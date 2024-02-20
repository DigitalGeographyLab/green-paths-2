""" Main module for preprocessing. """

import os
import gc
import geopandas as gpd

from src.preprocessing.vector_processor import process_vector_data
from src.preprocessing.user_data_handler import UserDataHandler
from src.preprocessing.raster_processor import get_raster_stats
from src.logging import setup_logger, LoggerColors
from src.config import (
    NETWORK_COLUMNS_TO_KEEP,
    USER_CONFIG_PATH,
)
from src.preprocessing.data_types import DataTypes
from src.preprocessing.osm_network_handler import OsmNetworkHandler
from src.preprocessing.preprocessing_exceptions import ConfigDataError
from src.preprocessing.user_config_parser import UserConfig

LOG = setup_logger(__name__, LoggerColors.GREEN.value)

# TODO: -> conf Dasking/multiprocess this
# TODO: -> poista testi kun haluut testaa kaikella
# TODO: -> move all methods to a better place!!!

ROOPE_DEVELOPMENT = True


def parse_config(config_path: str) -> UserConfig:
    """
    Get and parse user configuration file.

    :param config_path: Path to the configuration file.
    :return: UserConfig object.
    """
    user_config = UserConfig()
    user_config.parse_config(config_path)
    return user_config


def process_osm_network(user_config: UserConfig = None) -> gpd.GeoDataFrame:
    """
    Process OSM network.

    :param user_config: User configurations.
    :return: GeoDataFrame of the OSM network.
    """
    LOG.info("Processing OSM network.")
    network = OsmNetworkHandler(osm_pbf_file=user_config.osm_network.osm_pbf_file_path)
    network.convert_network_to_gdf()

    if ROOPE_DEVELOPMENT:
        # ota sata ekeaa rivii vaan
        dev_gdf = network.get_network_gdf().iloc[:100]
        network.set_network_gdf(dev_gdf)

    network.handle_crs(user_config)
    network.handle_invalid_geometries()
    network.network_filter_by_columns(NETWORK_COLUMNS_TO_KEEP)
    network.handle_invalid_geometries()
    network.rename_column("id", "osm_id")
    # network_gdf = network.get_network_gdf()

    return network


# TODO: rename
def preprocessing():
    try:
        LOG.info("Starting preprocessing")
        # parse and validate user configurations
        user_config = parse_config(USER_CONFIG_PATH)
        network = process_osm_network(user_config)

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
                # TODO: -> confeista jos datalle buffer?
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
