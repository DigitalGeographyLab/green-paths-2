""" General configurations for Green Paths 2 project """

import os
import numpy as np


# R5PY PATHS

# GREEN PATSH 2 PATCHED R5 JAR FILE PATH
# new release (precalculations)
R5_JAR_FILE_PATH = "https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-3/r5-v7.1-gp2-3-1-gbcaa62a-all.jar"


# TODO: LOCAL FOR TESTING
# R5_JAR_FILE_PATH = (
#     "/Users/hcroope/omat/r5_dgl/r5/build/libs/r5-v7.1-gp2-2.dirty-all.jar"
# )

# TODO: LOCAL FOR TESTING
# JAVA_PATH = "/Users/hcroope/miniconda3/envs/r5py_Gp2/lib/jvm"


# DEFAULT VALUE FOR CUSTOM COST TRANSPORT NETWORK'S ALLOW MISSING DATA (OSMIDS)
ALLOW_MISSING_DATA_DEFAULT = True

# SQLITE DATABASE

# SQLITE3 DB PATH
GP2_DB_PATH = "green_paths_2/src/database/gp2.db"

# TABLES

SEGMENT_STORE_TABLE = "segment_store"

ROUTING_RESULTS_TABLE = "routing_results"

TRAVEL_TIMES_TABLE = "travel_times"

OUTPUT_RESULTS_TABLE = "output_results"


# TABLES SCHEMAS

DB_ROUTING_RESULTS_COLUMNS = [
    {"name": "from_id", "type": "TEXT"},
    {"name": "to_id", "type": "TEXT"},
    {"name": "osm_ids", "type": "TEXT"},
]

DB_TRAVEL_TIMES_COLUMNS = [
    {"name": "osm_id", "type": "INTEGER PRIMARY KEY"},
    {"name": "travel_time", "type": "REAL"},
]


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

RASTER_CELL_RESOLUTION_KEY = "raster_cell_resolution"

CUMULATIVE_RANGES_KEY = "cumulative_ranges"

OTHER_KEY = "other"

ROUTING_KEY = "routing"

TRAVEL_SPEED_KEY = "travel_speed"

TRANSPORT_MODE_KEY = "transport_mode"

EXPOSURE_PARAMETERS_KEY = "exposure_parameters"

ANALYSING_KEY = "analysing"

PRECALCULATE_KEY = "precalculate"

KEEP_GEOMETRY_KEY = "keep_geometry"

SAVE_OUTPUT_NAME_KEY = "save_output_name"

GPKG_FILE_NAME = "gpkg"

CSV_FILE_NAME = "csv"

MIN_EXPOSURE_SUFFIX = "_min_exposure"

MAX_EXPOSURE_SUFFIX = "_max_exposure"

SUM_EXPOSURE_SUFFIX = "_sum_exposure"

TRAVERSAL_TIME_WEIGHTED_PATH_EXPOSURE_AVERAGE_SUFFIX = (
    "_time_weighted_path_exposure_avg"
)

TRAVERSAL_TIME_WEIGHTED_PATH_EXPOSURE_SUM_SUFFIX = "_time_weighted_path_exposure_sum"

# seconds
CUMULATIVE_EXPOSURE_SECONDS_SUFFIX = "_cumulative_exposure_seconds"

# KEY LISTS

NETWORK_COLUMNS_TO_KEEP = [OSM_ID_KEY, GEOMETRY_KEY]

ORIGIN_DESTINATION_KEYS = [FROM_ID_KEY, TO_ID_KEY]


# PATHS

USER_CONFIG_PATH = "green_paths_2/user/config.yaml"

OUTPUT_RASTER_DIR_PATH = "green_paths_2/src/cache/raster"

OUTPUT_FINAL_RESULTS_DIR_PATH = "results_output"


# # CACHE

DATA_CACHE_DIR_PATH: str = "green_paths_2/src/cache"

OSM_CACHE_DIR_NAME: str = "osm"

OSM_CACHE_SEGMENTED_DIR_NAME: str = "segmented"

RASTER_CACHE_DIR_NAME = "raster"

LOGS_CACHE_DIR_NAME = "logs"


# FILENAMES AND FILE EXTENSIONS

OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION: str = "_segmented.osm.pbf"

DESCRIPTOR_FILE_NAME = "data_description.txt"

RASTER_FILE_SUFFIX = ".tif"

REPROJECTED_RASTER_FILE_SUFFIX = "_reprojected.tif"

NORMALIZED_DATA_SUFFIX = "_normalized"

TIF_FILE_EXTENSION = ".tif"

OUTPUT_RESULTS_FILE_NAME = "output_results"

AQI_DATA_CACHE_DIR_PATH = os.path.join(DATA_CACHE_DIR_PATH, RASTER_CACHE_DIR_NAME)


# DEFAULT VALUES

FIX_INVALID_GEOMETRIES: bool = True

RASTER_NO_DATA_VALUE = np.nan

SEGMENT_POINTS_DEFAULT_SAMPLING_STRATEGY = "mean"

SEGMENT_VALUES_ROUND_DECIMALS = 3

SEGMENT_SAMPLING_POINTS_KEY = "sampling_points"

DATA_COVERAGE_SAFETY_PERCENTAGE = 33

DEFAULT_R5_TRAVEL_SPEED_WALKING = 3.6

DEFAULT_R5_TRAVEL_SPEED_CYCLING = 12.0

DEFAULT_BATCH_PROCENTAGE = 0.1


# default values for optional user configuration attributes
# these will be used if the user does not specify them in the configuration file
DEFAULT_CONFIGURATION_VALUES = {
    "segment_sampling_points_amount": 3,
    RASTER_CELL_RESOLUTION_KEY: 10,
    "save_raster_file": False,
    "datas_coverage_safety_percentage": DATA_COVERAGE_SAFETY_PERCENTAGE,
}
