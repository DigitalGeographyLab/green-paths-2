""" General data utilities for managing data. """

import os
import geopandas as gpd
import pandas as pd

from shapely.geometry import LineString

from .config import (
    DATA_CACHE_DIR_PATH,
    OSM_CACHE_DIR_NAME,
    OSM_CACHE_SEGMENTED_DIR_NAME,
    OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION,
    TEST_DATA_CACHE_DIR_PATH,
)
from .green_paths_exceptions import DataManagingError
from .logging import setup_logger, LoggerColors
from .timer import time_logger

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
    raster_extensions = [".tif", ".tiff", ".dem", ".dtm", ".nc"]
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


@time_logger
def convert_gdf_to_dict(
    target_gdf: gpd.GeoDataFrame | pd.DataFrame,
    set_index_column: str = None,
    orient: str = "dict",
):
    """
    Convert GeoDataFrame to dictionary.

    Parameters:
    - gdf: GeoDataFrame to convert to dictionary.

    Returns:
    - Dictionary containing the GeoDataFrame data.
    """
    if set_index_column and set_index_column in target_gdf.columns:
        target_gdf.set_index(set_index_column, inplace=True)
    return target_gdf.to_dict(orient=orient)


def construct_osm_segmented_network_name(osm_source_path: str) -> str:
    """Constructs the name for the segmented OSM network file."""
    # Normalize input path to avoid mix of path separators
    osm_source_path = osm_source_path.replace("\\", os.sep).replace("/", os.sep)

    network_name_no_extension = os.path.basename(osm_source_path).rsplit(".osm.pbf", 1)[
        0
    ]
    osm_file_name = (
        network_name_no_extension + OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION
    )

    # check if is dev env or test env from os.environ
    if os.getenv("ENV") == "TEST":
        data_cache_dir_path = TEST_DATA_CACHE_DIR_PATH.replace("\\", os.sep).replace(
            "/", os.sep
        )

    else:
        data_cache_dir_path = DATA_CACHE_DIR_PATH.replace("\\", os.sep).replace(
            "/", os.sep
        )

    return os.path.join(
        data_cache_dir_path,
        OSM_CACHE_DIR_NAME,
        OSM_CACHE_SEGMENTED_DIR_NAME,
        osm_file_name,
    )


def list_to_string(lst) -> list[str]:
    """
    Convert list to string.

    Parameters:
    - lst: List to convert to string.

    Returns:
    - String of the list elements separated by a semicolon.

    """
    return ",".join(map(str, lst)) if lst and isinstance(lst, list) else None


def string_to_list(string: str) -> list[str]:
    """
    Convert string to list.

    Parameters:
    - string: String to convert to list.

    Returns:
    - List of the string elements separated by a semicolon.
    """
    # Strip square brackets and split the string into a list
    list_from_string = string.strip("[]").split(",")
    return [elem for elem in list_from_string]


def combine_multilinestrings(multi_lines) -> LineString:
    """
    Combine MultiLineStrings to LineString.

    Parameters:
    ----------------
    - multi_lines: List of MultiLineStrings.

    Returns:
    ----------------
    - LineString.

    """
    combined_coords = []
    for multi_line in multi_lines:
        for line in multi_line.geoms:
            combined_coords.extend(line.coords)
    return LineString(combined_coords)
