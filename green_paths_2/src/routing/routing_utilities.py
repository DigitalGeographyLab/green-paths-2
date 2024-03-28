"""Module for routing utilities."""

import os
from green_paths_2.src.config import JAVA_PATH, NORMALIZED_DATA_SUFFIX, R5_JAR_FILE_PATH
import geopandas as gpd
from green_paths_2.src.data_utilities import construct_osm_segmented_network_name
from green_paths_2.src.preprocessing.user_data_handler import UserDataHandler

from green_paths_2.src.logging import setup_logger, LoggerColors


LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def set_environment_and_import_r5py() -> bool:
    """Set environment variables and import Green Paths 2 patch version of r5py."""
    try:
        import sys

        # Correctly use extend to add R5 classpath argument
        sys.argv.extend(["--r5-classpath", R5_JAR_FILE_PATH])

        # Now, dynamically import r5py and make it global
        global r5py, CustomCostTransportNetwork, TravelTimeMatrixComputer, DetailedItinerariesComputer
        import r5py
        from r5py import CustomCostTransportNetwork
        from r5py.r5.detailed_itineraries_computer import DetailedItinerariesComputer
        from r5py.r5.travel_time_matrix_computer import TravelTimeMatrixComputer

        return True
    except Exception as e:
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


import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# TODO TODO: not using anywhere atm...
# TODO: ROOPE TODO säädä tää kuntoon ku tiietää mitä kaikkia halutaan tukea...
def load_spatial_data_autodetect(file_path, target_crs="EPSG:4326"):
    # Extract file extension
    file_extension = os.path.splitext(file_path)[-1].lower()

    if file_extension == ".csv":
        # Load CSV
        df = pd.read_csv(file_path)
        # Assuming columns for origin and destination latitudes and longitudes
        origin_points = [Point(xy) for xy in zip(df.origin_lon, df.origin_lat)]
        dest_points = [Point(xy) for xy in zip(df.dest_lon, df.dest_lat)]
        # Combine into a single GeoDataFrame
        gdf_origins = gpd.GeoDataFrame(df, geometry=origin_points, crs="EPSG:4326")
        gdf_destinations = gpd.GeoDataFrame(df, geometry=dest_points, crs="EPSG:4326")
    elif file_extension in [".gpkg", ".shp"]:
        # Load GeoPackage or Shapefile
        gdf_origins = gpd.read_file(file_path)
        gdf_destinations = (
            gdf_origins.copy()
        )  # This line is illustrative; adjust based on actual needs
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    # Transform CRS if necessary for origins
    if gdf_origins.crs != target_crs:
        gdf_origins = gdf_origins.to_crs(target_crs)
    # Transform CRS if necessary for destinations
    if gdf_destinations.crs != target_crs:
        gdf_destinations = gdf_destinations.to_crs(target_crs)

    return gdf_origins, gdf_destinations
