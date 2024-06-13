""" Main module for preprocessing. """

import os
import gc
import geopandas as gpd
from ..data_utilities import (
    determine_file_type,
    filter_gdf_by_columns_if_found,
    save_gdf_to_cache,
)
from ..preprocessing.custom_functions import (
    apply_custom_processing_function,
)
from ..preprocessing.spatial_operations import (
    create_buffer_for_geometries,
)

from ..preprocessing.vector_processor import (
    load_and_process_vector_data,
)
from ..preprocessing.user_data_handler import UserDataHandler
from ..preprocessing.raster_operations import (
    calculate_segment_raster_values_from_raster_file,
    check_raster_file_crs,
    rasterize_and_calculate_segment_values,
    reproject_raster_to_crs,
)
from ..logging import setup_logger, LoggerColors
from ..config import (
    GEOMETRY_KEY,
    LENGTH_KEY,
    OSM_ID_KEY,
    OSM_NETWORK_CSV_CACHE_PATH,
    OSM_NETWORK_GDF_CACHE_PATH,
    RASTER_FILE_SUFFIX,
    REPROJECTED_RASTER_FILE_SUFFIX,
    SAVE_TO_CACHE_KEY,
    SEGMENT_STORE_GDF_CACHE_PATH,
)
from ..preprocessing.data_types import DataTypes
from ..green_paths_exceptions import (
    ConfigDataError,
    PipeLineRuntimeError,
)
from ..preprocessing.user_config_parser import UserConfig
from ..routing.main import routing_pipeline
from ..segment_value_store import SegmentValueStore
from ..timer import time_logger

LOG = setup_logger(__name__, LoggerColors.GREEN.value)

# TODO: -> conf Dasking/multiprocess this?


@time_logger
def preprocessing_pipeline(
    osm_network_gdf: gpd.GeoDataFrame,
    data_handler: UserDataHandler,
    user_config: UserConfig,
):
    """
    Run the whole preprocessing pipeline.

    Parameters
    ----------
    osm_network_gdf : gpd.GeoDataFrame
        OSM network data.
    user_config : UserConfig
        User configuration object.

    Returns
    -------
    gpd.GeoDataFrame
        The segment store GeoDataFrame.
    gpd.GeoDataFrame
        The OSM network GeoDataFrame.

    Raises
    ------
    PipeLineRuntimeError
        If the preprocessing pipeline fails.
    """

    LOG.info("\n\n\nStarting preprocessing pipeline\n\n\n")
    try:
        segment_store = SegmentValueStore()

        for data_name, data_source in data_handler.data_sources.items():
            data_conf_filepath = data_source.get_filepath()
            data_type = data_source.get_data_type() or determine_file_type(
                data_conf_filepath
            )

            no_data_value = data_source.get_no_data_value()

            LOG.info(f"Processing datasource: {data_name} ({data_type})")

            if data_type == DataTypes.Vector.value:
                LOG.info(f"Processing vector data source")

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
                    default_raster_null_value=no_data_value,
                )

                segment_store.save_segment_values(segment_values, data_name)

            elif data_type == DataTypes.Raster.value:
                LOG.info(f"Processing raster data source")

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
                    reprojected_raster_filepath = raster_path.replace(
                        RASTER_FILE_SUFFIX, REPROJECTED_RASTER_FILE_SUFFIX
                    )

                    reproject_raster_to_crs(
                        input_raster_filepath=raster_path,
                        output_raster_filepath=reprojected_raster_filepath,
                        target_crs=user_config.project_crs,
                        original_crs=data_source.get_original_crs(),
                        new_raster_resolution=data_source.get_raster_cell_resolution(),
                    )

                # use reprojected file if it was created or exists
                if os.path.exists(reprojected_raster_filepath):
                    raster_path = reprojected_raster_filepath

                segment_values = calculate_segment_raster_values_from_raster_file(
                    network_gdf=osm_network_gdf,
                    raster_file_path=raster_path,
                    default_raster_null_value=no_data_value,
                )

                segment_store.save_segment_values(segment_values, data_name)

        all_data_sources = data_handler.get_data_sources()

        all_osm_ids = segment_store.get_all_segment_osmids()

        if not all_osm_ids or len(all_osm_ids) == 0:
            LOG.error("no exposure data found for any segments!")
            raise ConfigDataError(
                "No data was found from the datasources for any of the segments. Check the data sources (e.g. CRS's) and try again."
            )

        segment_store.validate_data_coverage(
            all_data_sources,
            len(osm_network_gdf),
            user_config.datas_coverage_safety_percentage,
        )

        # TODO: ehkä tähän pitäis ottaa joku checki jos on tullu null arvoja teiltä?

        # check if user defined min and max values are valid
        segment_store.validate_user_min_max_values(all_data_sources)

        # save normalized values to the master segment store
        segment_store.save_normalized_values_to_store(all_data_sources)

        # TODO: remove these test prints...
        # use some osmid which is found from data
        # some_test_osmid = list(segment_store.get_all_segment_osmids())[0]
        # some_test_osmid_2 = list(segment_store.get_all_segment_osmids())[-1]
        # print(segment_store.get_segment_values(some_test_osmid))
        # print(segment_store.get_segment_values(some_test_osmid_2))

        # print("tää pitäs olla nan/FALSE")
        # print(segment_store.get_segment_values(-1000000034693))

        # combine exposures to geometries and convert the segment store to a GeoDataFrame
        segment_store.combine_exposures_to_geometries_and_lenghts(osm_network_gdf)
        segment_store.convert_segment_store_to_gdf()
        segment_store_gdf_with_exposure = segment_store.get_master_segment_gdf()

        if user_config.analysing and user_config.analysing.keep_geometry:
            columns_to_keep_from_network = [OSM_ID_KEY, GEOMETRY_KEY, LENGTH_KEY]
        else:
            columns_to_keep_from_network = [OSM_ID_KEY, LENGTH_KEY]

        filtered_osm_network_gdf = filter_gdf_by_columns_if_found(
            osm_network_gdf,
            columns_to_keep_from_network,
            keep=True,
        )

        has_save_to_cache = hasattr(user_config, SAVE_TO_CACHE_KEY)

        if has_save_to_cache and user_config.save_to_cache:
            LOG.info("Saving segment_store and osm_network to cache.")
            save_gdf_to_cache(
                segment_store_gdf_with_exposure, SEGMENT_STORE_GDF_CACHE_PATH
            )

            # check user configurations for keep geometry
            if user_config.analysing and user_config.analysing.keep_geometry:
                save_gdf_to_cache(filtered_osm_network_gdf, OSM_NETWORK_GDF_CACHE_PATH)
            else:
                # save as csv, without geometries
                save_gdf_to_cache(filtered_osm_network_gdf, OSM_NETWORK_CSV_CACHE_PATH)

        else:
            LOG.info("Not saving preprocessing results to cache.")

        LOG.info("End of preprocessing pipeline.")
        # delete current data and free memory
        del data_source
        gc.collect()
        return segment_store_gdf_with_exposure, filtered_osm_network_gdf
    except PipeLineRuntimeError as e:
        LOG.error(f"Preprocessing pipeline failed with error: {e}")
        raise e
