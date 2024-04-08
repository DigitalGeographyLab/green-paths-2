""" This module contains functions for loading and processing vector data. """

import geopandas as gpd
from green_paths_2.src.config import FIX_INVALID_GEOMETRIES
from green_paths_2.src.green_paths_exceptions import DataManagingError
from green_paths_2.src.preprocessing.data_source import DataSource

from green_paths_2.src.data_utilities import (
    filter_gdf_by_columns_if_found,
)

# from green_paths_2.src.preprocessing.data_types import DataSourceModel
from green_paths_2.src.preprocessing.spatial_operations import (
    fix_invalid_geometries,
    handle_gdf_crs,
    has_invalid_geometries,
)
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.BLUE.value)


import fiona


# TODO:  -> need to rename layers?
# noise_layers = {name: gdf.rename(columns={'db_low': name}) for name, gdf in noise_layers.items()}
def list_vector_data_layers(gpkg_path):
    LOG.info(f"Listing layers in GeoPackage: {gpkg_path}")
    available_layers = [layer for layer in fiona.listlayers(gpkg_path)]
    LOG.info(f"Available layers: {available_layers} for data path: {gpkg_path}")
    return available_layers


# TODO:  -> what if there is multiple layers?
def load_vector_data(data_path: str, layer_name: str = None):
    """
    Load vector point data from GeoPackage.
    If layer name is not provided, and there is multiple layers in the vector data, raise error.

    :param data_path: Path to the vector data.
    :param layer_name: Name of the layer to load.
    :return: GeoDataFrame containing the vector data.
    """
    LOG.info("loading vector point data")
    try:
        # layer name not provided
        if not layer_name:
            available_layers = list_vector_data_layers(data_path)
            if not available_layers:
                raise DataManagingError(
                    f"No layername provided and no layers found from vector data: {data_path}"
                )
            if len(available_layers) > 1 and not available_layers:
                raise DataManagingError(
                    f"Vector data has many layers but no layer name provided to choose from: {data_path}"
                )
                # return multiple layers as dict
                # return {
                #     name: gpd.read_file(data_path, layer=name)
                #     for name in available_layers
                # }
            # get the only layer name
            layer_name = available_layers[0]
        return gpd.read_file(data_path, layer=layer_name)
    except DataManagingError as e:
        LOG.info(f"failed to read vector point data layer for path: {data_path}")
        LOG.error(e)


def preprocess_vector_data(
    vector_data_gdf: gpd.GeoDataFrame,
    data_name: str,
    data_source: DataSource,
    project_crs: int,
) -> gpd.GeoDataFrame:
    """
    Preprocess vector data.
    If columns of interest is given filter the columns.
    Handle CRS of the data.

    :param data_name: Name of the data.
    :param data_source: Data source model.
    :param user_config: User configurations.

    :return: Preprocessed vector data.
    """
    # if specified, filter the vector data by the given columns
    if data_source.columns_of_interest:
        vector_data_gdf = filter_gdf_by_columns_if_found(
            vector_data_gdf,
            data_source.columns_of_interest,
            keep=True,
        )

    # LOG.info(f"is type gdf {isinstance(vector_data_gdf, gpd.GeoDataFrame)}")
    # LOG.info(f"vector data gdf size: {len(vector_data_gdf)}")
    # handle crs
    vector_data_gdf = handle_gdf_crs(
        name=data_name,
        gdf=vector_data_gdf,
        target_crs=project_crs,
        original_crs=data_source.original_crs,
    )

    # TODO:  -> muuttujiin nimet! vai poista?
    # save the data geometry to a new column to preserve it during sjoin
    # also rename geometry column to be more descriptive
    # vector_data_gdf["geometry_data"] = vector_data_gdf["geometry"].copy()

    return vector_data_gdf


# TODO:  -> maybe not pass the config here only the values?
# TODO:  -> toi data source model on väärä
def load_and_process_vector_data(
    data_name: str,
    data_source: DataSource,
    project_crs: int,
) -> gpd.GeoDataFrame:
    LOG.info(f"processing vector data: {data_source.filepath}")
    vector_data_gdf: gpd.GeoDataFrame = load_vector_data(data_source.filepath)
    cleaned_vector_data_gdf: gpd.GeoDataFrame = preprocess_vector_data(
        vector_data_gdf, data_name, data_source, project_crs
    )

    data_has_invalid_geometries = has_invalid_geometries(
        cleaned_vector_data_gdf, data_name
    )
    if data_has_invalid_geometries:
        cleaned_vector_data_gdf = fix_invalid_geometries(
            cleaned_vector_data_gdf, remove_invalid=FIX_INVALID_GEOMETRIES
        )
    return cleaned_vector_data_gdf
    # # TODO: should all this spatial join be removed -> if rasterizing is used?
    # spatially_joined_edges_with_polygons: gpd.GeoDataFrame = spatial_join_gdfs(
    #     osm_network_gdf, cleaned_vector_data_gdf
    # )

    # # drop index
    # # spatially_joined_edges_with_polygons.reset_index(drop=True)

    # # group
    # dfs_by_osm_id = spatially_joined_edges_with_polygons.groupby("osm_id")

    # # drop index
    # # spatially_joined_edges_with_polygons.reset_index(drop=True)

    # # TODO:  -> tää varmaankin pitäs laittaa jotenkin paralleleille hyvin helposti!
    # for osm_id, group_df in dfs_by_osm_id:
    #     LOG.info(f"Data for osm_id {osm_id}:")

    #     # test = calculate_exposure_distances(data_source, group_df)

    # # LOG.info(f"analysis results: {spatially_joined_edges_with_polygons.head(2)}")
    # # LOG.info(f"analysis length: {len(spatially_joined_edges_with_polygons)}")

    # # unique_osm_ids_count = analysis_results["osm_id"].nunique()
    # # LOG.info(unique_osm_ids_count)
