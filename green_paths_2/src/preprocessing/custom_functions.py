""" File for adding custom processing functions to the pipeline. Should be used with custom_processing yaml configuration parameter. """

import os
import rioxarray
import xarray
import rasterio
import numpy as np

from ..config import (
    AQI_DATA_CACHE_DIR_PATH,
    RASTER_NO_DATA_VALUE,
    TIF_FILE_EXTENSION,
)
from ..green_paths_exceptions import SpatialOperationError


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
    aqi_tif_name = f"{data_source.get_name()}{TIF_FILE_EXTENSION}"
    output_tif_filepath = os.path.join(AQI_DATA_CACHE_DIR_PATH, aqi_tif_name)
    raster_filepath = data_source.get_filepath()
    original_crs = data_source.get_original_crs()
    data_column = data_source.get_data_column()
    created_tif_filepath = convert_raster_nc_to_tif(
        raster_filepath, output_tif_filepath, original_crs, data_column
    )

    fix_aqi_tiff_scale_offset(created_tif_filepath)
    return created_tif_filepath


# CUSTOM FUNCTIONS FOR .NC RASTER CONVERSION TO TIF AND FIXING SCALE AND OFFSET

# TODO: if using interpolation, skip fillna...
# TODO: for some reason 1.0 is no data, i guess it's because of the modelled AQI data specs


def convert_raster_nc_to_tif(
    input_raster_file_path: str,
    output_tif_filepath: str,
    original_crs: str | int,
    data_column: str,
    fill_na_value: float = 1.0,
) -> str:
    """
    Mainly from Green Paths 1 with some modifications.
    https://github.com/DigitalGeographyLab/green-path-server


    Converts a netCDF file to a georeferenced raster file. xarray and rioxarray automatically
    scale and offset each netCDF file opened with proper values from the file itself. No manual
    scaling or adding offset required. CRS of the exported GeoTiff is set to WGS84.

    Parameters:
    ------------
    - input_raster_file_path: The filename of an nc file to be processed from cache e.g. allPollutants_2019-09-11T15.nc.
    - output_tif_filepath: The name of the exported tif file (e.g. aqi_2019-11-08T14.tif).
    - original_crs: The original CRS of the raster file.

    Returns:
    ------------
    - The name of the exported tif file (e.g. aqi_2019-11-08T14.tif).

    Raises:
    ------------
    - SpatialOperationError: If an error occurs during the conversion process.
    """
    try:
        # read .nc file containing the AQI layer as a multidimensional array
        data = xarray.open_dataset(input_raster_file_path)

        # retrieve AQI, AQI.data has shape (time, lat, lon)
        # the values are automatically scaled and offset AQI values

        aqi = data[data_column]

        # Fill NaN values with the specified fill value
        aqi_filled = aqi.fillna(fill_na_value)

        # save AQI to raster (.tif geotiff file recommended)
        aqi_filled = aqi_filled.rio.set_crs(original_crs)  # "epsg:4326"

        # parse date & time from nc filename and export raster
        # aqi_date_str = aqi_nc_name[:-3][-13:]
        # aqi_tif_name = f"aqi_{aqi_date_str}.tif"

        aqi_filled.rio.to_raster(output_tif_filepath)

        return output_tif_filepath
    except SpatialOperationError as e:
        raise SpatialOperationError(f"Error in converting AQI nc to tif: {e}")


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
    except SpatialOperationError as e:
        raise SpatialOperationError(
            f"Error in fixing scale and offset for the AQI tif file: {e}"
        )


# # TODO: do we want to interpolate?
# If not TODO: remove

# def fillna_in_raster(
# dir: str,
# aqi_tif_name: str,
# na_val: float = 1.0,
# log: Logger = None
# ) -> bool:
# """Fills nodata values in a raster by interpolating values from surrounding cells.
# Value 1.0 is considered as nodata. If no nodata is found with that value, a small offset
# will be applied, as sometimes the nodata value is slightly higher than 1.0 (assumably
# due to inaccuracy in netcdf to geotiff conversion).

# Args:
#     aqi_tif_name: The name of a raster file to be processed (in aqi_cache directory).
#     na_val: A value that represents nodata in the raster.
# """
# # open AQI band from AQI raster file
# aqi_filepath = dir + aqi_tif_name
# aqi_raster = rasterio.open(aqi_filepath)
# aqi_band = aqi_raster.read(1)

# if _has_unscaled_aqi(aqi_raster):
#     raise ValueError('AQI values are still unscaled')

# na_offsets = [0.0, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12]
# na_thresholds = [na_val + offset for offset in na_offsets]

# for na_threshold in na_thresholds:
#     nodata_count = np.sum(aqi_band <= na_threshold)
#     if log:
#         log.info(f'Nodata threshold: {na_threshold} / nodata count: {nodata_count}')
#     # check if nodata values can be mapped with the current offset
#     if nodata_count > 180000:
#         break
# if nodata_count < 180000:
#     if log:
#         log.info(f'Failed to set nodata values in the AQI tif, nodata count: {nodata_count}')

# # fill nodata in aqi_band using nodata mask
# aqi_nodata_mask = np.where(aqi_band <= na_threshold, 0, aqi_band)
# aqi_band_fillna = fill.fillnodata(aqi_band, mask=aqi_nodata_mask)

# # validate AQI values after na fill
# invalid_count = np.sum(aqi_band_fillna < 1.0)

# if invalid_count > 0:
#     if log:
#         log.warning(f'AQI band has {invalid_count} below 1.0 AQI values after na fill')

# # write raster with filled nodata
# aqi_raster_fillna = rasterio.open(
#     aqi_filepath,
#     'w',
#     driver='GTiff',
#     height=aqi_raster.shape[0],
#     width=aqi_raster.shape[1],
#     count=1,
#     dtype='float32',
#     transform=aqi_raster.transform,
#     crs=aqi_raster.crs
# )

# aqi_raster_fillna.write(aqi_band_fillna, 1)
# aqi_raster_fillna.close()

# return True
