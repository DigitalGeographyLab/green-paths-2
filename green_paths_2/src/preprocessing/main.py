""" Main module for preprocessing. """

import os
import gc
import geopandas as gpd
from green_paths_2.src.data_utilities import determine_file_type
from green_paths_2.src.preprocessing.custom_functions import (
    apply_custom_processing_function,
)
from green_paths_2.src.preprocessing.osm_segmenter import (
    segment_or_use_cache_osm_network,
)
from green_paths_2.src.preprocessing.spatial_operations import (
    create_buffer_for_geometries,
)

from green_paths_2.src.preprocessing.vector_processor import (
    load_and_process_vector_data,
)
from green_paths_2.src.preprocessing.user_data_handler import UserDataHandler
from green_paths_2.src.preprocessing.raster_operations import (
    calculate_segment_raster_values_from_raster_file,
    check_raster_file_crs,
    rasterize_and_calculate_segment_values,
    reproject_raster_to_crs,
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
from green_paths_2.src.segment_value_store import SegmentValueStore
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.GREEN.value)

# TODO: -> conf Dasking/multiprocess this
# TODO: -> poista testi kun haluut testaa kaikella
# TODO: -> move all methods to a better place!!!


# def parse_config(config_path: str) -> UserConfig:
#     """
#     Get and parse user configuration file.

#     :param config_path: Path to the configuration file.
#     :return: UserConfig object.
#     """
#     user_config = UserConfig()
#     user_config.parse_config(config_path)
#     return user_config


# TODO: rename
@time_logger
def preprocessing_pipeline():
    try:
        LOG.info("Starting preprocessing")
        # parse and validate user configurations
        user_config = UserConfig(USER_CONFIG_PATH).parse_config()

        # segment OSM network or use existing segmented network from cache
        # if the name matches with the source file name
        osm_network_pbf_file_path = segment_or_use_cache_osm_network(
            user_config.osm_network.osm_pbf_file_path
        )

        network = OsmNetworkHandler(osm_pbf_file=osm_network_pbf_file_path)

        network.process_osm_network(
            project_crs=user_config.project_crs,
            original_crs=user_config.osm_network.original_crs,
            segment_sampling_points_amount=user_config.osm_network.segment_sampling_points_amount,
        )
        # use the same network for all data sources

        data_handler = UserDataHandler()
        data_handler.populate_data_sources(data_sources=user_config.data_sources)
        osm_network_gdf: gpd.GeoDataFrame = network.get_network_gdf()

        # TODO: if confs -> populate with geometries? or should this be done always?
        segment_store = SegmentValueStore()

        for data_name, data_source in data_handler.data_sources.items():
            data_conf_filepath = data_source.get_filepath()
            data_type = data_source.get_data_type() or determine_file_type(
                data_conf_filepath
            )

            LOG.info(f"Processing datasource: {data_name} ({data_type})")

            if data_type == DataTypes.Vector.value:
                LOG.info(f"Found vector data source")

                cleaned_vector_gdf = load_and_process_vector_data(
                    data_name, data_source, user_config.project_crs
                )

                # if buffer for data is defined in config, apply it
                if data_source.get_data_buffer():
                    cleaned_vector_gdf = create_buffer_for_geometries(
                        data_name, cleaned_vector_gdf, data_source.get_data_buffer()
                    )

                segment_values = rasterize_and_calculate_segment_values(
                    data_name=data_name,
                    vector_data_gdf=cleaned_vector_gdf,
                    network_gdf=osm_network_gdf,
                    data_column=data_source.get_data_column(),
                    raster_cell_resolution=data_source.get_raster_cell_resolution(),
                    save_raster_file=data_source.get_save_raster_file(),
                )

                segment_store.save_segment_values(segment_values, data_name)

            elif data_type == DataTypes.Raster.value:
                LOG.info(f"Found raster data source")

                # check for possible custom processing function
                raster_path = (
                    apply_custom_processing_function(
                        data_source,
                    )
                    if data_source.get_custom_processing_function()
                    else data_conf_filepath
                )

                # check raster crs and reproject if needed

                if check_raster_file_crs(raster_path) != user_config.project_crs:
                    LOG.info(
                        f"Raster not in project crs. Reprojecting {raster_path} to project crs: {user_config.project_crs}"
                    )
                    # TODO: confeihin
                    reprojected_filepath = raster_path.replace(
                        ".tif", "_reprojected.tif"
                    )

                    reproject_raster_to_crs(
                        input_raster_filepath=raster_path,
                        output_raster_filepath=reprojected_filepath,
                        target_crs=user_config.project_crs,
                        new_raster_resolution=data_source.get_raster_cell_resolution(),
                    )

                # use reprojected file if it was created or exists
                if os.path.exists(reprojected_filepath):
                    raster_path = reprojected_filepath

                segment_values = calculate_segment_raster_values_from_raster_file(
                    network_gdf=osm_network_gdf,
                    raster_file_path=raster_path,
                )

                segment_store.save_segment_values(segment_values, data_name)

        # -1000000034089
        # -1000000027725
        # -1000000020694

        all_data_name_keys = data_handler.get_data_source_names()
        segment_store.save_normalized_values_to_store(all_data_name_keys)

        print(segment_store.get_segment_values("-1000000018889"))

        LOG.info("End of preprocessing pipeline.")

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
