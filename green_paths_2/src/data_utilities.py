""" TODO """

import os
import geopandas as gpd

from green_paths_2.src.config import (
    DATA_CACHE_DIR_PATH,
    OSM_CACHE_DIR_NAME,
    OSM_CACHE_SEGMENTED_DIR_NAME,
    OSM_ID_DEFAULT_KEY,
    OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION,
    SEGMENT_STORE_GDF_CACHE_PATH,
)
from green_paths_2.src.logging import setup_logger, LoggerColors

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
                column
                for column in target_gdf.columns
                if column not in existing_columns
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


def _get_exposure_data_from_cache_as_gdf() -> gpd.GeoDataFrame:
    """
    Get exposure data from cache. Read .gpkg file from data/cache directory.
    """
    try:
        exposure_gdf = gpd.read_file(SEGMENT_STORE_GDF_CACHE_PATH)
        # index the gdf with osm_id
        exposure_gdf.set_index(OSM_ID_DEFAULT_KEY, inplace=True)
        return exposure_gdf
    except:
        LOG.error("Failed to read exposure data from cache.")
        return {}


def get_exposure_data_dict(data_source_names: list[str]) -> dict:
    """
    Convert exposure data to dictionary, drop geometry.
    """
    exposure_data_gdf = _get_exposure_data_from_cache_as_gdf()
    # keep only data_source_names columns
    exposure_data_gdf = filter_gdf_by_columns_if_found(
        exposure_data_gdf, data_source_names, keep=True
    )
    return exposure_data_gdf.to_dict(orient="dict")


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
