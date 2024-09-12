""" Module for handling exposure data in the exposure analysing pipeline. Has also some general utilities """

import os

import geopandas as gpd
import pandas as pd
from shapely import wkt
from ..database_controller import DatabaseController
from ..preprocessing.user_config_parser import UserConfig

from ..config import (
    DEFAULT_BATCH_PROCENTAGE,
    GEOMETRY_KEY,
    ANALYSING_KEY,
    CSV_FILE_NAME,
    GPKG_FILE_NAME,
    OUTPUT_FINAL_RESULTS_DIR_PATH,
    OUTPUT_RESULTS_FILE_NAME,
    OUTPUT_RESULTS_TABLE,
    PROJECT_CRS_KEY,
    PROJECT_KEY,
    SAVE_OUTPUT_NAME_KEY,
    TEST_OUTPUT_RESULTS_DIR_PATH,
)

from ..logging import setup_logger, LoggerColors
from ..preprocessing.user_config_parser import UserConfig

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def save_to_gpkg_or_csv(df: pd.DataFrame, output_path: str, crs: int | str) -> None:
    """
    Save the final output to GeoPackage or CSV depending if geometry column is present.

    Parameters
    ----------
    df : pd.DataFrame
        The final output data.
    output_path : str
        The path to save the output data.
    """
    if GEOMETRY_KEY in df.columns:
        # Convert WKT geometries to GeoDataFrame
        df[GEOMETRY_KEY] = df[GEOMETRY_KEY].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry=GEOMETRY_KEY)
        gdf.set_crs(crs, inplace=True)
        gdf.to_file(output_path, driver="GPKG")
        LOG.info(f"Final output saved to GeoPackage: {output_path}")
    else:
        df["crs"] = f"EPSG:{crs}" if isinstance(crs, int) else crs
        df.to_csv(output_path, index=False, encoding="utf-8")
        LOG.info(f"Final output saved to CSV: {output_path}")


def get_batch_limit(routing_results_count: int):
    """
    Calculate the batch limit for analysing pipeline.

    Parameters
    ----------
    routing_results_count : int
        The count of routing results.
    """
    # TODO: put to config
    if routing_results_count < 1000:
        return routing_results_count

    # get the routing results count to enable batch processing
    LOG.info(f"the routing results count is {routing_results_count}. Splitting ")
    # Calculate batch limit
    limit = max(1, int(routing_results_count * DEFAULT_BATCH_PROCENTAGE))
    return limit


def save_exposure_results_to_file(
    db_handler: DatabaseController,
    user_config: UserConfig,
    keep_geometries: bool,
):
    """Save exposure results to file."""
    # after all chunks are processed, get all and save to csv of gpkg
    output_all_final_results, output_column_names = db_handler.get_all(
        OUTPUT_RESULTS_TABLE, column_names=True
    )

    final_output_df = pd.DataFrame(
        output_all_final_results, columns=output_column_names
    )

    # see if user configurations have output file name, if not use defaults
    output_file_name = user_config.get_nested_attribute(
        [ANALYSING_KEY, SAVE_OUTPUT_NAME_KEY]
    )

    if not output_file_name:
        output_file_name = OUTPUT_RESULTS_FILE_NAME

    output_file_type = GPKG_FILE_NAME if keep_geometries else CSV_FILE_NAME

    if not keep_geometries and GEOMETRY_KEY in final_output_df.columns:
        final_output_df.drop(columns=[GEOMETRY_KEY], inplace=True)

    time_now = pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")

    # set output dir path based on environment
    output_dir_path = (
        TEST_OUTPUT_RESULTS_DIR_PATH
        if os.getenv("ENV") == "TEST"
        else OUTPUT_FINAL_RESULTS_DIR_PATH
    )

    results_output_path = os.path.join(
        output_dir_path,
        f"{time_now}_{output_file_name}.{output_file_type}",
    )

    # normalize path for windows
    results_output_path = os.path.normpath(results_output_path)

    target_project_crs = output_file_name = user_config.get_nested_attribute(
        [PROJECT_KEY, PROJECT_CRS_KEY]
    )

    save_to_gpkg_or_csv(
        df=final_output_df, output_path=results_output_path, crs=target_project_crs
    )
