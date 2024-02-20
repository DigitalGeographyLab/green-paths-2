""" General configurations for Green Paths 2 project """

# OSM

OSM_SEGMENTED_NETWORK_DIR_PATH = "src/data/cache/osm"
OSM_SEGMENTED_NETWORK_NAME = "segmented_network.osm.pbf"

SUPPORTED_DATA_TYPES = ["point", "line", "polygon", "raster"]
SUPPORTED_FILE_FORMATS = [
    "gpkg",
    "gml",
]  # "shp", "csv", "json", "geojson", "tif", "tiff"

NETWORK_COLUMNS_TO_KEEP = ["id", "geometry"]

# cache dir for programatically downloadable data
DATA_CACHE_DIR_PATH: str = (
    "/Users/hcroope/omat/GP2/green_paths_2/green_paths_2/src/data/cache"
)

OSM_CACHE_DIR_NAME: str = "osm"

OSM_CACHE_SEGMENTED_DIR_NAME: str = "segmented"

OSM_SEGMENTED_DEFAULT_FILE_NAME: str = "segmented_network.osm.pbf"

# path to user configuration file which has e.g. data sources and osm network file path
USER_CONFIG_PATH = "src/user/config.yaml"


# GDF DEFAULT NAMES
GDF_BUFFERED_GEOMETRY_NAME = "buffered_geometry"
