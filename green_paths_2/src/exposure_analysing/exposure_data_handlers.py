""" Module for handling exposure data in the exposure analysing pipeline. Has also some general utilities """

import geopandas as gpd
import pandas as pd
from green_paths_2.src.config import (
    FINAL_EXPOSURE_ANALYSING_RESULTS_CSV_PATH,
    FINAL_EXPOSURE_ANALYSING_RESULTS_GPKG_PATH,
    OSM_ID_KEY,
    OSM_NETWORK_GDF_CACHE_PATH,
    ROUTING_RESULTS_CSV_CACHE_PATH,
    ROUTING_RESULTS_GDF_CACHE_PATH,
    SEGMENT_STORE_GDF_CACHE_PATH,
)
from green_paths_2.src.data_utilities import (
    convert_gdf_to_dict,
    get_and_convert_gdf_to_dict,
    save_gdf_to_cache,
)
from green_paths_2.src.green_paths_exceptions import (
    DataManagingError,
    SpatialOperationError,
)

from shapely.geometry import MultiLineString, LineString
from shapely.ops import linemerge, unary_union
from typing import List

from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.user_config_parser import UserConfig

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def get_datas_from_sources(
    exposure_gdf,
    osm_network_gdf,
    routing_results_gdf,
    # actual_travel_times_gdf,
):
    """
    Get data from sources for analysing pipeline.

    Parameters
    ----------
    exposure_gdf : gpd.GeoDataFrame
        GeoDataFrame containing exposure data.
    osm_network_gdf : gpd.GeoDataFrame
        GeoDataFrame containing OSM network data.
    routing_results_gdf : gpd.GeoDataFrame
        GeoDataFrame containing routing results.
    actual_travel_times_gdf : gpd.GeoDataFrame
        GeoDataFrame containing actual travel times.

    Returns
    -------
    tuple
        Tuple containing routing results, segment exposure store and OSM network store.
    """
    if (
        exposure_gdf is None
        or osm_network_gdf is None
        or routing_results_gdf is None
        # or actual_travel_times_gdf is None
    ):
        LOG.info("Loading data from cache for analysing pipeline")
        routing_results, segment_exposure_store, osm_network_store = (
            _load_datas_from_cache()
        )
    else:
        LOG.info("Using parameter data for analysing pipeline")
        segment_exposure_store = convert_gdf_to_dict(exposure_gdf, OSM_ID_KEY)
        routing_results = convert_gdf_to_dict(routing_results_gdf, orient="records")
        osm_network_store = convert_gdf_to_dict(osm_network_gdf, OSM_ID_KEY)
        # actual_travel_times_store = convert_gdf_to_dict(actual_travel_times_gdf)

    return routing_results, segment_exposure_store, osm_network_store


def _load_datas_from_cache():
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
    #     TRAVEL_TIMES_CSV_CACHE_PATH, OSM_ID_KEY
    # )

    routing_results_path = ROUTING_RESULTS_CSV_CACHE_PATH

    routing_results = get_and_convert_gdf_to_dict(
        routing_results_path, OSM_ID_KEY, orient="records"
    )
    segment_exposure_store = get_and_convert_gdf_to_dict(
        SEGMENT_STORE_GDF_CACHE_PATH, OSM_ID_KEY
    )

    osm_network_store = get_and_convert_gdf_to_dict(
        OSM_NETWORK_GDF_CACHE_PATH, OSM_ID_KEY
    )

    return routing_results, segment_exposure_store, osm_network_store


def combine_multilinestrings_to_single_linestring(
    multilinestrings: List[MultiLineString],
) -> LineString:
    """
    Combine multiple MultiLineString objects into a single LineString.

    Parameters:
    ----------
    - multilinestrings: a list of MultiLineString objects to be combined.

    Returns:
    ----------
    - A single LineString object if the line segments can be merged,
      otherwise returns None.
    """
    try:
        # Use unary_union to handle both LineString and MultiLineString objects,
        # and to ensure all geometries are considered for merging.
        combined_line_geometries = unary_union(multilinestrings)

        # check if has only 1 linestring, if so return it
        if (
            isinstance(combined_line_geometries, LineString)
            and len(multilinestrings) == 1
        ):
            return combined_line_geometries

        # merge multiple LineString objects into a single LineString
        merged_line = linemerge(combined_line_geometries)

        if isinstance(merged_line, LineString):
            return merged_line
        else:
            print(
                "Warning: The geometries could not be merged into a single LineString."
            )
            return None
    except SpatialOperationError as e:
        LOG.info(f"Error occured when combining a single linestring: {e}")
        return None


# TODO: add support to GeoJson? etc.?
def save_final_results_data(
    user_config: UserConfig, combined_master_statistics_store: list[dict]
) -> gpd.GeoDataFrame:
    """
    Save the final results data to cache as gpkg or csv file.

    Parameters:
    ----------
    user_config : UserConfig
        User configuration.
    combined_master_statistics_store : list[dict]
        List of dictionaries containing the final results data, one dictionary per path.

    Returns:
    ----------
    gpd.GeoDataFrame
        The saved GeoDataFrame.

    Raises:
    ----------
    DataManagingError
        If saving fails.

    """
    LOG.info("Saving final results data to cache.")
    try:
        if user_config.analysing and user_config.analysing.keep_geometry:
            final_results_gdf = gpd.GeoDataFrame(combined_master_statistics_store)

            if final_results_gdf.empty:
                LOG.error("No analysing result data to save, gdf is empty.")
                return False

            if (
                final_results_gdf.geometry.notnull().any()
                or not final_results_gdf.crs
                or final_results_gdf.crs != f"EPSG:{user_config.project_crs}"
                or final_results_gdf.crs != user_config.project_crs
            ):
                final_results_gdf.crs = user_config.project_crs

                save_gdf_to_cache(
                    final_results_gdf,
                    FINAL_EXPOSURE_ANALYSING_RESULTS_GPKG_PATH,
                )
                LOG.info(
                    f"Successfully saved final results data to cache as .gpkg file to path: {FINAL_EXPOSURE_ANALYSING_RESULTS_GPKG_PATH}"
                )
                return final_results_gdf
        else:
            final_results_df = pd.DataFrame(combined_master_statistics_store)
            save_gdf_to_cache(
                final_results_df,
                FINAL_EXPOSURE_ANALYSING_RESULTS_CSV_PATH,
            )
            LOG.info(
                f"Successfully saved final results data to cache as .csv file to path: {FINAL_EXPOSURE_ANALYSING_RESULTS_CSV_PATH}"
            )
        return final_results_df
    except DataManagingError as e:
        LOG.info(f"Failed to save final results data to cache. Error: {e}")
        return pd.DataFrame()
