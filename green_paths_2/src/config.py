""" General configurations for Green Paths 2 project """

import os
import numpy as np

# GREEN PATSH 2 PATCHED R5 JAR FILE PATH
# R5_JAR_FILE_PATH = "https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-1/r5-v7.1-gp2-2-gd8134d8-all.jar"

# TODO: roope testaa
R5_JAR_FILE_PATH = (
    "/Users/hcroope/omat/r5_dgl/r5/build/libs/r5-v7.1-gp2-1.dirty-all.jar"
)

JAVA_PATH = "/Users/hcroope/miniconda3/envs/r5py_Gp2/lib/jvm"

GENERAL_ID_DEFAULT_KEY = "id"
OSM_ID_DEFAULT_KEY = "osm_id"

OSM_IDS_DEFAULT_KEY = "osm_ids"


SUPPORTED_DATA_TYPES = ["point", "line", "polygon", "raster"]
SUPPORTED_FILE_FORMATS = [
    "gpkg",
    "gml",
]  # "shp", "csv", "json", "geojson", "tif", "tiff"

NETWORK_COLUMNS_TO_KEEP = ["osm_id", "geometry"]

# cache dir for programatically downloadable data
DATA_CACHE_DIR_PATH: str = "green_paths_2/src/cache"


# GP2 PIPELINE CACHE DIR NAMES

PREPROCESSING_CACHE_DIR_NAME: str = "preprocessing"
ROUTING_CACHE_DIR_NAME: str = "routing"
EXPOSURE_ANALYSING_CACHE_DIR_NAME: str = "exposure_analysing"

SEGMENT_STORE_GPKG_FILE_NAME: str = "segment_store.gpkg"

OSM_NETWORK_GPKG_FILE_NAME: str = "osm_network.gpkg"

ROUTING_RESULTS_GPKG_FILE_NAME: str = "routing_results.gpkg"

ROUTING_RESULTS_CSV_FILE_NAME: str = "routing_results.csv"

TRAVEL_TIMES_CSV_FILE_NAME: str = "travel_times.csv"

OSM_CACHE_DIR_NAME: str = "osm"

OSM_CACHE_SEGMENTED_DIR_NAME: str = "segmented"

OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION: str = "_segmented.osm.pbf"

# DESCRIPTOR FILENAME
DESCRIPTOR_FILE_NAME = "data_description.txt"

# DATA CACHE DIR NAME
DATA_DIR_NAME = "data"

RASTER_DIR_NAME = "raster"

LOGS_DIR_NAME = "logs"

# RASTER FILE NAMES

RASTER_FILE_SUFFIX = ".tif"

REPROJECTED_RASTER_FILE_SUFFIX = "_reprojected.tif"

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

SEGMENT_VALUES_ROUND_DECIMALS = 3

SEGMENT_SAMPLING_POINTS_KEY = "sampling_points"


# default values for optional user configuration attributes
# these will be used if the user does not specify them in the configuration file
DEFAULT_CONFIGURATION_VALUES = {
    "segment_sampling_points_amount": 3,
    "raster_cell_resolution": 10,
    "save_raster_file": False,
}

# SEGMENT STORE CACHE PATH
SEGMENT_STORE_GDF_CACHE_PATH = os.path.join(
    DATA_CACHE_DIR_PATH,
    PREPROCESSING_CACHE_DIR_NAME,
    SEGMENT_STORE_GPKG_FILE_NAME,
)

# OSM NETWORK GEOMETRY LENGHTS CACHE PATH
OSM_NETWORK_GDF_CACHE_PATH = os.path.join(
    DATA_CACHE_DIR_PATH,
    PREPROCESSING_CACHE_DIR_NAME,
    OSM_NETWORK_GPKG_FILE_NAME,
)

CACHE_ROUTING_RESULTS_PATH = os.path.join(DATA_CACHE_DIR_PATH, ROUTING_CACHE_DIR_NAME)

# ROUTING CACHE PATH
ROUTING_RESULTS_GDF_CACHE_PATH = os.path.join(
    CACHE_ROUTING_RESULTS_PATH,
    ROUTING_RESULTS_GPKG_FILE_NAME,
)

ROUTING_RESULTS_CSV_CACHE_PATH = os.path.join(
    CACHE_ROUTING_RESULTS_PATH, ROUTING_RESULTS_CSV_FILE_NAME
)

TRAVEL_TIMES_CSV_CACHE_PATH = os.path.join(
    CACHE_ROUTING_RESULTS_PATH, TRAVEL_TIMES_CSV_FILE_NAME
)


# NORMALIZED DATA SUFFIX
NORMALIZED_DATA_SUFFIX = "_normalized"

# DEFAULT VALUE FOR CUSTOM COST TRANSPORT NETWORK'S ALLOW MISSING DATA (OSMIDS)
ALLOW_MISSING_DATA_DEFAULT = True
