""" General configurations for Green Paths 2 project """

# NOTE: QUICK FIX FOR ABSOLUTE PATH NAMES, NO TIME TO FIX THIS PROPERLY
# SO THIS SHALL DO...
# THIS SHOULD BE TAKEN TO SERVER AN NAMED AS "config.py"


import os
import numpy as np


# OSM IDS TO INT V5 R5 (allow empty CCnetworks)
R5_JAR_FILE_PATH = "https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-5/r5-v7.1-gp2-5-all.jar"


# DEFAULT VALUE FOR CUSTOM COST TRANSPORT NETWORK'S ALLOW MISSING DATA (OSMIDS)
ALLOW_MISSING_DATA_DEFAULT = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLITE DATABASE

# SQLITE3 DB PATH
GP2_DB_PATH = "/home/ubuntu/green-paths-2/green_paths_2/src/database/gp2.db"

# SQLITE3 DB PATH FOR TESTING
GP2_DB_TEST_PATH = (
    "/home/ubuntu/green-paths-2/green_paths_2/tests/database/gp2_testing.db"
)

# TABLES

SEGMENT_STORE_TABLE = "segment_store"

ROUTING_RESULTS_TABLE = "routing_results"

TRAVEL_TIMES_TABLE = "travel_times"

OUTPUT_RESULTS_TABLE = "output_results"

# PIPELINE NAMES

PREPROCESSING_PIPELINE_NAME = "preprocessing"

ROUTING_PIPELINE_NAME = "routing"

ANALYSING_PIPELINE_NAME = "analysing"

ALL_PIPELINE_NAME = "all"


# KEYS

NAME_KEY = "name"

USER_ID_KEY = "user_id"

CONFIG_NAME_KEY = "config_name"

FROM_ID_KEY = "from_id"

TO_ID_KEY = "to_id"

LENGTH_KEY = "length"

GEOMETRY_KEY = "geometry"

TRAVEL_TIME_KEY = "travel_time"

ID_KEY = "id"

PATH_ID_KEY = "path_id"

OSM_ID_KEY = "osm_id"

OSM_IDS_KEY = "osm_ids"

PROJECT_CRS_KEY = "project_crs"

DATA_COVERAGE_SAFETY_PERCENTAGE_KEY = "datas_coverage_safety_percentage"

RASTER_CELL_RESOLUTION_KEY = "raster_cell_resolution"

CUMULATIVE_RANGES_KEY = "cumulative_ranges"

OTHER_KEY = "other"

ROUTING_KEY = "routing"

CHUNKING_TRESHOLD_KEY = "chunking_treshold"

TRAVEL_SPEED_KEY = "travel_speed"

TRAVEL_SPEED_WALKING_KEY = "travel_speed_walking"

TRAVEL_SPEED_CYCLING_KEY = "travel_speed_cycling"

TRANSPORT_MODE_KEY = "transport_mode"

EXPOSURE_PARAMETERS_KEY = "exposure_parameters"

PROJECT_KEY = "project"

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

USER_CONFIG_PATH = "/home/ubuntu/green-paths-2/green_paths_2/user/config.yaml"

OUTPUT_FINAL_RESULTS_DIR_PATH = "results_output"

TEST_OUTPUT_RESULTS_DIR_PATH = "/home/ubuntu/green-paths-2/green_paths_2/tests/outputs"


# # CACHE

TEST_DATA_CACHE_DIR_PATH: str = "tests/data"

OSM_CACHE_DIR_NAME: str = "osm"

OSM_CACHE_SEGMENTED_DIR_NAME: str = "segmented"

RASTER_CACHE_DIR_NAME = "raster"

LOGS_CACHE_DIR_NAME = "logs"


# FILENAMES AND FILE EXTENSIONS

OSM_DEFAULT_FILE_EXTENSION: str = ".osm.pbf"

OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION: str = "_segmented"

DESCRIPTOR_FILE_NAME = "data_description.txt"

RASTER_FILE_SUFFIX = ".tif"

