""" General configurations for Green Paths 2 project """

NETWORK_BUFFERED_GDF_CACHE_FILE_NAME = "osm_network_buffered_cache.gpkg"
BUFFERED_NETWORK_GPKG_CACHE_PATH = f"/Users/hcroope/omat/GP2/green_paths_2/green_paths_2/src/data/cache/dev/{NETWORK_BUFFERED_GDF_CACHE_FILE_NAME}"

SUPPORTED_DATA_TYPES = ["point", "line", "polygon", "raster"]
SUPPORTED_FILE_FORMATS = [
    "gpkg",
    "gml",
]  # "shp", "csv", "json", "geojson", "tif", "tiff"

DEFAULT_OSM_NETWORK_BUFFER_NAME = "osm_edge_buffer"
NETWORK_COLUMNS_TO_KEEP = ["id", "geometry", DEFAULT_OSM_NETWORK_BUFFER_NAME]

DEFAULT_OSM_NETWORK_BUFFER_METERS = 20

# cache dir for programatically downloadable data
DATA_CACHE_DIR_PATH: str = (
    "/Users/hcroope/omat/GP2/green_paths_2/green_paths_2/src/data/cache"
)

# path to user configuration file which has e.g. data sources and osm network file path
USER_CONFIG_PATH = "src/user/config.yaml"
