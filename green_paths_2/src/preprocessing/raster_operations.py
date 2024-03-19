""" Raster processing module. """

import os
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin
from shapely.geometry import box

import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject

from green_paths_2.src.config import (
    OSM_ID_DEFAULT_KEY,
    OUTPUT_RASTER_DIR_PATH,
    RASTER_NO_DATA_VALUE,
    SEGMENT_POINTS_DEFAULT_SAMPLING_STRATEGY,
    SEGMENT_SAMPLING_POINTS_KEY,
    SEGMENT_VALUES_ROUND_DECIMALS,
)


from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.PURPLE.value)


def calculate_raster_dimensions(
    vector_data_gdf: gpd.GeoDataFrame,
    raster_cell_resolution: int,
) -> tuple[int, int, rasterio.transform.Affine]:
    """
    Calculate raster dimensions based on the vector data.

    Parameters:
    - vector_data_gdf: The GeoDataFrame containing the vector data.
    - raster_cell_resolution: The resolution of the raster cells in meters.

    Returns:
    - width: Width of the raster.
    - height: Height of the raster.
    - transform: Affine transformation for the raster.
    """
    bounds = vector_data_gdf.total_bounds
    width = int((bounds[2] - bounds[0]) / raster_cell_resolution)
    height = int((bounds[3] - bounds[1]) / raster_cell_resolution)
    transform = from_origin(
        bounds[0], bounds[3], raster_cell_resolution, raster_cell_resolution
    )
    return width, height, transform


def rasterize_vector_data(
    vector_data_gdf: gpd.GeoDataFrame,
    width: int,
    height: int,
    transform,
    data_column: str,
    nodata_value: int,  # TODO: ?
) -> rasterio.io.DatasetWriter:
    """Rasterize vector data by using the maximum value for each pixel."""
    vector_data_gdf = vector_data_gdf.sort_values(by=data_column, ascending=True)

    # use rasterio for rasterization
    raster = rasterize(
        (
            (geom, value)
            for geom, value in zip(
                vector_data_gdf.geometry, vector_data_gdf[data_column]
            )
        ),
        out_shape=(height, width),
        transform=transform,
        fill=nodata_value,  # Use a no-data value for areas that are not covered by any polygon
        all_touched=True,  # Consider all pixels that touch a geometry
        dtype="float32",
    )
    return raster


def save_to_raster_file(
    raster, output_path, transform, width, height, crs, nodata, dtype="float32"
):
    """
    Saves a numpy array as a raster file.

    Parameters:
    - raster: The numpy array to save.
    - output_path: Path to the output raster file.
    - transform: Affine transform for the raster.
    - width: Width of the raster.
    - height: Height of the raster.
    - crs: Coordinate reference system of the raster.
    - dtype: Data type of the raster. Default is 'float32'.
    - nodata: No data value for the raster. Default is None.
    """
    LOG.info(f"Saving raster to {output_path}")
    raster_meta = {
        "driver": "GTiff",
        "dtype": dtype,
        "nodata": nodata,
        "width": width,
        "height": height,
        "count": 1,
        "crs": crs,
        "transform": transform,
    }

    with rasterio.open(output_path, "w", **raster_meta) as dst:
        # Write to first band
        dst.write(raster, 1)


def rasterize_and_calculate_segment_values(
    data_name: str,
    vector_data_gdf: gpd.GeoDataFrame,
    network_gdf: gpd.GeoDataFrame,
    data_column: str,
    raster_cell_resolution: int,
    save_raster_file: bool = False,
) -> dict[int, float]:
    """
    Rasterize vector data and save it to a raster file.

    Parameters:
    - vector_data_gdf: The GeoDataFrame containing the vector data.
    - data_column: The name of the column containing the values to rasterize.
    - raster_cell_resolution: The resolution of the raster cells in meters.
    - save_raster_file: Whether to save the raster to a file. Default is False.

    Returns:
    - A dictionary containing the raster value for each road segment.
    """
    LOG.info(f"Rasterizing vector data: {data_name}")
    # Calculate raster dimensions and transformation
    width, height, transform = calculate_raster_dimensions(
        vector_data_gdf, raster_cell_resolution
    )

    # Rasterize the vector data
    raster = rasterize_vector_data(
        vector_data_gdf=vector_data_gdf,
        width=width,
        height=height,
        transform=transform,
        data_column=data_column,
        nodata_value=RASTER_NO_DATA_VALUE,
    )

    output_raster_path = os.path.join(OUTPUT_RASTER_DIR_PATH, data_name + "-raster.tif")

    raster_segment_values = calculate_segment_raster_values(
        network_gdf, raster, transform
    )

    # Save the raster to a new file if so configured
    if save_raster_file:
        # Save the raster to a new file
        save_to_raster_file(
            raster,
            output_raster_path,
            transform,
            width,
            height,
            vector_data_gdf.crs,
            nodata=RASTER_NO_DATA_VALUE,
        )

    return raster_segment_values


def get_raster_value_at_point(point, raster_data, transform):
    """Get the raster value at a given point."""
    # edit: changed from row, col to col, row -> fix working?
    col, row = ~transform * (
        point.x,
        point.y,
    )  # Transform point coordinates to raster indices
    row, col = int(row), int(col)  # Convert to integer indices
    # Check if indices are within the raster dimensions
    if 0 <= row < raster_data.shape[0] and 0 <= col < raster_data.shape[1]:
        return raster_data[row, col]
    else:
        return None  # or np.nan, or another value indicating no data


