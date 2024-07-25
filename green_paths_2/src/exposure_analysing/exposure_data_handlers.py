""" Module for handling exposure data in the exposure analysing pipeline. Has also some general utilities """

# TODO: need to clean this file for all obsolete code!


import geopandas as gpd
import pandas as pd
from shapely import wkt

from ..config import (
    DEFAULT_BATCH_PROCENTAGE,
    GEOMETRY_KEY,
)

from ..logging import setup_logger, LoggerColors
from ..preprocessing.user_config_parser import UserConfig

LOG = setup_logger(__name__, LoggerColors.GREEN.value)


def save_to_gpkg_or_csv(df: pd.DataFrame, output_path: str) -> None:
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
        gdf.to_file(output_path, driver="GPKG")
        LOG.info(f"Final output saved to GeoPackage: {output_path}")
    else:
        df.to_csv(output_path, index=False)
        LOG.info(f"Final output saved to CSV: {output_path}")


def get_batch_limit(routing_results_count: int):
    """
    Calculate the batch limit for analysing pipeline.

    Parameters
    ----------
    routing_results_count : int
        The count of routing results.
    """

    # get the routing results count to enable batch processing
    LOG.info(f"the routing results count is {routing_results_count}. Splitting ")
    # Calculate batch limit
    limit = max(1, int(routing_results_count * DEFAULT_BATCH_PROCENTAGE))
    return limit
