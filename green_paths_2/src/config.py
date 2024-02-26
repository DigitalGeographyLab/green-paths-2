""" General configurations for Green Paths 2 project """

import os
import numpy as np

GENERAL_ID_DEFAULT_KEY = "id"
OSM_ID_DEFAULT_KEY = "osm_id"

SUPPORTED_DATA_TYPES = ["point", "line", "polygon", "raster"]
SUPPORTED_FILE_FORMATS = [
    "gpkg",
    "gml",
]  # "shp", "csv", "json", "geojson", "tif", "tiff"

NETWORK_COLUMNS_TO_KEEP = ["osm_id", "geometry"]

# cache dir for programatically downloadable data
DATA_CACHE_DIR_PATH: str = "green_paths_2/src/cache"

OSM_CACHE_DIR_NAME: str = "osm"

OSM_CACHE_SEGMENTED_DIR_NAME: str = "segmented"

OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION: str = "_segmented.osm.pbf"

# DATA CACHE DIR NAME
DATA_DIR_NAME = "data"

RASTER_DIR_NAME = "raster"

# TODO: are these used?

# AQI (air quality index) data source
AQI_DATA_SOURCE_NAME = "aqi.nc"

AQI_DATA_CACHE_DIR_PATH = os.path.join(DATA_CACHE_DIR_PATH, RASTER_DIR_NAME)

# path to AQI data source file
AQI_DATA_SOURCE_FILE_PATH = os.path.join(
    DATA_CACHE_DIR_PATH, DATA_DIR_NAME, AQI_DATA_SOURCE_NAME
)

# path to user configuration file which has e.g. data sources and osm network file path
USER_CONFIG_PATH = "green_paths_2/src/user/config.yaml"

GDF_BUFFERED_GEOMETRY_NAME = "buffered_geometry"

FIX_INVALID_GEOMETRIES: bool = True

# RASTER NO DATA DEFAULT VALUE
RASTER_NO_DATA_VALUE = np.nan

OUTPUT_RASTER_DIR_PATH = "green_paths_2/src/cache/raster"

RASTER_CELL_RESOLUTION_DEFAULT = 10

SAVE_RASTER_FILE_DEFAULT = False

# SAMPLING POINTS DEFAULT GDF KEY NAME

# SEGMENT POINTS SAMPLING AGGREGATE DEFAULT STRATEGY
SEGMENT_POINTS_DEFAULT_SAMPLING_STRATEGY = "mean"

# SEGMENT SAMPLE POINTS DEFAULT AMOUNT

SEGMENT_VALUES_ROUND_DECIMALS = 5

SEGMENT_SAMPLING_POINTS_KEY = "sampling_points"


# default values for optional user configuration attributes
# these will be used if the user does not specify them in the configuration file
DEFAULT_CONFIGURATION_VALUES = {
    "segment_sampling_points_amount": 3,
    "raster_cell_resolution": 10,
    "save_raster_file": False,
}
