""" Main module for preprocessing. """

import gc
import geopandas as gpd
from green_paths_2.src.data_utilities import determine_file_type
from green_paths_2.src.preprocessing.spatial_operations import (
    create_buffer_for_geometries,
)

from green_paths_2.src.preprocessing.vector_processor import (
    load_and_process_vector_data,
)
from green_paths_2.src.preprocessing.user_data_handler import UserDataHandler
from green_paths_2.src.preprocessing.raster_operations import (
    rasterize_and_calculate_segment_values,
)
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.config import (
    USER_CONFIG_PATH,
)
from green_paths_2.src.preprocessing.data_types import DataTypes
from green_paths_2.src.preprocessing.osm_network_handler import OsmNetworkHandler
from green_paths_2.src.preprocessing.preprocessing_exceptions import (
    ConfigDataError,
    ConfigError,
)
from green_paths_2.src.preprocessing.user_config_parser import UserConfig

LOG = setup_logger(__name__, LoggerColors.GREEN.value)

# TODO: -> conf Dasking/multiprocess this
# TODO: -> poista testi kun haluut testaa kaikella
# TODO: -> move all methods to a better place!!!


def parse_config(config_path: str) -> UserConfig:
    """
    Get and parse user configuration file.

    :param config_path: Path to the configuration file.
    :return: UserConfig object.
    """
    user_config = UserConfig()
    user_config.parse_config(config_path)
    return user_config


# TODO: rename
def preprocessing():
    try:
        LOG.info("Starting preprocessing")
        # parse and validate user configurations
        user_config = parse_config(USER_CONFIG_PATH)
        network = OsmNetworkHandler(
            osm_pbf_file=user_config.osm_network.osm_pbf_file_path
        )
        network.process_osm_network(
            project_crs=user_config.project_crs,
            original_crs=user_config.osm_network.original_crs,
            segment_sampling_points_amount=user_config.osm_network.segment_sampling_points_amount,
        )
        # use the same network for all data sources

        data_handler = UserDataHandler()
        data_handler.populate_data_sources(data_sources=user_config.data_sources)
        osm_network_gdf: gpd.GeoDataFrame = network.get_network_gdf()

        # kaikki tää tulis lopuks siirtää esim vector handlerii? -> tms jonnekki muualle!
        # mainissa tulis olla vaan kutsuja luokkiin ja metodeihin ei itsessään mitään logiikkaa
        # !!!

        for data_name, data_source in data_handler.data_sources.items():
            data_type = data_source.get_data_type() or determine_file_type(
                data_source.get_filepath()
            )
            LOG.info(f"processing datasource: {data_name} ({data_type})")

            if data_type == DataTypes.Vector.value:
                LOG.info(f"found vector data source")

                cleaned_vector_gdf = load_and_process_vector_data(
                    data_name, data_source, user_config.project_crs
                )

                # if buffer for data is defined in config, apply it
                if data_source.get_data_buffer():
                    cleaned_vector_gdf = create_buffer_for_geometries(
                        data_name, cleaned_vector_gdf, data_source.get_data_buffer()
                    )

                rasterize_and_calculate_segment_values(
                    data_name=data_name,
                    vector_data_gdf=cleaned_vector_gdf,
                    network_gdf=osm_network_gdf,
                    data_column=data_source.get_data_column(),
                    raster_cell_resolution=data_source.get_raster_cell_resolution(),
                    save_raster_file=data_source.get_save_raster_file(),
                )

            elif data_source.data_type == DataTypes.Raster.value:
                LOG.info(f"processing datasource: {data_name} ({data_type})")

                # TODO: -> tähän tää raster versio miten lasketaan juttuja...
                # result_dask_gdf = DaskGenerator.dask_operation_generator(
                #     main_gdf,
                #     lambda df: SpatialAnalysis.overlay_analysis(
                #         network_gdf_buffered, "data?"
                #     ),
                # )

                # Merge these new values into the main GeoDataFrame
                # This assumes computed_new_values has an 'OSM_ID' column for merging
            else:
                raise ConfigError(
                    f"Unsupported data type provided in config for {data_name}!"
                )

            LOG.info("Preprocessing working so far roope")
            # delete current data and free memory
            del data_source
            gc.collect()

    except ConfigDataError as e:
        LOG.error(f"Config error occurred: {e}")

    # TODO: confeista jos datalle buffer?
    # TODO: tää varmaan tarvitaan vaan jos aiotaan tehdä jotain overlay juttuja VECTOREILLE

    # process_vector_data(
    #     data_name, data_source, osm_network_gdf, user_config
    # )
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
