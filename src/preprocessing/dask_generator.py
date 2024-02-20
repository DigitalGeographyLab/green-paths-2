""" TODO """

import dask.dataframe as dd
import pandas as pd
import geopandas as gpd
from typing import Callable
from src.logging import setup_logger, LoggerColors
from src.timer import time_logger


LOG = setup_logger(__name__, LoggerColors.CYAN.value)


def update_metadata(gdf, new_columns):
    dummy = pd.DataFrame()
    for col in gdf.columns:
        dummy[col] = pd.Series([], dtype=gdf[col].dtype)
    for col, dtype in new_columns.items():
        dummy[col] = pd.Series([], dtype=dtype)
    return dummy


@time_logger
def dask_operation_runner(gdf, operation_func: Callable):
    """
    General generator for a Dask operation.

    :param gdf: Input GeoDataFrame.
    :param operation_func: Function to apply to each partition of the DataFrame.
    :return: Dask DataFrame after applying the operation.
    """
    LOG.info("starting dask operation generator")
    # Convert GeoDataFrame to Dask DataFrame
    dask_gdf = dd.from_pandas(gdf, npartitions=2)
    # dask_gdf = dask_gdf.repartition(partition_size="100MB")

    # TODO: remove buffer object?
    new_cols = {"buffer": "object"}
    metadata = update_metadata(gdf, new_cols)

    result = dask_gdf.map_partitions(operation_func, meta=metadata).compute()
    return result
