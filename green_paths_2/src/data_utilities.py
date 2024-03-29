""" TODO """

from enum import Enum
import os
import geopandas as gpd
import pandas as pd

from green_paths_2.src.config import (
    DATA_CACHE_DIR_PATH,
    OSM_CACHE_DIR_NAME,
    OSM_CACHE_SEGMENTED_DIR_NAME,
    OSM_ID_DEFAULT_KEY,
    OSM_IDS_DEFAULT_KEY,
    OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION,
    ROUTING_RESULTS_CSV_CACHE_PATH,
    SEGMENT_STORE_GDF_CACHE_PATH,
)
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.data_types import RoutingComputers
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.CYAN.value)


def filter_gdf_by_columns_if_found(
    target_gdf, columns, keep: bool = True
) -> gpd.GeoDataFrame:
    """
    Filters GeoDataFrame by the given columns.
    Check if the columns exist in the GeoDataFrame.
    to avoid filtering by non-existing columns.
    if keeps true, keeps the parameter columns
    if keeps false drops the parameter columns.
    Default action is keep.

    Parameters:
    - target_gdf: GeoDataFrame to filter.
    - columns: List of column names to filter by.
    - keep: If True, keeps the given columns, else drops the rest.

    Returns:
    - The filtered GeoDataFrame.
    """
    existing_columns = [col for col in columns if col in target_gdf.columns]
    if keep:
        target_gdf = target_gdf[existing_columns]
    else:
        target_gdf.drop(
            # TODO: ROOPE OTIN TOST IN -> NOT POIS
            columns=[
                column for column in target_gdf.columns if column in existing_columns
            ],
            inplace=True,
        )
    return target_gdf


def rename_gdf_column(
    gdf: gpd.GeoDataFrame, old_column_name: str, new_column_name: str
) -> gpd.GeoDataFrame:
    """
    Renames the given column in the GeoDataFrame.

    Parameters:
    - gdf: The GeoDataFrame to rename the column in.
    - old_column_name: The name of the column to be renamed.
    - new_column_name: The new name for the column.

    Returns:
    - The GeoDataFrame with the renamed column.
    """
    updated_gdf = gdf.copy()
    updated_gdf.rename(columns={old_column_name: new_column_name}, inplace=True)
    return updated_gdf


def determine_file_type(file_path: str) -> str | None:
    """
    Determine DataType from file extension.
    This is not a foolproof method, but it should work for most cases.

    Parameters:
    - file_path: Path to the file as a string.

    Returns:
    - A string indicating the file type ('raster', 'vector', or 'unknown').
    """
    LOG.info(f"Determining data_type for {file_path}")
    # Common raster and vector file extensions
    # TODO: are these all supported e.g. img???
    raster_extensions = [".tif", ".tiff", ".img", ".dem", ".dtm", ".nc"]
    vector_extensions = [".shp", ".geojson", ".gpkg", ".kml", ".gml"]

    # Get the file extension
    _, ext = os.path.splitext(file_path.lower())

    # Determine file type
    if ext in raster_extensions:
        return "raster"
    elif ext in vector_extensions:
        return "vector"
    else:
        return None


def get_gpkg_from_cache_as_gdf(
    file_path: str, set_index_column: str = None
) -> gpd.GeoDataFrame:
    """
    Get exposure data from cache. Read .gpkg file from data/cache directory.
    """
    try:
        if not os.path.exists(file_path):
            LOG.error(f"Cached file not found for path: {file_path}.")
            return gpd.GeoDataFrame()

        exposure_gdf = gpd.read_file(file_path)
        # index the gdf with osm_id if found in columns
        # if not in columns, the osm_id is already the index
        if set_index_column and set_index_column in exposure_gdf.columns:
            exposure_gdf.set_index(set_index_column, inplace=True)

        return exposure_gdf
    except:
        LOG.error("Failed to read exposure data from cache.")
        return gpd.GeoDataFrame()


@time_logger
def get_and_convert_gdf_to_dict(
    path: str,
    set_index_column: str = None,
    data_source_names: list[str] = None,
    orient: str = "dict",
) -> dict:
    """
    Convert exposure data to dictionary, drop geometry.
    """
    LOG.info(f"Getting and converting GeoDataFrame to dictionary from path: {path}")
    if ".gpkg" in path:
        exposure_data_gdf = get_gpkg_from_cache_as_gdf(path, set_index_column)
    elif ".csv" in path:
        exposure_data_gdf = pd.read_csv(path)

    if exposure_data_gdf.empty:
        LOG.error("Exposure data GeoDataFrame is empty.")
        raise ValueError("Exposure data GeoDataFrame from cache is empty.")

    if data_source_names:
        # keep only data_source_names columns
        exposure_data_gdf = filter_gdf_by_columns_if_found(
            exposure_data_gdf, data_source_names, keep=True
        )

    return exposure_data_gdf.to_dict(orient=orient)


