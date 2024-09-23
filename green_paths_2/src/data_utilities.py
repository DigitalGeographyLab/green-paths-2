""" General data utilities for managing data. """

import os
import geopandas as gpd
import pandas as pd

from shapely.geometry import LineString, MultiLineString

from .config import (
    DATA_CACHE_DIR_PATH,
    OSM_CACHE_DIR_NAME,
    OSM_CACHE_SEGMENTED_DIR_NAME,
    OSM_DEFAULT_FILE_EXTENSION,
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

    # Normalize input path and extract file name without extension
    osm_source_path = os.path.normpath(osm_source_path)
    network_name_no_extension = os.path.basename(osm_source_path).rsplit(".osm.pbf", 1)[
        0
    ]

    # Determine the OSM file name
    osm_file_name = (
        network_name_no_extension + OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION
        if OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION not in network_name_no_extension
        else network_name_no_extension
    ) + OSM_DEFAULT_FILE_EXTENSION

    # Determine the environment (TEST or other) and set data cache directory
    data_cache_dir_path = (
        TEST_DATA_CACHE_DIR_PATH if os.getenv("ENV") == "TEST" else DATA_CACHE_DIR_PATH
    )
    data_cache_dir_path = os.path.normpath(data_cache_dir_path)

    # Return the constructed file path
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


from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import linemerge


def append_multilinestrings(multi_lines) -> LineString:
    """
    Appends Geometries. This will not produce visually correct results
    as it will not order the segments by proximity.
    This is used for API where the geometries are not really used for visualization.

    Parameters:
    ----------------
    - multi_lines: List of MultiLineStrings.

    Returns:
    ----------------
    - LineString.

    """
    combined_coords = []
    for multi_line in multi_lines:
        if not multi_line or multi_line.is_empty:
            continue
        for line in multi_line.geoms:
            combined_coords.extend(line.coords)
    return LineString(combined_coords)


def combine_multilinestrings(multi_lines) -> LineString | MultiLineString:
    """
    Combine MultiLineStrings and LineStrings into a single LineString or MultiLineString,
    ensuring that the segments are ordered by proximity.

    Parameters:
    ----------------
    - multi_lines: List of MultiLineStrings or LineStrings.

    Returns:
    ----------------
    - A combined LineString or MultiLineString.
    """
    combined_coords = []

    # Flatten MultiLineStrings and LineStrings into a single list of LineStrings
    all_lines = []
    for geom in multi_lines:
        if isinstance(geom, MultiLineString):
            all_lines.extend(list(geom.geoms))  # Add individual LineStrings
        elif isinstance(geom, LineString):
            all_lines.append(geom)

    # Ensure lines are ordered by proximity
    ordered_lines = order_lines_by_proximity(all_lines)

    # Combine the coordinates
    for line in ordered_lines:
        combined_coords.extend(line.coords)

    # If the coordinates form a continuous path, return a LineString
    if combined_coords:
        return LineString(combined_coords)

    # If not, return a MultiLineString
    return MultiLineString(ordered_lines)


def order_lines_by_proximity(lines: list[LineString]) -> list[LineString]:
    """
    Order a list of LineStrings based on the proximity of their endpoints.

    Parameters:
    ----------------
    - lines: List of LineString geometries.

    Returns:
    ----------------
    - List of ordered LineString geometries.
    """
    if not lines:
        return []

    ordered_lines = [lines.pop(0)]  # Start with the first LineString

    while lines:
        current_line = ordered_lines[-1]
        current_end = Point(current_line.coords[-1])  # Convert tuple to Point

        closest_index = None
        closest_distance = float("inf")
        reversed_needed = False

        for i, line in enumerate(lines):
            dist_start = current_end.distance(
                Point(line.coords[0])
            )  # Compare with start of line
            dist_end = current_end.distance(
                Point(line.coords[-1])
            )  # Compare with end of line

            # Check if we need to reverse the line
            if dist_start < closest_distance:
                closest_index = i
                closest_distance = dist_start
                reversed_needed = False
            if dist_end < closest_distance:
                closest_index = i
                closest_distance = dist_end
                reversed_needed = True

        # Get the closest line and reverse it if necessary
        closest_line = lines.pop(closest_index)
        if reversed_needed:
            closest_line = LineString(list(closest_line.coords)[::-1])

        # Add the closest line to the ordered list
        ordered_lines.append(closest_line)

    return ordered_lines