def aggregate_values(values: list[float | None], method="mean") -> float:
    """
    Aggregate values based on the given method.
    If all values are np.nan, the function returns np.nan.
    Uses np.nan[mean | max | min] to ignore np.nan values in calculations.

    Parameters:
    - values: A list of values to aggregate.
    - method: The aggregation method to use. Options are 'mean', 'max', and 'min'.

    Returns:
    - The aggregated value | np.nan.
    """
    values = np.array(values, dtype=float)
    if len(values) == 0 or np.all(np.isnan(values)) or all(v is None for v in values):
        return np.nan
    if method == "mean":
        return np.nanmean(values)
    elif method == "max":
        return np.nanmax(values)
    elif method == "min":
        return np.nanmin(values)


def calculate_segment_raster_values(
    network_gdf: gpd.GeoDataFrame, raster_data, transform
) -> dict:
    """
    Calculate raster values for each road segment.

    Parameters:
    - network_gdf: The GeoDataFrame containing the road network data.
    - raster_data: The raster data.
    - transform: Affine transformation for the raster.

    Returns:
    - A dictionary containing the raster values for each road segment.

    """
    # Loop over road segments and their sample points
    segment_raster_values: dict = {}
    for _, row in network_gdf.iterrows():
        # Extract raster values for each sample point
        values = [
            get_raster_value_at_point(pt, raster_data, transform)
            for pt in row[SEGMENT_SAMPLING_POINTS_KEY]
        ]

        # Aggregate the values for the segment
        # round to 2 decimals
        value_for_segment = aggregate_values(
            values, method=SEGMENT_POINTS_DEFAULT_SAMPLING_STRATEGY
        )

        # do not store nan values
        # this most likely means that the segment is outside of the raster
        # or no raster data was found for any of the segment sample points
        if value_for_segment is np.nan:
            continue

        osm_id = row[OSM_ID_DEFAULT_KEY]

        # round and store value
        segment_raster_values[osm_id] = round(
            value_for_segment, SEGMENT_VALUES_ROUND_DECIMALS
        )
        # Store or use the aggregated value as needed
    return segment_raster_values


def check_raster_file_crs(raster_filepath: str):
    """Check if the raster CRS is the same as the project CRS."""
    with rasterio.open(raster_filepath) as raster_src:
        return raster_src.crs


def reproject_raster_to_crs(
    input_raster_filepath: str,
    output_raster_filepath: str,
    target_crs: str,
    new_raster_resolution: int = None,
) -> None:
    """
    Reproject a raster to the target CRS.

    Parameters:
    - input_raster_filepath: The path to the input raster file.
    - output_raster_filepath: The path to the output raster file.
    - target_crs: The target CRS.
    """
    try:
        with rasterio.open(input_raster_filepath) as src:
            # if new raster resolution is defined use it, otherwise use the original resolution
            # this slows down the process a little bit
            if new_raster_resolution:
                transform, width, height = calculate_default_transform(
                    src.crs,
                    target_crs,
                    src.width,
                    src.height,
                    *src.bounds,
                    resolution=new_raster_resolution,
                )
            else:
                transform, width, height = calculate_default_transform(
                    src.crs, target_crs, src.width, src.height, *src.bounds
                )
            kwargs = src.meta.copy()
            kwargs.update(
                {
                    "crs": target_crs,
                    "transform": transform,
                    "width": width,
                    "height": height,
                }
            )

            with rasterio.open(output_raster_filepath, "w", **kwargs) as dst:
                # reproject first band
                reproject(
                    source=rasterio.band(src, 1),
                    destination=rasterio.band(dst, 1),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest,
                )
    except Exception as e:
        raise ValueError(f"Error in reprojecting raster: {e}")


# TODO: test -> gpt4 created
def calculate_segment_raster_values_from_raster_file(
    network_gdf: gpd.GeoDataFrame, raster_file_path: str
) -> dict:
    """
    Calculate raster values for each road segment from a raster file.

    Parameters:
    - network_gdf: The GeoDataFrame containing the road network data.
    - raster_file_path: The path to the raster file.

    Returns:
    - A dictionary containing the raster values for each road segment.
    """
    with rasterio.open(raster_file_path) as raster_src:
        return calculate_segment_raster_values(
            network_gdf, raster_src.read(1), raster_src.transform
        )


# from greenpaths 1
# TODO:
# kato kaikki kommentit ja koodi ja nimeämiset ja folderit jne!
# folderi custom functions? Testaa muillakin rastereil mihin ei tarvi tehdä custom processingii


def describe_raster_data(filepath: str) -> tuple[float, float, int]:
    """
    Describe the raster data.

    Parameters:
    - filepath: Path to the raster file.

    Returns:
    - min_value: Minimum value in the raster.
    - max_value: Maximum value in the raster.
    - count: Count of non-NaN values in the raster.
    """
    with rasterio.open(filepath) as src:
        # read only 1st band
        array = src.read(1)
        crs = src.crs
        min_value = array.min()
        max_value = array.max()
        # count non-nan values
        non_nan_count = np.count_nonzero(~np.isnan(array))
        # count nan-values
        nan_count = np.count_nonzero(np.isnan(array))
    return crs, min_value, max_value, non_nan_count, nan_count