def construct_osm_segmented_network_name(osm_source_path: str) -> str:
    """Constructs the name for the segmented OSM network file."""
    network_name_no_extension = os.path.basename(osm_source_path).rsplit(".osm.pbf", 1)[
        0
    ]
    osm_file_name = (
        network_name_no_extension + OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION
    )
    return os.path.join(
        DATA_CACHE_DIR_PATH,
        OSM_CACHE_DIR_NAME,
        OSM_CACHE_SEGMENTED_DIR_NAME,
        osm_file_name,
    )


@time_logger
def save_gdf_to_cache_as_gpkg(gdf_to_save: gpd.GeoDataFrame, cache_file_path: str):
    """
    Save GeoDataFrame to cache as .gpkg file.

    Parameters:
    - gdf_to_save: GeoDataFrame to save.
    - cache_path: Path to the cache file.

    Raises:
    - Exception: If saving fails.
    """
    LOG.info(f"Saving GeoDataFrame to cache as .gpkg file.")
    try:
        if isinstance(gdf_to_save, gpd.GeoDataFrame) and not gdf_to_save.empty:
            gdf_to_save.to_file(
                cache_file_path,
                driver="GPKG",
            )
            if not os.path.exists(cache_file_path):
                LOG.error("Wasn't able to save gdf to cache.")
        elif isinstance(gdf_to_save, pd.DataFrame) and not gdf_to_save.empty:
            gdf_to_save.to_csv(cache_file_path, index=False)
    except Exception as e:
        LOG.error(f"Failed to save GeoDataFrame to cache. Error: {e}")
        raise e


def prepare_gdf_for_saving(
    gdf: gpd.GeoDataFrame, routing_computer: str
) -> gpd.GeoDataFrame:
    """
    Prepare GeoDataFrame for saving.

    """
    LOG.info("Preparing GeoDataFrame for saving.")
    # convert osm_ids list to string

    if routing_computer == RoutingComputers.Detailed.value:
        if "osm_ids" in gdf.columns:
            gdf[OSM_IDS_DEFAULT_KEY] = gdf[OSM_IDS_DEFAULT_KEY].apply(list_to_string)
        filter_columns = [
            "from_id",
            "to_id",
            "distance",
            "geometry",
            "osm_ids",
        ]
        gdf = filter_gdf_by_columns_if_found(gdf, filter_columns)

    # TODO: maybe remove for -> transpor_mode can be fetched form confs
    # and travel_time is probably wrong because of custom costs...

    # # convert all non-hashable columns to string e.g. Enum and Timedelta
    # for column in gdf.columns:
    #     # Check for Enum and convert to its name value
    #     if isinstance(gdf[column].dtype, pd.CategoricalDtype):
    #         if issubclass(gdf[column].dtype.categories.dtype.type, Enum):
    #             gdf[column] = gdf[column].astype(str)
    #     elif any(isinstance(v, Enum) for v in gdf[column].dropna().unique()):
    #         gdf[column] = gdf[column].apply(
    #             lambda x: x.name if isinstance(x, Enum) else x
    #         )
    #     # Convert Timedelta to total seconds
    #     elif pd.api.types.is_timedelta64_dtype(gdf[column].dtype):
    #         gdf[column] = gdf[column].dt.total_seconds()
    return gdf


def list_to_string(lst) -> list[str]:
    """
    Convert list to string.

    Parameters:
    - lst: List to convert to string.

    Returns:
    - String of the list elements separated by a semicolon.

    """
    return ";".join(map(str, lst)) if lst and isinstance(lst, list) else None


def string_to_list(string: str) -> list[str]:
    """
    Convert string to list.

    Parameters:
    - string: String to convert to list.

    Returns:
    - List of the string elements separated by a semicolon.
    """
    # Strip square brackets and split the string into a list
    list_from_string = string.strip("[]").split(", ")
    return [elem for elem in list_from_string]


def convert_travel_times_dicts_to_gdf(actual_travel_times: list[dict]):
    """
    Convert travel times to GeoDataFrame.

    Parameters:
    - actual_travel_times: List of dictionaries containing actual travel times.

    Returns:
    - GeoDataFrame containing the actual travel times.
    """
    all_travel_times = {}
    for travel_time_data in actual_travel_times:
        _, travel_times = travel_time_data
        all_travel_times.update(travel_times)

    return pd.DataFrame(all_travel_times.items(), columns=["osm_id", "travel_time"])
