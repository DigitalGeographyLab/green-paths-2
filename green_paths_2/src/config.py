""" General configurations for Green Paths 2 project """

import os
import numpy as np


# R5PY PATHS

# GREEN PATSH 2 PATCHED R5 JAR FILE PATH
R5_JAR_FILE_PATH = "https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-2/r5-v7.1-gp2-1-1-ga342478-all.jar"

# TODO: LOCAL FOR TESTING
# R5_JAR_FILE_PATH = (
#     "/Users/hcroope/omat/r5_dgl/r5/build/libs/r5-v7.1-gp2-2.dirty-all.jar"
# )

# TODO: LOCAL FOR TESTING
# JAVA_PATH = "/Users/hcroope/miniconda3/envs/r5py_Gp2/lib/jvm"


# DEFAULT VALUE FOR CUSTOM COST TRANSPORT NETWORK'S ALLOW MISSING DATA (OSMIDS)
ALLOW_MISSING_DATA_DEFAULT = True

# SQLITE3 DB PATH
GP2_DB_PATH = "green_paths_2/src/database/gp2.db"


# KEYS

NAME_KEY = "name"

FROM_ID_KEY = "from_id"

TO_ID_KEY = "to_id"

LENGTH_KEY = "length"

GEOMETRY_KEY = "geometry"

TRAVEL_TIME_KEY = "travel_time"

ID_KEY = "id"

OSM_ID_KEY = "osm_id"

OSM_IDS_KEY = "osm_ids"

SAVE_TO_CACHE_KEY = "save_to_cache"

RASTER_CELL_RESOLUTION_KEY = "raster_cell_resolution"

MIN_EXPOSURE_SUFFIX = "_min_exposure"

MAX_EXPOSURE_SUFFIX = "_max_exposure"

SUM_EXPOSURE_SUFFIX = "_sum_exposure"

TRAVERSAL_TIME_WEIGHTED_PATH_EXPOSURE_AVERAGE_SUFFIX = (
    "_time_weighted_path_exposure_avg"
)

TRAVERSAL_TIME_WEIGHTED_PATH_EXPOSURE_SUM_SUFFIX = "_time_weighted_path_exposure_sum"

# seconds
CUMULATIVE_EXPOSURE_TIME_METERS_SUFFIX = "_cumulative_exposure_time_meters"

# KEY LISTS

NETWORK_COLUMNS_TO_KEEP = [OSM_ID_KEY, GEOMETRY_KEY]

ORIGIN_DESTINATION_KEYS = [FROM_ID_KEY, TO_ID_KEY]


# PATHS

USER_CONFIG_PATH = "green_paths_2/src/user/config.yaml"

OUTPUT_RASTER_DIR_PATH = "green_paths_2/src/cache/raster"


# # CACHE

DATA_CACHE_DIR_PATH: str = "green_paths_2/src/cache"

PREPROCESSING_CACHE_DIR_NAME: str = "preprocessing"

ROUTING_CACHE_DIR_NAME: str = "routing"

EXPOSURE_ANALYSING_CACHE_DIR_NAME: str = "final_exposure_results"

OSM_CACHE_DIR_NAME: str = "osm"

DATA_CACHE_DIR_NAME = "data"

OSM_CACHE_SEGMENTED_DIR_NAME: str = "segmented"

RASTER_CACHE_DIR_NAME = "raster"

LOGS_CACHE_DIR_NAME = "logs"


# FILENAMES AND FILE EXTENSIONS

SEGMENT_STORE_GPKG_FILE_NAME: str = "segment_store.gpkg"

OSM_NETWORK_GPKG_FILE_NAME: str = "osm_network.gpkg"

OSM_NETWORK_CSV_FILE_NAME: str = "osm_network.csv"

ROUTING_RESULTS_CSV_FILE_NAME: str = "routing_results.csv"

TRAVEL_TIMES_CSV_FILE_NAME: str = "travel_times.csv"

OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION: str = "_segmented.osm.pbf"

DESCRIPTOR_FILE_NAME = "data_description.txt"

RASTER_FILE_SUFFIX = ".tif"

