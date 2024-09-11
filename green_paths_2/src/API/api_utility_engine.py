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
    API_EXPOSURES,
    API_EXPOSURES_NAME_MAPPING,
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
    try:
        filepath = os.path.join(ODS_TEMP_CSV_PATH, filename)
        with open(filepath, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            # delete all existing data
            writer.writerow([])
            writer.writerow(["lat", "lon", "id"])  # Column headers
            # TODO: Add the correct CRS, AND MAYHBE THE ID
            writer.writerow([lat, long, id])  # Data row
        return True
    except Exception as e:
        logger.error(f"Failed to save CSV file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process OD's.")


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

    db_controller = DatabaseController()

    # empty segment store table to get a fresh start
    # TODO: only run this in PROD!!!
    # db_controller.empty_table(SEGMENT_STORE_TABLE)
    # TODO: run that code only in prod...

    custom_cost_networks = {}
    configs = {}

    # TODO: loop all exposures
    for exposure in API_EXPOSURES:  # ["greenery"]:
        # Directory path for current exposure type under the city
        exposure_config_path = os.path.join(CITY_CONFIGS_PATH, exposure)

        # List of all user configuration names under the current exposure directory
        # loop all of these sensitivities
        user_configuration_sensitivity_names = os.listdir(exposure_config_path)

        for config_name in user_configuration_sensitivity_names:
            config_path = os.path.join(exposure_config_path, config_name)
            user_config, data_handler = init_config_and_data_handler(config_path)

            # for first config, execute preprocessing pipeline if not done before

            segment_store_exists = db_controller.check_table_exists(SEGMENT_STORE_TABLE)
            if (
                not segment_store_exists
                or db_controller.get_row_count(SEGMENT_STORE_TABLE) == 0
            ):
                logger.info("Starting preprocessing...")
                osm_network_gdf = handle_osm_network_process(user_config=user_config)
                preprocessing_pipeline(
                    osm_network_gdf=osm_network_gdf,
                    data_handler=data_handler,
                    user_config=user_config,
                )
                logger.info("Preprocessing completed.")

            osm_segmented_network_path = validate_segmented_osm_network_path(
                osm_segmented_network_path=user_config.osm_network.osm_pbf_file_path
            )

            normalized_exposures_dict = get_exposures_from_db(
                db_handler=db_controller, data_handler=data_handler
            )

            custom_cost_transport_network = build_custom_cost_network(
                osm_segmented_network_path, normalized_exposures_dict, user_config
            )

            # Key format: 'exposure/config_name'
            exposure_config_id_key = f"{city_name}/{exposure}/{config_name}"
            custom_cost_networks[exposure_config_id_key] = custom_cost_transport_network
            configs[exposure_config_id_key] = user_config

    logger.info(f"Created {len(custom_cost_networks)} custom cost networks")
    return custom_cost_networks, configs


def get_individual_segments_using_routing_results(
    db_handler: DatabaseController, data_name: str
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

    columns_to_fetch = [data_name, GEOMETRY_KEY]

    # TODO: should we get the normalized values instead, for visualization purposes?
    return db_handler.select_rows_by_osm_ids(
        table=SEGMENT_STORE_TABLE,
        osm_ids=osm_ids_int_list,
        columns=columns_to_fetch,
    )


def convert_segments_to_features(
    segments_data: list[dict], data_name: str, path_id: str, source_crs: int
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

            # the geometry is stored as string in sqlite db
            # convert to shapely geom
            geometry = wkt.loads(segment[GEOMETRY_KEY])

            # convert to 4326, which the front end uses
            geometry = convert_to_epsg4326(geometry, source_crs)

            # Convert Shapely geometry to GeoJSON-like dictionary
            geometry = mapping(geometry)

            # TODO: test exposure normalized value...
            # Dynamically create properties dictionary using data_names
            properties = {"exposure_value": segment[data_name]}

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


def _filter_and_format_path_output_results_by_exposures(
    path_output_result: dict, exposure: str, path_id: str
) -> dict:
    """Filter path output results by exposures and return a dictionary with the filtered properties."""
    # seconds
    travel_time = path_output_result.get("travel_time", False)
    if not travel_time:
        travel_time = "not found"
    else:
        # Transform to minutes
        travel_time = int(float(travel_time))
        travel_time = int(round(travel_time / 60, 0))

    travel_length = path_output_result.get("length", False)
    if not travel_length:
        travel_length = "not found"
    else:
        travel_length = float(travel_length)
        if travel_length < 1000:
            travel_length = f"{round(travel_length, 1)} m"
        else:
            travel_length = f"{round(travel_length / 1000, 1)} km"

    # Prepare filtered properties with only the needed field
    filtered_properties = {
        PATH_ID_KEY: path_id,
        "Time": travel_time,
        "Length": travel_length,
    }

    for api_exposure, api_exposure_short in API_EXPOSURES_NAME_MAPPING.items():
        avg_exposure_field = f"{api_exposure_short}_time_weighted_path_exposure_avg"

        # Add average exposure to the filtered properties
        filtered_properties[f"{api_exposure}_average"] = path_output_result.get(
            avg_exposure_field, "not found"
        )

    # Handle cumulative exposure
    cumulative_exposure_field = (
        f"{API_EXPOSURES_NAME_MAPPING[exposure]}_cumulative_exposure_seconds"
    )
    cumulative_exposure_data = path_output_result.get(cumulative_exposure_field)

    # Check if cumulative_exposure_data is a string (possible JSON) and convert it to a dictionary
    if isinstance(cumulative_exposure_data, str):
        try:
            cumulative_exposure_data = json.loads(cumulative_exposure_data)
        except json.JSONDecodeError:
            cumulative_exposure_data = "invalid data"

    filtered_properties["cumulative_exposure"] = (
        cumulative_exposure_data
        if isinstance(cumulative_exposure_data, dict)
        else "not found"
    )

    return filtered_properties


def create_path_feature(
    path_output_result: dict, path_id: str, exposure: str, source_crs: int
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

        # convert back to 4326, which the front end uses
        geometry = convert_to_epsg4326(geometry, source_crs)

        # Convert Shapely geometry to GeoJSON-like dictionary
        geometry = mapping(geometry)

        filtered_properties = _filter_and_format_path_output_results_by_exposures(
            path_output_result, exposure, path_id
        )

        return PathFeature(
            geometry=geometry,
            properties=PathProperties(**filtered_properties),
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
