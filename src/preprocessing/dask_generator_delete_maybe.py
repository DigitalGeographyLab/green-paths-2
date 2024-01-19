""" roope todo """

import dask.dataframe as dd
import pandas as pd
import geopandas as gpd
from typing import Callable
from src.logging import setup_logger, LoggerColors
from src.timer import time_logger


LOG = setup_logger(__name__, LoggerColors.CYAN.value)


# # roope todo muokkaa tätä!
# ehkä pois class -> tilalle module?
# # ja lisää kaikki parametrein...

# # Function to process each road segment
# def process_road_segment(segment, point_data):
#     # Example processing, e.g., creating buffer and performing spatial join
#     buffer = segment.geometry.buffer(your_buffer_size)
#     points_in_buffer = point_data[point_data.intersects(buffer)]
#     return calculate_mean_value(points_in_buffer)  # Your custom calculation

# # Load road data using osmnx or geopandas (gdf)
# # ...
# # Convert GeoDataFrame to Dask DataFrame
# ddf = dd.from_pandas(gdf, npartitions=4)  # Adjust npartitions based on your data size

# # Apply the function to each partition of the Dask DataFrame
# result = ddf.map_partitions(process_road_segment, point_data="your_point_data", meta=float)

# # Compute the result
# result_computed = result.compute()

# Assuming you have some function for spatial operations
# def spatial_operation(gdf):
#     # Perform spatial operations like buffering, overlay analysis, etc.
#     # Return modified GeoDataFrame
#     return modified_gdf


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
    dask_gdf = dd.from_pandas(
        gdf, npartitions=2
    )  # Adjust npartitions based on your system
    # dask_gdf = dask_gdf.repartition(partition_size="100MB")
    # Apply the operation function to each partition

    # roope todo -> testi, poista ehkä?:

    new_cols = {"buffer": "object"}
    metadata = update_metadata(gdf, new_cols)

    result = dask_gdf.map_partitions(operation_func, meta=metadata).compute()
    return result


# @time_logger
# def dask_operation_runner(dask_gdf) -> gpd.GeoDataFrame:
#     LOG.info("starting dask operation runner")
#     result_computed = dask_gdf.compute()
#     LOG.info("finished dask operation runner")
#     return result_computed