REPROJECTED_RASTER_FILE_SUFFIX = "_reprojected.tif"

AQI_DATA_SOURCE_NAME = "aqi.nc"

NORMALIZED_DATA_SUFFIX = "_normalized"

EXPOSURE_ANALYSIS_RESULTS_GPKG_NAME = "exposure_analysis_results.gpkg"

EXPOSURE_ANALYSIS_RESULTS_CSV_NAME = "exposure_analysis_results.csv"

TIF_FILE_EXTENSION = ".tif"


# COMBINATION PATHS

AQI_DATA_CACHE_DIR_PATH = os.path.join(DATA_CACHE_DIR_PATH, RASTER_CACHE_DIR_NAME)

AQI_DATA_SOURCE_FILE_PATH = os.path.join(
    DATA_CACHE_DIR_PATH, DATA_CACHE_DIR_NAME, AQI_DATA_SOURCE_NAME
)

SEGMENT_STORE_GDF_CACHE_PATH = os.path.join(
    DATA_CACHE_DIR_PATH,
    PREPROCESSING_CACHE_DIR_NAME,
    SEGMENT_STORE_GPKG_FILE_NAME,
)

OSM_NETWORK_GDF_CACHE_PATH = os.path.join(
    DATA_CACHE_DIR_PATH,
    PREPROCESSING_CACHE_DIR_NAME,
    OSM_NETWORK_GPKG_FILE_NAME,
)

OSM_NETWORK_CSV_CACHE_PATH = os.path.join(
    DATA_CACHE_DIR_PATH,
    PREPROCESSING_CACHE_DIR_NAME,
    OSM_NETWORK_CSV_FILE_NAME,
)


CACHE_ROUTING_RESULTS_PATH = os.path.join(DATA_CACHE_DIR_PATH, ROUTING_CACHE_DIR_NAME)

ROUTING_RESULTS_GDF_CACHE_PATH = os.path.join(
    CACHE_ROUTING_RESULTS_PATH,
)

ROUTING_RESULTS_CSV_CACHE_PATH = os.path.join(
    CACHE_ROUTING_RESULTS_PATH, ROUTING_RESULTS_CSV_FILE_NAME
)

TRAVEL_TIMES_CSV_CACHE_PATH = os.path.join(
    CACHE_ROUTING_RESULTS_PATH, TRAVEL_TIMES_CSV_FILE_NAME
)

FINAL_EXPOSURE_ANALYSING_RESULTS_GPKG_PATH = os.path.join(
    DATA_CACHE_DIR_PATH,
    EXPOSURE_ANALYSING_CACHE_DIR_NAME,
    EXPOSURE_ANALYSIS_RESULTS_GPKG_NAME,
)

FINAL_EXPOSURE_ANALYSING_RESULTS_CSV_PATH = os.path.join(
    DATA_CACHE_DIR_PATH,
    EXPOSURE_ANALYSING_CACHE_DIR_NAME,
    EXPOSURE_ANALYSIS_RESULTS_CSV_NAME,
)


# DEFAULT VALUES

FIX_INVALID_GEOMETRIES: bool = True

RASTER_NO_DATA_VALUE = np.nan

RASTER_CELL_RESOLUTION_DEFAULT = 10

SAVE_RASTER_FILE_DEFAULT = False

SEGMENT_POINTS_DEFAULT_SAMPLING_STRATEGY = "mean"

SEGMENT_VALUES_ROUND_DECIMALS = 3

SEGMENT_SAMPLING_POINTS_KEY = "sampling_points"

DATA_COVERAGE_SAFETY_PERCENTAGE = 33

DEFAULT_R5_TRAVEL_SPEED_WALKING = 3.6

DEFAULT_R5_TRAVEL_SPEED_CYCLING = 12.0


# default values for optional user configuration attributes
# these will be used if the user does not specify them in the configuration file
DEFAULT_CONFIGURATION_VALUES = {
    "segment_sampling_points_amount": 3,
    RASTER_CELL_RESOLUTION_KEY: 10,
    "save_raster_file": False,
    "datas_coverage_safety_percentage": DATA_COVERAGE_SAFETY_PERCENTAGE,
}
