""" Api Path Engine module """

import csv
from fastapi import HTTPException
import json
import os
from typing import Tuple
from pyproj import Transformer

from shapely import wkt
from shapely.geometry import shape, MultiLineString, LineString, mapping
import geojson

from ..API.models import (
    EdgeFeature,
    PathFeature,
    PathProperties,
    SegmentProperties,
)

# from geojson import MultiLineString, LineString

from ..config import (
    CONFIGS_DIR,
    GEOMETRY_KEY,
    ODS_TEMP_CSV_PATH,
    OSM_IDS_KEY,
    PATH_ID_KEY,
    ROUTING_RESULTS_TABLE,
    SEGMENT_STORE_TABLE,
)

from ..database_controller import DatabaseController
from green_paths_2.src.pipeline_controller import (
    init_config_and_data_handler,
)
from ..osm_network_controller import handle_osm_network_process
from ..preprocessing.main import preprocessing_pipeline
from ..routing.main import (
    get_exposures_from_db,
)
from ..routing.r5py_router import build_custom_cost_network
from ..routing.routing_utilities import validate_segmented_osm_network_path

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_csv(lat: float, long: float, filename: str, id: int) -> str:
    filepath = os.path.join(ODS_TEMP_CSV_PATH, filename)
    with open(filepath, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        # delete all existing data
        writer.writerow([])
        writer.writerow(["lat", "lon", "id"])  # Column headers
        # TODO: Add the correct CRS, AND MAYHBE THE ID
        writer.writerow([lat, long, id])  # Data row
    return True


def build_custom_cost_networks(city_name: str) -> Tuple[dict, dict]:
    """
    Build custom cost networks for all user configurations.

    Returns:
    --------
    Tuple[dict, dict]
        Tuple of custom cost networks and user configurations. Keys are the names of the user configurations used.
    """
    # TODO ROOPE TODO: tää jotenki paremmmi, ehkä looppaamalla noi dirs?
    CITY_CONFIGS_PATH = os.path.join(CONFIGS_DIR, city_name)
    # list of names of all user configurations under certain directory
    user_configuration_names = os.listdir(CITY_CONFIGS_PATH)

    # doe not really matter which one is used
    first_config_path = os.path.join(CITY_CONFIGS_PATH, user_configuration_names[0])

    user_config, data_handler = init_config_and_data_handler(first_config_path)
    db_controller = DatabaseController()

    logger.info("Checking for preprocessed data from db, skipping if found.")

    if db_controller.get_row_count(SEGMENT_STORE_TABLE) < 0:
        logger.info("Starting preprocessing...")
        osm_network_gdf = handle_osm_network_process(user_config)
        preprocessing_pipeline(osm_network_gdf, data_handler, user_config)
        logger.info("Preprocessing completed.")

    osm_segmented_network_path = validate_segmented_osm_network_path(
        user_config.osm_network.osm_pbf_file_path
    )

    normalized_exposures_dict = get_exposures_from_db(db_controller, data_handler)

    custom_cost_networks = {}
    configs = {}

    for config_name in user_configuration_names:
        config_path = os.path.join(CITY_CONFIGS_PATH, config_name)
        user_config, data_handler = init_config_and_data_handler(config_path)

        custom_cost_transport_network = build_custom_cost_network(
            osm_segmented_network_path, normalized_exposures_dict, user_config
        )

        custom_cost_networks[config_name] = custom_cost_transport_network
        configs[config_name] = user_config

    return custom_cost_networks, configs


def get_individual_segments_using_routing_results(
    db_handler: DatabaseController, data_names: list[str]
) -> list[dict]:
    """
    Get single segments from the database to return a edge_FC to API.

    Parameters
    ----------
    db_handler : DatabaseController
        DatabaseController object.
    data_names : list of str
        List of column names to be used in the edge_FC.

    Returns
    -------
    list of dict
        List of dictionaries containing segment data
    """
    # get all osmids from the routing
    logger.info("Getting individual segments using routing results")
    routing_results = db_handler.get_all(ROUTING_RESULTS_TABLE, column_names=True)

    # get only osm_ids column by column name
    # this is actually string, which reminds of list, but it is not list
    osm_ids_string = routing_results[0][0][OSM_IDS_KEY]

    osm_ids_list = json.loads(osm_ids_string)

    # convert osm_ids list elements to int
    osm_ids_int_list = [int(i) for i in osm_ids_list]

    data_names_with_geometry = data_names.append(GEOMETRY_KEY)

    # TODO: should we get the normalized values instead, for visualization purposes?
    return db_handler.select_rows_by_osm_ids(
        table=SEGMENT_STORE_TABLE,
        osm_ids=osm_ids_int_list,
        columns=data_names_with_geometry,
    )


def _parse_coordinates_from_string_geom(geom: str):
    """
    Get the geometry from a row and parse the coordinates into a MultiLineString or LineString format.

    Parameters
    ----------
    geom : str
        A string representation of the geometry

    Returns
    -------
    coordinates: list of tuple or list of list of tuple
        A list of coordinates suitable for Shapely LineString or MultiLineString
    """
    try:
        if "MULTILINESTRING" in geom:
            geom_type = "MULTILINESTRING"
            chars_to_replace_and_split = ("((", "))", "),(")
        elif "LINESTRING" in geom:
            geom_type = "LINESTRING"
            chars_to_replace_and_split = ("(", ")", ",")
        else:
            raise ValueError("Unexpected geometry type")

        if not geom or geom.lower() == GEOMETRY_KEY:
            raise ValueError(f"Unexpected geometry: {geom}")

        # Parse coordinates
        parsed_geom = geom.replace(
            f"{geom_type} {chars_to_replace_and_split[0]}", ""
        ).replace(chars_to_replace_and_split[1], "")
        lines = parsed_geom.split(chars_to_replace_and_split[2])

        # Convert to Shapely-suitable format
        if geom_type == "MULTILINESTRING":
            coordinates = []
            for line in lines:
                # Trim spaces and any remaining parentheses
                coords = [coord.strip(" ()") for coord in line.split(", ")]
                # Convert to tuples of floats
                line_coords = [tuple(map(float, coord.split())) for coord in coords]
                coordinates.append(line_coords)
            return coordinates  # Wrap in list for MultiLineString
        elif geom_type == "LINESTRING":
            coords = [coord.strip(" ()") for coord in lines[0].split(", ")]
            coordinates = [tuple(map(float, coord.split())) for coord in coords]
            return coordinates  # Directly use for LineString

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"GP2 SERVER FAILED TO PARSE GEOMETRIES FROM RESULTS. GEOMETRY {geom}. Error: {e}",
        )


