""" Spatial operations for GeoDataFrames. """

import geopandas as gpd
import shapely
from src.preprocessing.data_source import DataSource
from src.data_utilities import rename_gdf_column
from src.config import DEFAULT_OSM_NETWORK_BUFFER_NAME
from src.logging import setup_logger, LoggerColors
from src.timer import time_logger
from shapely import wkt


LOG = setup_logger(__name__, LoggerColors.ORANGE.value)


def get_crs(gdf):
    return gdf.crs


def init_crs(gdf, crs):
    gdf.set_crs(crs, inplace=True)
    return gdf


def project_to_crs(gdf, crs):
    gdf.to_crs(crs, inplace=True)
    return gdf


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
        # roope todo -> ehkä custom error?
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


# roope todo -> laita use conffeihi et voi vaihtaa tätä distance arvoa ja per jokainen data...
# toi jokainen data -> kysy joltain esim Vuokko / Tuuli / Chris onko järkevää?

# roope todo -> laita mahollisuus laittaa eri bufferit per data?


@time_logger
def create_buffers_for_edges(gdf, buffer: int) -> gpd.GeoDataFrame:
    """
    Creates buffers in meters for gdf active geometry column.
    Creates new column called 'geometry_buffer_{buffer}' for gdf.
    """
    # buffer name will be e.g. geometry_buffer_20
    gdf[DEFAULT_OSM_NETWORK_BUFFER_NAME] = gdf.geometry.buffer(buffer)
    return gdf


def convert_wkt_to_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """convert geometry column from wkt to shapely geometry"""
    gdf["geometry"] = gdf["geometry_wkt"].apply(wkt.loads)
    return gdf


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


# roope todo -> ehkä halutaan poistaa? -> flagi poistamiseen confeista?
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


def spatial_join_gdfs(
    network_gdf: gpd.GeoDataFrame, data_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """spatially join vector datas: network and polygons geometries"""
    LOG.info("Spatial join data with network")
    joined_gdf = gpd.sjoin(network_gdf, data_gdf, how="inner", op="intersects")
    joined_gdf.rename_geometry("geometry_network", inplace=True)
    joined_gdf.drop(columns=["index_right"], inplace=True)
    return joined_gdf


import geopandas as gpd
from shapely.geometry import LineString
from shapely.ops import split


def cut_line_by_polygon(line, polygon):
    return [seg for seg in split(line, polygon) if seg.within(polygon)]


def process_segment(row, data_source):
    """TODO maybe remove secondary_data_source and multiple_data_strategy?"""
    osm_id = row["osm_id"]
    edge_geom = row["geometry_network"]
    data_geom = row["geometry_data"]
    primary_data_source = data_source.primary_data_column
    secondary_data_source = hasattr(data_source, "secondary_data_column")
    multiple_data_strategy = hasattr(data_source, "multiple_data_strategy")

    if secondary_data_source and multiple_data_strategy:
        LOG.info(
            "Has also secondary_data_source: {secondary_data_source}, using with strategy: {multiple_data_strategy}."
        )

    # TODO: add point sampling!

    if edge_geom.intersects(data_geom):
        LOG.info(osm_id)
        segments = cut_line_by_polygon(edge_geom, data_geom)
        LOG.info(segments)
        return

        # TODO: logic for each segment...
        # remember to handle multiprocessing / parallel processing

        # for segment in segments:
        #     segment_length = segment.length
        #     if "aasd" in my_dict:
        #         my_dict[key] += value
        #     else:
        #         my_dict[key] = value
        #     # Calculate weighted value based on db_lo, db_hi, and segment length
        #     # Handle NaN values as per your chosen strategy
        #     # weighted_value = calculate_weighted_value(
        #     #     segment_length, db_lo, db_hi
        #     # )  # Implement this function
        #     results.append((row["osm_id"], segment_length, weighted_value))

    # # Convert results to a DataFrame
    # segments_df = pd.DataFrame(
    #     results, columns=["osm_id", "segment_length", "weighted_value"]
    # )
