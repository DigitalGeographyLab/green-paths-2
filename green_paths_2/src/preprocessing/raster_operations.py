""" Raster processing module. """

import os
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_origin

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


def aggregate_values(values, method="mean") -> float:
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
    if len(values) == 0 or np.all(np.isnan(values)):
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


def calculate_segment_raster_values_from_raster_file(
    network_gdf: gpd.GeoDataFrame, raster_file_path: str
) -> dict:
    segment_raster_values = {}
    with rasterio.open(raster_file_path) as src:
        raster_data = src.read(1)  # Assuming you're interested in the first band
        transform = src.transform

        for _, row in network_gdf.iterrows():
            values = [
                get_raster_value_at_point(pt, raster_data, transform)
                for pt in row[
                    "sampling_points"
                ]  # Ensure this is correctly set in your GDF
            ]

            # Here, implement your logic as before to aggregate and process these values...
            value_for_segment = aggregate_values(values, method="mean")  # Example

            if not np.isnan(value_for_segment):
                osm_id = row["osm_id"]  # Adjust based on your GDF structure
                segment_raster_values[osm_id] = round(
                    value_for_segment, 2
                )  # Example rounding

    return segment_raster_values


# from greenpaths 1
# TODO: mieti miten tän vois tehdä joustavasti

# kato kaikki kommentit ja koodi ja nimeämiset ja folderit jne!

# pitää ehkä tehä joku folder "custom_functions" tai jotain mis voi tehä tän
# vois kans ehk kokeilla jotain random rasteria missä ei tarvii tehdä mitään transformei jne...
# et toimii muillakin rastereilla
# ehkä confeihin joku "use_custom_function" ja siihen nää?


# from logging import Logger
# from typing import Union
# import zipfile

# TODO is this rioxarray needed?
import rioxarray
import xarray
import rasterio
import numpy as np

# from rasterio import fill


def convert_aq_nc_to_tif(dir: str, aqi_nc_name: str) -> str:
    """Converts a netCDF file to a georeferenced raster file. xarray and rioxarray automatically
    scale and offset each netCDF file opened with proper values from the file itself. No manual
    scaling or adding offset required. CRS of the exported GeoTiff is set to WGS84.

    Args:
        aqi_nc_name: The filename of an nc file to be processed (in aqi_cache directory).
            e.g. allPollutants_2019-09-11T15.nc
    Returns:
        The name of the exported tif file (e.g. aqi_2019-11-08T14.tif).
    """
    # read .nc file containing the AQI layer as a multidimensional array
    data = xarray.open_dataset(dir + aqi_nc_name)

    # retrieve AQI, AQI.data has shape (time, lat, lon)
    # the values are automatically scaled and offset AQI values
    aqi = data["AQI"]

    # save AQI to raster (.tif geotiff file recommended)
    aqi = aqi.rio.set_crs("epsg:4326")

    # parse date & time from nc filename and export raster
    aqi_date_str = aqi_nc_name[:-3][-13:]
    aqi_tif_name = f"aqi_{aqi_date_str}.tif"
    aqi.rio.to_raster(rf"{dir}{aqi_tif_name}")
    return aqi_tif_name


def _has_unscaled_aqi(aqi_raster) -> bool:
    d_type = aqi_raster.dtypes[0]
    return d_type == "int8"


def _get_scale(aqi_raster) -> float:
    return aqi_raster.scales[0]


def _get_offset(aqi_raster) -> float:
    return aqi_raster.offsets[0]


def fix_aqi_tiff_scale_offset(aqi_filepath: str) -> bool:
    aqi_raster = rasterio.open(aqi_filepath)
    aqi_band = aqi_raster.read(1)

    if not _has_unscaled_aqi(aqi_raster):
        return False

    scale = _get_scale(aqi_raster)
    offset = _get_offset(aqi_raster)

    aqi_band = aqi_band * scale + offset

    # TODO roope -> tää salee on jo se save? eikö?
    aqi_raster_fillna = rasterio.open(
        aqi_filepath,
        "w",
        driver="GTiff",
        height=aqi_raster.shape[0],
        width=aqi_raster.shape[1],
        count=1,
        dtype="float32",
        transform=aqi_raster.transform,
        crs=aqi_raster.crs,
    )

    aqi_raster_fillna.write(aqi_band, 1)
    aqi_raster_fillna.close()
    return True