def convert_segments_to_features(
    segments_data: list[dict], data_names: list[str], path_id: str, source_crs: int
) -> list[EdgeFeature]:
    """
    Convert a list of segment dictionaries into a list of Features.

    Parameters
    ----------
    segments_data : list of dict
        Each dict represents a segment with 'geometry' and multiple properties.
    data_names : list of str
        The names of the properties to include in each Feature. Consist of data names derived from user configuration.
    path_id : str or None, optional
        An optional identifier for the path these segments belong to.

    Returns
    -------
    edge_features: list of EdgeFeatures
        A list of segments as EdgeFeatures
    """
    logger.info("Converting segments to features")
    try:
        edge_features = []

        for segment in segments_data:
            # geometry = MultiLineString(
            #     _parse_coordinates_from_string_geom(geom=segment[GEOMETRY_KEY])
            # )

            # the geometry is stored as string in sqlite db
            # convert to shapely geom
            geometry = wkt.loads(segment[GEOMETRY_KEY])

            # convert to 4326, which the front end uses
            geometry = convert_to_epsg4326(geometry, source_crs)

            # Convert Shapely geometry to GeoJSON-like dictionary
            geometry = mapping(geometry)

            # TODO: test exposure normalized value...
            # Dynamically create properties dictionary using data_names
            properties = {
                "exposure_norm_value": segment[name]
                for name in data_names
                if name in segment and name != GEOMETRY_KEY
            }

            properties[PATH_ID_KEY] = path_id

            feature = EdgeFeature(
                geometry=geometry, properties=SegmentProperties(**properties)
            )

            edge_features.append(feature)

        return edge_features
    except:
        raise HTTPException(
            status_code=500,
            detail=f"GP2 SERVER FAILED TO CONVERT SEGMENTS TO FEATURES (path_id: {path_id}).",
        )


def create_path_feature(
    path_output_result: dict, path_id: str, source_crs: int
) -> PathFeature:
    """
    Create a GeoJSON FeatureCollection for path data from the output_results table.

    Parameters
    ----------
    path_output_result : dict
        Dictionary containing path data.
    path_id: str
        Identifier for the path. Generally configuration name is used here

    Returns
    -------
    PathFeature:
        A PathFeature of the result path

    """
    try:

        # coordinates = _parse_coordinates_from_string_geom(
        #     geom=path_output_result[GEOMETRY_KEY]
        # )

        # the geometry is stored as string in sqlite db
        # convert to shapely geom
        geometry = wkt.loads(path_output_result[GEOMETRY_KEY])

        # Check if coordinates are valid for LineString (need at least 2 points)
        # if len(coordinates) < 2:
        #     logger.error(
        #         f"Insufficient points to create a LineStringm, path id {path_id}"
        #     )
        #     return None

        # geometry = LineString(coordinates)

        # convert back to 4326, which the front end uses
        geometry = convert_to_epsg4326(geometry, source_crs)

        # Convert Shapely geometry to GeoJSON-like dictionary
        geometry = mapping(geometry)

        properties = {k: v for k, v in path_output_result.items() if k != GEOMETRY_KEY}
        properties[PATH_ID_KEY] = path_id

        return PathFeature(
            geometry=geometry,
            properties=PathProperties(**properties),
        )
    except:
        raise HTTPException(
            status_code=500,
            detail=f"GP2 SERVER FAILED TO BUILD PATHFEATURE (path_id: {path_id}).",
        )


def convert_to_epsg4326(geometry, source_crs):
    """
    Convert a Shapely or GeoJSON geometry to EPSG:4326 (WGS 84).

    Parameters
    ----------
    geometry : shapely.geometry or geojson.geometry
        The geometry to be converted.
    source_crs : str
        The source CRS of the input geometry.

    Returns
    -------
    shapely.geometry
        The geometry converted to EPSG:4326.
    """
    transformer = Transformer.from_crs(source_crs, "EPSG:4326", always_xy=True)

    # Convert GeoJSON to shapely.geometry if needed
    if isinstance(geometry, dict) or isinstance(geometry, geojson.geometry.Geometry):
        geometry = shape(geometry)  # Convert GeoJSON to Shapely geometry

    if geometry.geom_type == "MultiLineString":
        converted_coords = []
        for line in geometry.geoms:
            line_coords = [(transformer.transform(x, y)) for x, y in line.coords]
            converted_coords.append(line_coords)
        return MultiLineString(converted_coords)

    elif geometry.geom_type == "LineString":
        line_coords = [(transformer.transform(x, y)) for x, y in geometry.coords]
        return LineString(line_coords)

    else:
        # Add more geometry types as needed
        raise ValueError(f"Unsupported geometry type: {geometry.geom_type}")