REPROJECTED_RASTER_FILE_SUFFIX = "_reprojected.tif"

NORMALIZED_DATA_SUFFIX = "_normalized"

TIF_FILE_EXTENSION = ".tif"

OUTPUT_RESULTS_FILE_NAME = "output_results"


# DEFAULT VALUES

# not the best approach, but it is a quick fix for now (for tests)
ROUTING_CHUNKING_THRESHOLD = 200_000

CHUNK_SIZE_FOR_ROUTING_RESULTS = 100_000

FIX_INVALID_GEOMETRIES: bool = True

RASTER_NO_DATA_VALUE = -9999.0

SEGMENT_POINTS_DEFAULT_SAMPLING_STRATEGY = "mean"

SEGMENT_VALUES_ROUND_DECIMALS = 3

SEGMENT_SAMPLING_POINTS_KEY = "sampling_points"

DATA_COVERAGE_SAFETY_PERCENTAGE = 33

DEFAULT_R5_TRAVEL_SPEED_WALKING = 5

DEFAULT_R5_TRAVEL_SPEED_CYCLING = 15

DEFAULT_BATCH_PROCENTAGE = 0.1

DEFAULT_USER_ID = "GP2"


# default values for optional user configuration attributes
# these will be used if the user does not specify them in the configuration file
DEFAULT_CONFIGURATION_VALUES = {
    "segment_sampling_points_amount": 3,
    RASTER_CELL_RESOLUTION_KEY: 10,
    "save_raster_file": False,
    "datas_coverage_safety_percentage": DATA_COVERAGE_SAFETY_PERCENTAGE,
}

# TABLES SCHEMAS

DB_ROUTING_RESULTS_COLUMNS = [
    {"name": FROM_ID_KEY, "type": "TEXT"},
    {"name": TO_ID_KEY, "type": "TEXT"},
    {"name": CONFIG_NAME_KEY, "type": "TEXT"},
    {"name": OSM_IDS_KEY, "type": "TEXT"},
    {"name": USER_ID_KEY, "type": "TEXT"},
]

DB_TRAVEL_TIMES_COLUMNS = [
    {"name": OSM_ID_KEY, "type": "INTEGER PRIMARY KEY"},
    {"name": TRAVEL_TIME_KEY, "type": "REAL"},
]

DB_OUTPUT_RESULST_BASE_COLUMNS = {TO_ID_KEY: -1, FROM_ID_KEY: -1}

# CACHE DIRS
DATA_CACHE_DIR_PATH: str = os.path.join(BASE_DIR, "cache")
AQI_DATA_CACHE_DIR_PATH = os.path.join(DATA_CACHE_DIR_PATH, RASTER_CACHE_DIR_NAME)

# API

HElSINKI_CITY_KEY = "helsinki"

UPDATE_IN_PROGRESS_KEY = "update_in_progress"

LATEST_BUILD_AQI_TIMESTAMP_KEY = "latest_build_aqi_timestamp"

LATEST_FETCH_AQI_TIMESTAMP_KEY = "latest_fetch_aqi_timestamp"

# mapping for API exposures names to the names used in the database
API_EXPOSURES_NAME_MAPPING = {
    "airquality": "aqi",
    "greenery": "gvi",
    "noise": "noise",
}

ODS_TEMP_CSV_PATH = "/home/ubuntu/green-paths-2/green_paths_2/src/API/temp_ods"

CONFIGS_DIR = "/home/ubuntu/green-paths-2/green_paths_2/src/API/configs"

# Define filenames for origin and destination
ORIGIN_CSV_NAME = "api_origin.csv"
DESTINATION_CSV_NAME = "api_destination.csv"

# API EXPOSURES (DIR NAMES)
GREENERY_EXPOSURE_KEY = "greenery"
AIRQUALITY_EXPOSURE_KEY = "airquality"
NOISE_EXPOSURE_KEY = "noise"

API_EXPOSURES = [GREENERY_EXPOSURE_KEY, AIRQUALITY_EXPOSURE_KEY, NOISE_EXPOSURE_KEY]
