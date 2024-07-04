""" Spatial operations for GeoDataFrames. """

import geopandas as gpd
import rasterio
import shapely

from green_paths_2.src.config import GEOMETRY_KEY, RASTER_CELL_RESOLUTION_KEY

from ..logging import setup_logger, LoggerColors
from ..timer import time_logger
from shapely.geometry import MultiLineString
from shapely.wkt import dumps
from pyproj import CRS

import geopandas as gpd
from shapely.geometry import box


LOG = setup_logger(__name__, LoggerColors.ORANGE.value)


def get_crs(gdf):
    return gdf.crs


def init_crs(gdf, crs):
    gdf.set_crs(crs, inplace=True)
    return gdf


def project_to_crs(gdf, crs):
    gdf.to_crs(crs, inplace=True)
    return gdf


def crs_uses_meters(crs_code) -> bool:
    """Check if CRS uses meters as unit."""
    # Allows input as EPSG code, PROJ string, etc.
    crs = CRS.from_user_input(crs_code)
    return crs.axis_info[0].unit_name == "metre"


def handle_gdf_crs(
    name: str,
    gdf: gpd.GeoDataFrame,
    target_crs: int,
    original_crs: int = None,
) -> gpd.GeoDataFrame:
    """
    Validates and handles CRS for GeoDataFrame.
    If CRS is not found, and original CRS is not given, raises error,
    for we can't know what is the correct CRS for the data.
    If CRS is not the same as target CRS, project to target CRS.
    Target CRS is derived from user configurations, and should be selected
    based on the spatial extent (location) of the network and data.

    :param name: Name of the data.
    :param gdf: GeoDataFrame to handle CRS for.
    :param target_crs: Target CRS to project to.
    :param original_crs: Original CRS of the data.
    :return: GeoDataFrame with correct CRS.
    """
    # this csr is derived from the gdf
    gdf_original_crs = get_crs(gdf)
    LOG.info(f"Gdf {name} original crs: {gdf_original_crs}")

    # if data has no crs, and no crs is given in params (mostly derived from config), raise error
    # for we can't know what is the correct CRS for the data/gdf
    if not gdf_original_crs and not original_crs:
        # TODO: ehkä custom error?
        raise Exception(f"No CRS found or original CRS defined for data: {name}")

    # if gdf has no crs, but original_crs is found from conf
    if not gdf_original_crs and original_crs:
        LOG.info(f"set gdf {name} crs from user confs")
        gdf = init_crs(gdf, original_crs)

    # if crs not the same as target crs, project to target crs
    if target_crs and gdf_original_crs != target_crs or original_crs != target_crs:
        LOG.info(
            f"gdf {name} has different crs than target crs. Projecting to target crs: {target_crs}"
        )
        gdf = project_to_crs(gdf, target_crs)

    f"gdf {name} crs is now: {get_crs(gdf)}"
    return gdf


# TODO: laita use conffeihi et voi vaihtaa tätä distance arvoa ja per jokainen data...
# toi jokainen data -> kysy joltain esim Vuokko / Tuuli / Chris onko järkevää?

# TODO: laita mahollisuus laittaa eri bufferit per data?


@time_logger
def create_buffer_for_geometries(
    data_name: str, gdf: gpd.GeoDataFrame, buffer_size: int
) -> gpd.GeoDataFrame:
    """
    Creates buffers for geometries in a GeoDataFrame.

    :param data_name: Name of the data being processed.
    :param gdf: GeoDataFrame containing the geometries to buffer.
    :param buffer_size: Size of the buffer in meters.
    :return: A new GeoDataFrame with buffered geometries.
    """
    LOG.info(
        f"Creating {buffer_size}m buffer for geometries in GeoDataFrame {data_name}"
    )
    # Create buffers
    buffered_gdf = gdf.copy()
    buffered_gdf.geometry = buffered_gdf.geometry.buffer(int(buffer_size))

    return buffered_gdf


