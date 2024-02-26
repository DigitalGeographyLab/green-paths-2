""" File for adding custom processing functions to the pipeline. Should be used with custom_processing yaml configuration parameter. """

import os
import rioxarray
import xarray
import rasterio
import numpy as np

from green_paths_2.src.config import (
    AQI_DATA_CACHE_DIR_PATH,
    RASTER_NO_DATA_VALUE,
)


# TODO add checking if function exists in globals


def validate_function_in_globals(custom_function_name: str) -> bool:
    """Check if the function exists in globals."""
    return custom_function_name in globals()


def apply_custom_processing_function(
    data_source: dict = None, project_crs: str | int = None
) -> str:
    """
    General function to apply custom processing to the data source.

    Parameters:
    - data_source: The data source dictionary.
    - project_crs: The CRS of the project.

    Returns:
    - The filepath of the processed data.
    """
    custom_function_name = data_source.get_custom_processing_function()
    # to make sure that the function exists in globals
    if not validate_function_in_globals(custom_function_name):
        raise ValueError(
            f"Custom processing function {custom_function_name} not found in globals."
        )

    # Dynamically retrieve the function from globals and call it
    # filepath is the data's source file path
    output_filepath = globals()[custom_function_name](data_source)
    return output_filepath


def convert_aq_nc_to_tif_and_scale_offset(data_source: dict) -> str:
    # TODO: name needs to be dynamical?
    aqi_tif_name = f"{data_source.get_name()}.tif"
    output_tif_filepath = os.path.join(AQI_DATA_CACHE_DIR_PATH, aqi_tif_name)
    raster_filepath = data_source.get_filepath()
    original_crs = data_source.get_original_crs()
    created_tif_filepath = convert_raster_nc_to_tif(
        raster_filepath, output_tif_filepath, original_crs
    )

    fix_aqi_tiff_scale_offset(created_tif_filepath)
    return created_tif_filepath


# CUSTOM FUNCTIONS FOR .NC RASTER CONVERSION TO TIF AND FIXING SCALE AND OFFSET


# TODO: edit docstrings etc.
def convert_raster_nc_to_tif(
    input_raster_file_path: str, output_tif_filepath: str, original_crs: str | int
) -> str:
    """
    Converts a netCDF file to a georeferenced raster file. xarray and rioxarray automatically
    scale and offset each netCDF file opened with proper values from the file itself. No manual
    scaling or adding offset required. CRS of the exported GeoTiff is set to WGS84.

    Parameters:
    - input_raster_file_path: The filename of an nc file to be processed from cache e.g. allPollutants_2019-09-11T15.nc.
    - output_tif_filepath: The name of the exported tif file (e.g. aqi_2019-11-08T14.tif).
    - original_crs: The original CRS of the raster file.

    Returns:
    - The name of the exported tif file (e.g. aqi_2019-11-08T14.tif).
    """
    try:
        # read .nc file containing the AQI layer as a multidimensional array
        data = xarray.open_dataset(input_raster_file_path)

        # retrieve AQI, AQI.data has shape (time, lat, lon)
        # the values are automatically scaled and offset AQI values
        aqi = data["AQI"]

        # save AQI to raster (.tif geotiff file recommended)
        aqi = aqi.rio.set_crs(original_crs)  # "epsg:4326"

        # parse date & time from nc filename and export raster
        # aqi_date_str = aqi_nc_name[:-3][-13:]
        # aqi_tif_name = f"aqi_{aqi_date_str}.tif"

        aqi.rio.to_raster(output_tif_filepath)

        return output_tif_filepath
    except Exception as e:
        raise ValueError(f"Error in converting AQI nc to tif: {e}")


def _has_unscaled_aqi(aqi_raster) -> bool:
    d_type = aqi_raster.dtypes[0]
    return d_type == "int8"


def _get_scale(aqi_raster) -> float:
    return aqi_raster.scales[0]


def _get_offset(aqi_raster) -> float:
    return aqi_raster.offsets[0]


# TODO: could use save_to_raster_file?
def fix_aqi_tiff_scale_offset(aqi_filepath: str) -> bool:
    try:
        # read and check the data
        with rasterio.open(aqi_filepath, "r") as aqi_raster:
            aqi_band = aqi_raster.read(1)

            if not _has_unscaled_aqi(aqi_raster):
                return False

            scale = _get_scale(aqi_raster)
            offset = _get_offset(aqi_raster)
            aqi_band_scaled = aqi_band * scale + offset

        # reopen for writing with the updated data
        with rasterio.open(
            aqi_filepath,
            "w",
            driver="GTiff",
            height=aqi_raster.height,
            width=aqi_raster.width,
            count=1,
            dtype="float32",
            crs=aqi_raster.crs,
            transform=aqi_raster.transform,
            nodata=RASTER_NO_DATA_VALUE,
        ) as aqi_raster_fillna:
            aqi_raster_fillna.write(aqi_band_scaled, 1)

        return aqi_raster.crs
    except Exception as e:
        raise ValueError(f"Error in fixing scale and offset for the AQI tif file: {e}")
