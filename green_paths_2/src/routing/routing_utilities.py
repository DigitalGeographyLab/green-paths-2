"""Module for routing utilities."""

import os

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from ..config import (
    NORMALIZED_DATA_SUFFIX,
    R5_JAR_FILE_PATH,
)
from ..data_utilities import construct_osm_segmented_network_name
from ..green_paths_exceptions import R5pyError
from ..preprocessing.data_types import DataSourceModel
from ..preprocessing.user_config_parser import UserConfig

from ..logging import setup_logger, LoggerColors


LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def set_environment_and_import_r5py(set_environmental_variables: bool = True) -> bool:
    """
    Set environment variables according to param flag and import Green Paths 2 patch version of r5py.

    Parameters
    ----------
    set_environmental_variables : bool, optional
        If True, set environmental variables, by default True

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    try:
        if set_environmental_variables:
            import sys

            # Correctly use extend to add R5 classpath argument
            sys.argv.extend(["--r5-classpath", R5_JAR_FILE_PATH])

        # dynamically import r5py and make it global
        global r5py, CustomCostTransportNetwork, TravelTimeMatrixComputer
        import r5py
        from r5py import CustomCostTransportNetwork
        from r5py.r5.travel_time_matrix_computer import TravelTimeMatrixComputer

        return True
    except R5pyError as e:
        LOG.error(
            f"Failed to set environment variables or import Green Paths 2 patch version of r5py. Error: {e}"
        )
        return False


def get_normalized_data_source_names(data_source_names: list[str]) -> list[str]:
    """
    Return normalized data source names.

    Parameters
    ----------
    data_source_names : list[str]
        List of data source names.

    Returns
    -------
    list[str]
        List of normalized data source names.
    """
    return [
        f"{data_source_name}{NORMALIZED_DATA_SUFFIX}"
        for data_source_name in data_source_names
    ]


def validate_segmented_osm_network_path(osm_segmented_network_path: str) -> str:
    """
    Check if segmented OSM network exists

    Parameters
    ----------
    osm_segmented_network_path : str
        Path to the OSM segmented network.

    Returns
    -------
    str
        Path to the OSM segmented network.

    Raises
    ------
    FileNotFoundError
        If segmented OSM network is not found.
    """
    osm_segmented_network_path = construct_osm_segmented_network_name(
        osm_segmented_network_path
    )
    if not os.path.exists(osm_segmented_network_path):
        raise FileNotFoundError(
            f"Segmented OSM network not found from path: {osm_segmented_network_path}. Please run preprocessing pipeline or segmenter first."
        )
    return osm_segmented_network_path


def test_2_init_single_hki_od_points():

    # "green_paths_2/src/cache/data/origin_point_hki.gpkg"

    # "green_paths_2/src/cache/data/destination_point_hki.gpkg"

    origin_point = gpd.read_file(
        os.path.join("green_paths_2/src/cache/data/multiple_origin_points.gpkg")
    )

    # check that the crs is correct, if not, convert it
    if not origin_point.crs or origin_point.crs != "EPSG:4326":
        origin_point = origin_point.to_crs("EPSG:4326")

    origin_point.geometry = origin_point.geometry.centroid

    destination_point = gpd.read_file(
        os.path.join("green_paths_2/src/cache/data/multiple_destinations_hki.gpkg")
    )

    # check that the crs is correct, if not, convert it
    if not destination_point.crs or destination_point.crs != "EPSG:4326":
        destination_point = destination_point.to_crs("EPSG:4326")

    destination_point.geometry = destination_point.geometry.centroid

    return origin_point, destination_point


def init_origin_destinations_from_files(
    routing_config: UserConfig, project_crs: str | int
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Initialize origins and destinations from files.

    Parameters
    ----------
    routing_config : UserConfig
        Routing configuration.
    project_crs : str | int
        Project CRS.

    Returns
    -------
    tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]
        Tuple containing the origins and destinations GeoDataFrames.
    """

    origins_path = routing_config.origins
    destinations_path = routing_config.destinations

    if hasattr(routing_config, DataSourceModel.ODLonName.value) and hasattr(
        routing_config, DataSourceModel.ODLatName.value
    ):
        lon_name = routing_config.od_lon_name
        lat_name = routing_config.od_lat_name
        od_crs = routing_config.od_crs

        if lon_name and lat_name:
            origins = build_routing_ods_from_file(
                origins_path,
                original_crs=od_crs,
                target_crs=project_crs,
                lon_col_name=lon_name,
                lat_col_name=lat_name,
            )
            destinations = build_routing_ods_from_file(
                destinations_path,
                original_crs=od_crs,
                target_crs=project_crs,
                lon_col_name=lon_name,
                lat_col_name=lat_name,
            )

            return origins, destinations

    origins = build_routing_ods_from_file(origins_path, target_crs=project_crs)
    destinations = build_routing_ods_from_file(
        destinations_path, target_crs=project_crs
    )

    return origins, destinations


# TODO: remove this
def test_init_ods():
    population_grid = gpd.read_file(
        os.path.join(
            "/Users/hcroope/omat_playground/r5py/docs/_static/data/Helsinki/population_grid_2020.gpkg"
        )
    )
    import shapely

    RAILWAY_STATION = shapely.Point(24.941521, 60.170666)
    # take just the 10 first points from the population grid

    origins = population_grid.copy()
    # origins = origins.iloc[:100]
    origins.geometry = origins.geometry.centroid

    destinations = gpd.GeoDataFrame(
        {"id": [1], "geometry": [RAILWAY_STATION]},
        crs="EPSG:4326",
    )

    return origins, destinations


def build_routing_ods_from_file(
    file_path: str,
    original_crs: str | int = None,
    target_crs: str | int = None,
    lon_col_name: str = None,
    lat_col_name: str = None,
):
    """
    Build routing origins or destinations from file.

    Parameters
    ----------
    file_path : str
        Path to the file.
    target_crs : str | int, optional
        Target CRS, by default None
    lon_col_name : str, optional
        Longitude column name, by default None
    lat_col_name : str, optional
        Latitude column name, by default None

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame containing the routing origins or destinations.
    """
    # Extract file extension
    file_extension = os.path.splitext(file_path)[-1].lower()

    if file_extension == ".csv":
        df = pd.read_csv(file_path)
        # Assuming columns for origin and destination latitudes and longitudes
        points_from_csv = [Point(xy) for xy in zip(df[lat_col_name], df[lon_col_name])]
        gdf_from_file = gpd.GeoDataFrame(df, geometry=points_from_csv, crs=original_crs)
    elif file_extension in [".gpkg", ".shp"]:
        gdf_from_file = gpd.read_file(file_path)
    else:
        raise ValueError(
            f"Unsupported file extension for Origins or Destinations: {file_extension}. Please use .csv, .gpkg or .shp."
        )

    # all geometries should be of type Point, otherwise raise an error
    if not gdf_from_file.geometry.geom_type.eq("Point").all():
        raise ValueError(
            f"Invalid geometry type in the Origins or Destinations file. Please make sure the file contains only Point geometries."
        )

    # Check if the crs is correct, if not, convert it
    if gdf_from_file.crs != target_crs:
        gdf_from_file = gdf_from_file.to_crs(target_crs)

    return gdf_from_file