def has_invalid_geometries(gdf: gpd.GeoDataFrame, name: str = "") -> bool:
    """Check for invalid geometries in GeoDataFrame"""
    LOG.info(f"Checking for invalid geometries for {name}")

    non_geom_rows = gdf[
        gdf.geometry.apply(
            lambda x: not isinstance(
                x, (shapely.geometry.base.BaseGeometry, type(None))
            )
        )
    ]
    invalid_geoms = gdf[~gdf.geometry.is_valid]
    LOG.info(
        f"Found {len(non_geom_rows)} rows with non-geometry geometries and {len(invalid_geoms)} invalid geometries"
    )
    if non_geom_rows.empty and invalid_geoms.empty:
        return False
    return True


def fix_invalid_geometries(gdf: gpd.GeoDataFrame, remove_invalid: bool = False):
    """
    Fix invalid geometries, try to fix with buffer 0
    If fix wont work, remove those geometries
    """
    invalid_geoms = gdf[~gdf.geometry.is_valid]
    LOG.info(
        f"Trying to fix {len(invalid_geoms)} invalid geometries with buffer 0. Remove invalid is: {remove_invalid}"
    )

    # attempt to fix geoms with zero buffer
    if not invalid_geoms.empty:
        gdf.loc[~gdf.geometry.is_valid, "geometry"] = gdf.loc[
            ~gdf.geometry.is_valid
        ].geometry.buffer(0)
    invalid_geoms_after_fix = gdf[~gdf.geometry.is_valid]
    if not invalid_geoms_after_fix.empty and remove_invalid:
        LOG.info(
            f"Found {len(invalid_geoms_after_fix)} invalid geometries after attempting to fix. Removing them."
        )
        gdf = gdf[gdf.geometry.is_valid]
        LOG.info(f"Removed {len(invalid_geoms_after_fix)} still invalid geometries")
    else:
        LOG.info("Managed to fix all invalid geometries with adding buffer 0's to all")

    return gdf


def check_if_vector_data_and_network_extends_overlap(
    data_gdf: gpd.GeoDataFrame, network_gdf: gpd.GeoDataFrame
) -> bool:
    """
    Check if the extent of the vector and the network data overlap.

    Parameters:
    - vector_extent: The extent of the vector data.
    - network_gdf: The GeoDataFrame containing the road network data.

    Returns:
    - True if the extent of the vector and the network data overlap, False otherwise.
    """
    data_extent = gpd.GeoDataFrame(
        {"geometry": [data_gdf.unary_union]}, crs=data_gdf.crs
    )
    return data_extent.intersects(network_gdf.unary_union).any()


def check_if_raster_and_network_extends_overlap(
    raster_data_filepath: str, network_gdf: gpd.GeoDataFrame
) -> bool:
    """
    Check if the extent of the raster and the network data overlap.

    Parameters:
    - raster_extent: The extent of the raster data.
    - network_gdf: The GeoDataFrame containing the road network data.

    Returns:
    - True if the extent of the raster and the network data overlap, False otherwise.
    """

    # Open raster and get bounds
    with rasterio.open(raster_data_filepath) as src:
        bounds = src.bounds
        raster_extent = gpd.GeoDataFrame({"geometry": [box(*bounds)]}, crs=src.crs)

    return raster_extent.intersects(network_gdf.unary_union).any()


def get_most_accurate_data_source_resolution(data_sources) -> list:
    """
    Get the resolutions from data sources.

    Parameters:
    - data_sources: The data sources.

    Returns:
    - The most accurate resolution from the data sources.
    """
    resolutions = []
    for data_source in data_sources:
        if "raster_cell_resolution" in data_source:
            # prioritize resolution from user configurations
            conf_resolution = data_source.get(RASTER_CELL_RESOLUTION_KEY)
            resolutions.append(conf_resolution)
        elif data_source.get("data_type") == "raster":
            # process raster resolution from file
            # if it did not have resolution in confs
            raster_path = data_source.get("filepath")
            with rasterio.open(raster_path) as dataset:
                raster_resolution = dataset.res
            # take the min from tuple of dimensions
            resolutions.append(min(raster_resolution))
    return min(resolutions)


def convert_geometries_to_wkt(
    data: dict[str, dict[str, float]]
) -> dict[str, dict[str, float]]:
    """Convert geometries to WKT format."""
    for _, values in data.items():
        if GEOMETRY_KEY in values and isinstance(values[GEOMETRY_KEY], MultiLineString):
            values[GEOMETRY_KEY] = dumps(values[GEOMETRY_KEY])
    return data
